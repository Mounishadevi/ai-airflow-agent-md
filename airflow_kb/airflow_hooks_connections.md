# Airflow Hooks and Connections

## Connections

A Connection in Airflow stores the information needed to connect to an external system: host, port, login, password, schema, and extra parameters (often as JSON). Connections are managed via the Airflow UI (Admin > Connections), the CLI, environment variables, or a secrets backend (like AWS Secrets Manager or HashiCorp Vault).

Each connection has a `conn_id` that tasks and hooks reference to retrieve the connection's details at runtime, rather than hardcoding credentials in DAG code.

## Hooks

A Hook is a reusable interface for interacting with an external platform or database, built on top of a Connection. Hooks abstract away the low-level details of authenticating and communicating with a system.

Examples:
- **PostgresHook**, **MySqlHook**: Database hooks for running queries.
- **S3Hook**: Interacts with AWS S3 (uploading, downloading, listing objects).
- **HiveServer2Hook**, **HiveCliHook**: Interact with Hive for running queries or submitting jobs.

Operators often use Hooks internally; for example, a SQL-based operator typically calls a database Hook to execute its query rather than reimplementing connection logic.

## Best Practices

- Never hardcode credentials directly in DAG files; always reference a `conn_id`.
- Use a secrets backend for production environments instead of storing plaintext passwords in the Airflow metadata database.
- Test connections via the Airflow UI's "Test Connection" feature where supported, to catch misconfigurations before a DAG run fails.
