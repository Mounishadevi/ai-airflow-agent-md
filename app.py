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
# CHROMADB - EphemeralClient (works perfectly on Streamlit Cloud)
# ==========================

@st.cache_resource
def load_collection():
    chroma_client = chromadb.EphemeralClient()
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
# ==========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

KB_FOLDERS = [
    os.path.join(BASE_DIR, "agent_docs"),
    os.path.join(BASE_DIR, "airflow_kb")
]

def ingest_knowledge_base():

    added = 0
    errors = []

    for folder in KB_FOLDERS:

        if not os.path.isdir(folder):
            errors.append(f"Folder '{folder}' not found — skipped.")
            continue

        for filename in sorted(os.listdir(folder)):

            if not filename.endswith(".md"):
                continue

            path = os.path.join(folder, filename)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()

                if not text.strip():
                    errors.append(f"'{filename}' is empty — skipped.")
                    continue

                doc_id = f"{os.path.basename(folder)}::{filename}"
                embedding = embedding_model.encode(text).tolist()

                collection.upsert(
                    ids=[doc_id],
                    documents=[text],
                    embeddings=[embedding],
                )
                added += 1

            except Exception as e:
                errors.append(f"Failed to ingest '{filename}': {e}")

    return added, errors

# ==========================
# RUN INGEST ON STARTUP
# ==========================

try:
    existing_count = collection.count()
except Exception as e:
    existing_count = 0

if existing_count == 0:

    with st.spinner("Building knowledge base..."):

        try:
            added, ingestion_errors = ingest_knowledge_base()

            if added > 0:
                st.success(f"✅ Knowledge base initialized: {added} document(s) loaded.")
            else:
                st.warning("⚠️ No documents were ingested.")

            if ingestion_errors:
                with st.expander(f"⚠️ {len(ingestion_errors)} issue(s) during ingestion"):
                    for err in ingestion_errors:
                        st.write(f"- {err}")

        except Exception as e:
            st.error(f"❌ Ingestion failed: {e}")

# ==========================
# SAFE TEXT EXTRACTOR
# ==========================

def safe_text(response, fallback="Sorry, I couldn't generate a response. Please rephrase."):
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
            thinking_config=types.ThinkingConfig(thinking_budget=512)
        )
    )

    return safe_text(response, fallback="Sorry, I couldn't generate the DAG. Please try rephrasing.")

# ==========================
# TOOL 2 - ERROR ANALYZER
# ==========================

def explain_error(error_text):

    prompt = f"""
You are an Airflow, Hive, Spark and ETL troubleshooting expert.

Analyze:
{error_text}

Rules:
- For common errors: Cause and Fix only.
- For complex errors:
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

    return safe_text(response, fallback="Sorry, I couldn't analyze that error. Please try again.")

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
        context = ""

    prompt = f"""
You are a senior Apache Airflow and ETL expert.

Use the context when relevant.

Context:
{context}

Question:
{question}

Rules:
- Simple questions: 2-4 sentences.
- Conceptual questions: medium explanation.
- How-to questions: step-by-step.
- Comparison questions: bullets or table.
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

    return safe_text(response, fallback="Sorry, I couldn't find a good answer. Please rephrase.")

# ==========================
# AGENT ROUTER
# ==========================

def classify_intent(query):

    q = query.lower()

    dag_keywords = [
        "generate dag", "create dag", "write dag",
        "build dag", "dag code", "airflow code",
        "create airflow dag", "generate airflow dag"
    ]

    error_keywords = [
        "error", "exception", "traceback", "failed",
        "failure", "ora-", "sparkexception",
        "hiveexception", "task failed"
    ]

    if any(k in q for k in dag_keywords):
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
# UI
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

try:
    doc_count = collection.count()
    st.markdown(f"""
### 📊 Knowledge Base Stats
- 📄 **Documents Loaded:** {doc_count}
- 📁 **Sources:** agent_docs + airflow_kb
""")
except:
    pass

st.markdown("---")

# ==========================
# INPUT
# ==========================

question = st.text_area(
    "Ask your question",
    height=120,
    placeholder="Ask anything about Airflow, DAGs, or ETL errors"
)

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
