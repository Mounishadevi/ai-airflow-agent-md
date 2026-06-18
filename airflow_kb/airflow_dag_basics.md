# Airflow DAGs

A DAG (Directed Acyclic Graph) is the core concept in Apache Airflow. It represents a collection of tasks you want to run, organized in a way that reflects their relationships and dependencies, with a defined direction and no cycles.

## Key Properties

- **dag_id**: A unique identifier for the DAG.
- **schedule_interval / schedule**: Defines how often the DAG runs (e.g., a cron expression like "0 9 * * *", or presets like "@daily", "@hourly").
- **start_date**: The date from which Airflow starts considering the DAG for scheduling.
- **catchup**: If True, Airflow will run all missed DAG runs between start_date and now when the DAG is first enabled. Defaults to True, and is often set to False to avoid unwanted historical backfills.
- **default_args**: A dictionary of default parameters (like retries, retry_delay, owner, email_on_failure) applied to all tasks in the DAG unless overridden.

## Defining a DAG

DAGs are typically defined in Python files placed in the Airflow `dags/` folder. Airflow's scheduler periodically scans this folder, parses each file, and registers any DAG objects it finds.

## Best Practices

- Keep DAG files lightweight; avoid expensive computation or database calls at the top level of the file, since the scheduler re-parses DAG files frequently.
- Use `with DAG(...) as dag:` context manager syntax for cleaner task definitions.
- Make tasks idempotent — re-running a task should produce the same result without unwanted side effects, since Airflow may retry or rerun tasks.
- Avoid tightly coupling tasks to wall-clock time; use Airflow's execution_date / logical_date context instead of `datetime.now()`.
