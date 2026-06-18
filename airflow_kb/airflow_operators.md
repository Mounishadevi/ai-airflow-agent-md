# Airflow Operators

An Operator defines a single, atomic unit of work in an Airflow DAG. Each task in a DAG is created by instantiating an Operator.

## Common Built-in Operators

- **PythonOperator**: Executes a Python callable.
- **BashOperator**: Executes a bash command or script.
- **EmailOperator**: Sends an email.
- **DummyOperator / EmptyOperator**: A no-op task, often used to group dependencies or mark milestones in a DAG.
- **BranchPythonOperator**: Executes a Python callable that returns the task_id(s) to follow next, enabling conditional branching in a DAG.

## Provider Operators

Airflow's provider packages add operators for specific systems, such as:

- **SparkSubmitOperator**: Submits a Spark job to a cluster.
- **HiveOperator**: Executes HiveQL in a specified Hive environment.
- **S3ToRedshiftOperator**, **BigQueryInsertJobOperator**, and many others for cloud and database integrations.

## Sensors vs Operators

Sensors are a special subclass of Operator that wait for a certain condition to be true (like a file appearing or a partition being available) before allowing downstream tasks to proceed.

## Idempotency

A key design principle: operators should be written so that re-running the same task with the same inputs produces the same outcome, since Airflow may retry tasks automatically after failures.
