import chromadb
from sentence_transformers import SentenceTransformer

# 1. Load embedding model (SAME as app.py)
model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Create / open ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("airflow")

# 3. Sample knowledge (you can expand later)
docs = [
    "Airflow DAG defines workflow of tasks.",
    "XCom is used to pass data between tasks.",
    "LocalExecutor runs tasks on the same machine.",
    "CeleryExecutor is used for distributed execution.",
    "ORA-00942 means table or view does not exist or no permission.",
    "Retries allow failed tasks to rerun automatically.",
    "Hive is a data warehouse system on Hadoop.",
    "Sqoop transfers data between Oracle and Hive."
]

# 4. Convert to embeddings
embeddings = model.encode(docs).tolist()

ids = [f"doc_{i}" for i in range(len(docs))]

# 5. Store in ChromaDB
collection.add(
    documents=docs,
    embeddings=embeddings,
    ids=ids
)

print("✅ Ingestion complete!")
print("Total documents:", collection.count())
