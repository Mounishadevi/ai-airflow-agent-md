# DAG Generator Tool

The DAG Generator tool creates production-ready Apache Airflow DAGs from natural language requirements.

## Trigger keywords

Questions containing phrases like "generate dag", "create dag", "write dag", "build dag", "dag code", "airflow code", "create airflow dag", or "generate airflow dag" are routed to this tool.

## How it works

1. The user's requirement is inserted into a prompt instructing Gemini to act as a senior Apache Airflow engineer.
2. Gemini 2.5 Flash-Lite is asked to generate a DAG that includes default_args, retries, logging, and email alerts, follows Airflow best practices, and includes helpful comments.
3. The model is configured with a larger output token budget (4000 tokens) and a small thinking budget (256 tokens) to balance code quality with response speed.
4. The tool returns only the generated Python code for the DAG, with no extra explanation.
