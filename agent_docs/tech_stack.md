# Tech Stack and Deployment

This agent is built with:

- Python as the primary language
- Streamlit for the web-based chat interface, deployed on Streamlit Cloud
- Google Gemini API (model: gemini-2.5-flash-lite) as the underlying language model for all three tools
- ChromaDB as a persistent local vector store for retrieval-augmented generation
- Sentence Transformers (all-MiniLM-L6-v2) for generating text embeddings used in similarity search

Chat history is stored in Streamlit's session state, so conversations persist within a single browser session but are not saved permanently across sessions or page reloads.
