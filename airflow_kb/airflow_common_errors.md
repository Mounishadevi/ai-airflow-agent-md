# Common Airflow Errors

## DAG Import Errors

Caused by Python syntax errors, missing imports, or exceptions raised at the top level of a DAG file. Shown as a red "Broken DAG" banner in the Airflow UI. Fix: check the Airflow webserver/scheduler logs or the UI's import error list for the exact traceback.

## Task Stuck in "Queued" State

Often caused by: insufficient worker capacity, executor/worker connectivity issues, a full pool with no free slots, or a mismatch between the Airflow version on the scheduler vs. the workers. Fix: check worker logs, pool slot usage, and executor health.

## Zombie Tasks

A "zombie" task is one whose process died unexpectedly (e.g., the worker crashed or was OOM-killed) without properly reporting failure back to Airflow. The scheduler periodically detects zombies and marks them as failed. Frequent zombies often point to worker resource exhaustion (memory/CPU limits too low).

## Scheduler Not Picking Up New DAGs

Usually caused by: the DAG file not being in the configured dags_folder, a syntax error preventing parsing, or the scheduler's file-parsing interval not yet having reached the new file. Fix: verify file location, check for import errors, and consider triggering a manual DAG file refresh.

## Task Failed with Executor Reporting "Task Instance Finished (Failed)"

This generic message often masks an underlying issue: OOM kill, network timeout to an external system, or an unhandled exception in task code. Always check the actual task logs (not just the executor's summary status) for the real root cause.

## Jinja Templating Errors

Caused by malformed template strings (e.g., `{{ ds }}`) in operator parameters, or referencing a variable/macro that doesn't exist in the templating context. Fix: validate template syntax and confirm the macro/variable is available for that operator.
