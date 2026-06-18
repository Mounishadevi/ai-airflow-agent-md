# Airflow Executors

The Executor determines how and where Airflow task instances actually get run.

## Common Executor Types

- **SequentialExecutor**: Runs one task at a time, sequentially. Used mainly for testing with SQLite; not suitable for production.
- **LocalExecutor**: Runs tasks as parallel processes on the same machine as the scheduler. Good for small to medium single-machine deployments.
- **CeleryExecutor**: Distributes tasks across a pool of worker machines using the Celery distributed task queue, backed by a message broker like Redis or RabbitMQ. Common for production deployments needing horizontal scaling.
- **KubernetesExecutor**: Launches a new Kubernetes pod for each task instance, providing strong isolation and dynamic resource allocation. Well suited for cloud-native, containerized environments.
- **CeleryKubernetesExecutor**: A hybrid that lets some tasks run via Celery workers and others via dedicated Kubernetes pods, based on task configuration.

## Choosing an Executor

- Single-machine or low-throughput setups: LocalExecutor.
- High-throughput, multi-worker production environments: CeleryExecutor or KubernetesExecutor.
- Workloads needing strict per-task isolation/resource limits: KubernetesExecutor.

## Related Failure Modes

Executor misconfiguration is a common source of "task stuck in queued" or "executor reports task instance finished (failed) although the task says its queued" errors. These often relate to worker connectivity issues, mismatched Airflow versions between scheduler and workers, or insufficient worker capacity.
