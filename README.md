# Multi-Agent Airflow AI Assistant

## 🔥 What it does
This AI agent helps data engineers by:

- Answering Airflow questions using RAG (ChromaDB)
- Generating Airflow DAGs using LLM
- Debugging failed pipelines using logs
- Executing SQL validation queries
- Routing requests using an intelligent agent system

## 🧠 Architecture
User → Router Agent → {RAG / DAG Generator / Debug Agent} → Response

## ⚙️ Tech Stack
Python, Gemini API, ChromaDB, Streamlit, Airflow

## 🚀 Features
- Multi-agent routing system
- DAG code generator
- Retrieval-Augmented Generation (RAG)
- Debug assistant for pipeline failures

## ▶️ Run
pip install -r requirements.txt
streamlit run app/streamlit_app.py