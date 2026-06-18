# Error Analyzer Tool

The Error Analyzer tool diagnoses Airflow, Spark, Hive, and general ETL errors.

## Trigger keywords

Questions containing words like "error", "exception", "traceback", "failed", "failure", "ora-", "sparkexception", "hiveexception", or "task failed" are routed to this tool.

## How it works

1. The error text submitted by the user is inserted into a prompt instructing Gemini to act as an Airflow, Hive, Spark, and ETL troubleshooting expert.
2. For common errors, Gemini is asked to return only the cause and the fix.
3. For more complex errors, Gemini is asked to return a structured breakdown: root cause, impact, fix, and prevention.
4. The model is run with no "thinking" budget, prioritizing fast, direct responses over slower deliberation, with a 600 token output limit.
