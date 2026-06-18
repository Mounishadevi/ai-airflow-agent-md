# Intent Routing Logic

The agent uses a lightweight, keyword-based intent classifier rather than a machine-learning classifier to decide which tool should handle an incoming question.

The classifier checks the lowercased question text against two keyword lists:

- DAG generation keywords: trigger the DAG Generator tool.
- Error-related keywords: trigger the Error Analyzer tool.

If neither list matches, the question defaults to the RAG Search tool, which treats it as a general knowledge question and searches the ChromaDB collection for relevant context.

## Limitation

This approach is fast and predictable, but it means questions that don't contain expected keywords — for example, meta-questions about the agent's own architecture, or questions about unrelated topics — are routed to RAG Search by default. If no ingested document covers the topic, the answer falls back to the language model's general knowledge rather than grounded, agent-specific information.
