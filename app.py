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

MODEL_NAME = "models/gemini-2.5-flash-lite"

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

Requirements:
- Use default_args
- Include retries
- Include logging
- Include email alerts
- Follow Airflow best practices
- Add useful comments
- Return ONLY Python code
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=4000,
            thinking_config=types.ThinkingConfig(thinking_budget=256)
        )
    )

    return safe_text(response, fallback="Sorry, I couldn't generate the DAG. Please try rephrasing your requirement.")

# ==========================
# TOOL 2 - ERROR ANALYZER
# ==========================

def explain_error(error_text):

    prompt = f"""
You are an Airflow, Hive, Spark and ETL troubleshooting expert.

Analyze:

{error_text}

Rules:
- For common errors, provide Cause and Fix only.
- For complex errors, provide:
  1. Root Cause
  2. Impact
  3. Fix
  4. Prevention
- Be practical and concise.
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
You are a senior Apache Airflow and ETL expert.

Use the context when relevant.

Context:
{context}

Question:
{question}

Rules:
- Answer according to the complexity of the question.
- Simple questions: answer in 2-4 sentences.
- Conceptual questions: provide a medium-length explanation.
- How-to questions: provide step-by-step guidance.
- Comparison questions: use bullets or a table.
- Generate code only if explicitly requested.
- Do not mention the context source.
- Be concise but complete.
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

    q = query.lower()

    dag_generation_keywords = [
        "generate dag",
        "create dag",
        "write dag",
        "build dag",
        "dag code",
        "airflow code",
        "create airflow dag",
        "generate airflow dag"
    ]

    error_keywords = [
        "error",
        "exception",
        "traceback",
        "failed",
        "failure",
        "ora-",
        "sparkexception",
        "hiveexception",
        "task failed"
    ]

    if any(k in q for k in dag_generation_keywords):
        return "GENERATE_DAG"

    if any(k in q for k in error_keywords):
        return "EXPLAIN_ERROR"

    return "QA"

def agent(query):

    intent = classify_intent(query)

    if intent == "GENERATE_DAG":
        return generate_dag(query)

    elif intent == "EXPLAIN_ERROR":
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
