# AI-Powered Airflow Operations Agent — Architecture

This application is a Streamlit-based conversational agent that helps engineers interact with Apache Airflow workflows using natural language. It combines Retrieval-Augmented Generation (RAG), automated DAG generation, and ETL/Airflow error analysis in a single chat interface.

## High-Level Flow

1. The user submits a question through the Streamlit UI.
2. An intent classifier (classify_intent) inspects the question for keywords related to DAG generation or error/exception handling.
3. Based on the detected intent, the query is routed to one of three tools:
   - RAG Search — for general Airflow Q&A
   - DAG Generator — for requests to create or build an Airflow DAG
   - Error Analyzer — for troubleshooting errors, exceptions, or failures
4. Each tool builds a tailored prompt and calls the Gemini 2.5 Flash-Lite model via the Google Gemini API to generate a response.
5. The response is displayed in the chat interface and stored in Streamlit's session state as conversation history.

## Components

- Streamlit UI: Handles user input, displays responses, and maintains chat history using st.session_state.
- Agent Router (classify_intent / agent): A keyword-based intent classifier that decides which tool should handle a given query.
- RAG Search (rag_search): Embeds the user's question with a Sentence Transformer model, retrieves the top matching documents from a ChromaDB vector store, and passes the retrieved context to Gemini to generate a grounded answer.
- DAG Generator (generate_dag): Takes a plain-language requirement and asks Gemini to produce a production-ready Airflow DAG with default_args, retries, logging, and email alerts.
- Error Analyzer (explain_error): Takes error text (Airflow, Spark, Hive, or general ETL errors) and asks Gemini to return a cause-and-fix summary, or a deeper root-cause/impact/fix/prevention breakdown for complex issues.
- Gemini 2.5 Flash-Lite: The underlying language model used by all three tools to generate natural-language and code responses.

## Reliability Safeguard

Gemini 2.5's internal "thinking" process can occasionally consume its entire token budget before producing visible output, returning an empty response. A safe_text() helper checks for this case and returns a friendly fallback message instead of a blank answer, so the agent never leaves the user without a response.

