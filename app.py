import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
import os

from google import genai
from google.genai import types

# ==========================
# CONFIG
# ==========================

st.set_page_config(
    page_title="AI Airflow Operations Agent",
    page_icon="🚀",
    layout="wide"
)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL_NAME = "models/gemini-2.5-flash"

# ==========================
# CHAT HISTORY
# ==========================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==========================
# CHROMADB
# ==========================

@st.cache_resource
def load_collection():

    db_path = os.path.abspath("./chroma_db")

    chroma_client = chromadb.PersistentClient(path=db_path)

    collection = chroma_client.get_or_create_collection(
        name="airflow_docs"
    )

    return collection

collection = load_collection()

# ==========================
# EMBEDDING MODEL
# ==========================

@st.cache_resource
def load_embedding_model():

    return SentenceTransformer("all-MiniLM-L6-v2")

embedding_model = load_embedding_model()

# ==========================
# SAFE TEXT EXTRACTOR
# (Gemini 2.5 Flash can return None text if it spends its whole
# token budget on internal "thinking" before producing output)
# ==========================

def safe_text(response, fallback="Sorry, I couldn't generate a response for that. Could you rephrase the question?"):
    try:
        if response and response.text:
            return response.text
    except Exception:
        pass
    return fallback

# ==========================
# TOOL 1 - DAG GENERATOR
# ==========================

def generate_dag(requirement):

    prompt = f"""
You are a senior Apache Airflow engineer.

Generate a production-ready Airflow DAG.

Requirement:
{requirement}

Rules:
- retries
- schedule
- email alerts
- best practices
- return ONLY Python code
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=4000,
            thinking_config=types.ThinkingConfig(thinking_budget=512)
        )
    )

    return safe_text(response, fallback="Sorry, I couldn't generate the DAG. Please try rephrasing your requirement.")

# ==========================
# TOOL 2 - ERROR ANALYZER
# ==========================

def explain_error(error_text):

    prompt = f"""
You are an Airflow + ETL expert.

Analyze this error:

{error_text}

Rules:
- If this is a simple, well-known error, answer in 2-4 short sentences covering cause and fix. Do not use headings for simple errors.
- Only use the structured format below if the error is genuinely complex or ambiguous:
  1. Root Cause
  2. Impact
  3. Fix
  4. Prevention
- Be direct. No restating the error back, no filler intro sentences.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=600,
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
    )

    return safe_text(response, fallback="Sorry, I couldn't analyze that error. Please try pasting it again.")

# ==========================
# TOOL 3 - RAG SEARCH
# ==========================

def rag_search(question):

    query_embedding = embedding_model.encode(question).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    context = "\n\n".join(results["documents"][0])

    prompt = f"""
You are an Apache Airflow expert.

Use this context:

{context}

Question:
{question}

Rules:
- Answer in 2-4 sentences unless the question explicitly asks for steps, a list, or a detailed explanation.
- No preamble such as "Based on the context provided...". Answer directly.
- Only go longer if the question genuinely requires it.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=500,
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
    )

    return safe_text(response, fallback="Sorry, I couldn't find a good answer to that. Could you rephrase the question?")

# ==========================
# AGENT ROUTER (intent classification, not keyword matching)
# ==========================

def classify_intent(query):

    prompt = f"""Classify the user query into exactly one category. Respond with ONLY the category name, nothing else.

Categories:
- GENERATE_DAG: user explicitly wants you to create, write, or build a new Airflow DAG or pipeline code.
- EXPLAIN_ERROR: user is pasting or describing an error, exception, traceback, or failure and wants it diagnosed.
- QA: user is asking a conceptual, informational, or how-it-works question (including questions that merely mention "DAG", "pipeline", or "workflow" without asking you to generate one).

Query:
{query}

Category:"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=50,
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
    )

    text = safe_text(response, fallback="QA")
    return text.strip().upper()

def agent(query):

    intent = classify_intent(query)

    if "GENERATE_DAG" in intent:
        return generate_dag(query)

    elif "EXPLAIN_ERROR" in intent:
        return explain_error(query)

    else:
        return rag_search(query)

# ==========================
# UI HEADER
# ==========================

st.title("🚀 AI-Powered Airflow Operations Agent")

st.markdown("---")

st.markdown("""
### 🤖 Capabilities

- 📚 Airflow Q&A (RAG)
- ⚙️ DAG Generation
- 🚨 ETL / Airflow Error Analysis
""")

st.markdown("---")

# ==========================
# INPUT
# ==========================

question = st.text_area(
    "Ask your question",
    height=120,
    placeholder="Ask anything about Airflow, DAGs, or ETL errors"
)

# ==========================
# SUBMIT
# ==========================

if st.button("Submit"):

    if not question.strip():
        st.warning("Please enter a question.")
        st.stop()

    try:

        with st.spinner("Agent Thinking..."):

            answer = agent(question)

        st.session_state.chat_history.append({
            "question": question,
            "answer": answer
        })

    except Exception as e:
        st.error(f"Error: {e}")

# ==========================
# CHAT HISTORY
# ==========================

st.markdown("## 💬 Conversation History")

for chat in reversed(st.session_state.chat_history):

    st.markdown("### 🧑 You")
    st.write(chat["question"])

    st.markdown("### 🤖 Agent")
    st.write(chat["answer"])

    st.markdown("---")
