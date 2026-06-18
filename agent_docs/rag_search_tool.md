# RAG Search Tool

The RAG Search tool answers general Airflow questions using Retrieval-Augmented Generation. It is the default tool used whenever a question does not match DAG-generation or error-related keywords.

## How it works

1. The user's question is converted into a vector embedding using the all-MiniLM-L6-v2 Sentence Transformer model.
2. The embedding is used to query a persistent ChromaDB collection named "airflow", retrieving the 3 most similar documents.
3. The retrieved documents are combined into a single context block.
4. The context and the original question are sent to Gemini 2.5 Flash-Lite with instructions to answer according to the complexity of the question:
   - Simple questions get a short 2-4 sentence answer.
   - Conceptual questions get a medium-length explanation.
   - How-to questions get step-by-step guidance.
   - Comparison questions get bullets or a table.
5. The tool returns Gemini's generated answer without revealing that the answer was grounded in retrieved context.

## Notes

The quality of RAG Search answers depends entirely on what has been added to the ChromaDB knowledge base. If a topic isn't covered by any ingested document, the retrieved context will be irrelevant, and Gemini will fall back on its own general knowledge rather than grounded, agent-specific information.
