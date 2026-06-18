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
        name="airflow"
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
# AUTO-INGEST KNOWLEDGE BASE
# (Runs once, automatically, if the ChromaDB collection is empty.
# This is what makes the agent self-sufficient on Streamlit Cloud —
# a fresh deploy has no pre-populated chroma_db folder, so without
# this step RAG Search would always retrieve nothing.)
# ==========================

KB_FOLDERS = ["agent_docs", "airflow_kb"]

def ingest_knowledge_base():
    """
    Walks each folder in KB_FOLDERS, embeds every .md file, and upserts
    it into the ChromaDB collection. Returns (added_count, error_list)
    so the caller can report exactly what happened.
    """

    added = 0
    errors = []

    for folder in KB_FOLDERS:

        if not os.path.isdir(folder):
            errors.append(f"Folder '{folder}' not found in the app directory — skipped.")
            continue

        for filename in sorted(os.listdir(folder)):

            if not filename.endswith(".md"):
                continue

            path = os.path.join(folder, filename)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()

                if not text.strip():
                    errors.append(f"'{folder}/{filename}' is empty — skipped.")
                    continue

                doc_id = f"{folder}::{filename}"
                embedding = embedding_model.encode(text).tolist()

                collection.upsert(
                    ids=[doc_id],
                    documents=[text],
                    embeddings=[embedding],
                )
                added += 1

            except Exception as e:
                errors.append(f"Failed to ingest '{folder}/{filename}': {e}")

    return added, errors


# Check current collection size safely — collection.count() can itself
# raise on some ChromaDB versions/states, so we don't let that crash the app.
try:
    existing_count = collection.count()
except Exception as e:
    existing_count = 0
    st.warning(f"Could not check existing knowledge base size, assuming empty. Details: {e}")

if existing_count == 0:

    with st.spinner("First run detected — building knowledge base..."):

        try:
            added, ingestion_errors = ingest_knowledge_base()

            if added > 0:
                st.success(f"✅ Knowledge base initialized: {added} document(s) loaded.")
            else:
                st.warning(
                    "⚠️ No documents were ingested. Make sure the 'agent_docs/' "
                    "and 'airflow_kb/' folders exist in the app directory and "
                    "contain .md files."
                )

            if ingestion_errors:
                with st.expander(f"⚠️ {len(ingestion_errors)} issue(s) during ingestion — click to view"):
                    for err in ingestion_errors:
                        st.write(f"- {err}")

        except Exception as e:
            # Last-resort catch: ingestion failing should never crash the
            # whole app — RAG Search will just retrieve nothing until fixed.
            st.error(f"❌ Knowledge base ingestion failed unexpectedly: {e}")

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

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        context = "\n\n".join(results["documents"][0]) if results["documents"] and results["documents"][0] else ""
    except Exception as e:
        # If the collection is empty or the query otherwise fails,
        # fall back to no context rather than crashing the whole request.
        context = ""
        st.warning(f"RAG retrieval issue (continuing without retrieved context): {e}")

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

# Show knowledge base stats
try:
    doc_count = collection.count()
    st.markdown(f"""
    ### 📊 Knowledge Base Stats
    - 📄 **Documents Loaded:** {doc_count}
    - 📁 **Sources:** agent_docs + airflow_kb
    """)
except:
    pass

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
