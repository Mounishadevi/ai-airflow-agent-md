import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
import os

from google import genai

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
        contents=prompt
    )

    return response.text

# ==========================
# TOOL 2 - ERROR ANALYZER
# ==========================

def explain_error(error_text):

    prompt = f"""
You are an Airflow + ETL expert.

Analyze this error:

{error_text}

Provide:
1. Root Cause
2. Impact
3. Fix
4. Prevention
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text

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
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text

# ==========================
# AGENT ROUTER
# ==========================

def agent(query):

    q = query.lower()

    if "dag" in q or "pipeline" in q or "workflow" in q:
        return generate_dag(query)

    elif (
        "error" in q or
        "failed" in q or
        "exception" in q or
        "ora-" in q
    ):
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
