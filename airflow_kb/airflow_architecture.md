# Airflow Architecture

Apache Airflow is made up of several core components that work together to schedule and execute workflows.

## Core Components

- **Webserver**: Serves the Airflow UI, where users can view DAGs, trigger runs, inspect logs, and manage connections/variables.
- **Scheduler**: Continuously parses DAG files, determines which tasks are ready to run based on dependencies and schedule, and sends them to the executor.
- **Executor**: Determines how and where task instances actually run (see Airflow Executors). The executor itself runs as part of the scheduler process for some executor types, or coordinates with external workers for others (e.g., CeleryExecutor, KubernetesExecutor).
- **Metadata Database**: A relational database (commonly PostgreSQL or MySQL) that stores DAG run state, task instance state, connections, variables, XComs, and other persistent Airflow data.
- **Workers**: For distributed executors like Celery or Kubernetes, workers are the processes/pods that actually execute task code.
- **Triggerer** (Airflow 2.2+): A dedicated process that handles deferrable (async) tasks and sensors, allowing them to wait on events without occupying a full worker slot.

## Typical Flow

1. The scheduler parses DAG files and updates the metadata database with new DAG runs and task instances as they become due.
2. The executor (or its workers) picks up queued task instances and executes them.
3. Task instances report their state (success, failed, running, etc.) back to the metadata database.
4. The webserver reads from the metadata database to display current and historical state in the UI.

## High Availability

Production Airflow deployments often run multiple scheduler replicas (supported since Airflow 2.0) and multiple workers for redundancy and throughput, all sharing the same metadata database.
