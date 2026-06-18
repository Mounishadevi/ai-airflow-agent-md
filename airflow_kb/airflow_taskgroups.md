# Airflow TaskGroups

TaskGroups provide a way to visually and logically group related tasks within a single DAG, making complex DAGs easier to read in the Airflow UI's graph view.

## Why Use TaskGroups

- They replace the older, more complex SubDAG feature, which had known performance and deadlock issues.
- Tasks inside a TaskGroup behave like normal tasks — they can have dependencies on tasks inside or outside the group.
- TaskGroups are purely a UI/organizational construct; they don't introduce separate scheduling or executor behavior the way SubDAGs did.

## Example Pattern

```python
from airflow.utils.task_group import TaskGroup

with TaskGroup("extract_tasks") as extract_group:
    extract_a = PythonOperator(task_id="extract_a", python_callable=extract_a_fn)
    extract_b = PythonOperator(task_id="extract_b", python_callable=extract_b_fn)

extract_group >> transform_task
```

## SubDAGs (Legacy)

SubDAGs allowed embedding one DAG inside another but ran on a separate executor context, which could cause deadlocks if the SubDAG's executor pool was exhausted by the parent DAG. TaskGroups are now the recommended replacement for almost all use cases that previously used SubDAGs.
