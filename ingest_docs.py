"""
Run this once to load BOTH the agent's self-knowledge docs AND the general
Airflow knowledge base docs into your existing ChromaDB "airflow" collection.

This gives your RAG Search tool two things it doesn't currently have:
  1. Real Airflow/Spark/Hive domain knowledge to answer Q&A questions
  2. Self-knowledge about the agent's own architecture and tools

Usage:
    1. Place this script in the same folder as your app.py (so it finds
       ./chroma_db the same way your app does).
    2. Put both folders next to this script:
         - agent_docs/   (self-knowledge docs)
         - airflow_kb/    (general Airflow/Spark/Hive knowledge docs)
    3. Run: python ingest_docs.py
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer

FOLDERS = ["agent_docs", "airflow_kb"]

def main():
    db_path = os.path.abspath("./chroma_db")
    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_or_create_collection(name="airflow")

    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    added = 0
    for folder in FOLDERS:
        if not os.path.isdir(folder):
            print(f"Folder '{folder}' not found, skipping.")
            continue

        for filename in sorted(os.listdir(folder)):
            if not filename.endswith(".md"):
                continue

            path = os.path.join(folder, filename)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            doc_id = f"{folder}::{filename}"
            embedding = embedding_model.encode(text).tolist()

            # upsert so re-running this script doesn't create duplicates
            collection.upsert(
                ids=[doc_id],
                documents=[text],
                embeddings=[embedding],
            )
            added += 1
            print(f"Ingested: {folder}/{filename}")

    count = collection.count()
    print(f"\nDone. {added} document(s) ingested this run.")
    print(f"Collection 'airflow' now has {count} total document(s).")

if __name__ == "__main__":
    main()
