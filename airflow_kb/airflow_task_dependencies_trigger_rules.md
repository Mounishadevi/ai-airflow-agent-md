# Airflow Task Dependencies and Trigger Rules

## Setting Dependencies

Task dependencies in Airflow are typically defined using the `>>` and `<<` bitshift operators, or the `set_upstream()` / `set_downstream()` methods.

Example pattern: `task_a >> task_b >> task_c` means task_b runs after task_a succeeds, and task_c runs after task_b succeeds.

## Trigger Rules

By default, a task only runs once all of its upstream (parent) tasks have succeeded (`all_success`). Trigger rules let you change this behavior:

- **all_success** (default): All upstream tasks must succeed.
- **all_failed**: All upstream tasks must have failed.
- **all_done**: All upstream tasks must have finished, regardless of success or failure — useful for cleanup tasks.
- **one_failed**: Triggers as soon as at least one upstream task fails, without waiting for the others.
- **one_success**: Triggers as soon as at least one upstream task succeeds.
- **none_failed**: All upstream tasks succeeded or were skipped, but none failed.

## Common Use Case

A common pattern is to add a final "notify on failure" or "cleanup" task with `trigger_rule="all_done"` so it always runs at the end of a DAG run, regardless of whether earlier tasks succeeded or failed.

## Common Pitfall

Forgetting to set an appropriate trigger_rule on downstream tasks after a BranchPythonOperator can cause unintended skips, since tasks on the unchosen branch are marked "skipped," and any task depending on both branches with the default all_success rule will also be skipped rather than run.
