# Airflow Scheduling

Airflow's scheduler is responsible for monitoring DAGs and triggering task instances whose dependencies have been met.

## Key Concepts

- **schedule_interval / schedule**: Can be a cron expression, a timedelta, or a preset like "@daily", "@hourly", "@weekly", or None for manually-triggered DAGs.
- **execution_date / logical_date**: Represents the start of the data interval a DAG run is processing, not the actual wall-clock time the run executes. A DAG run that fires at midnight for a daily schedule typically has a logical_date of the previous day, since it represents data for that completed period.
- **data_interval_start / data_interval_end**: The newer, clearer way (Airflow 2.2+) to represent the time range a DAG run covers.
- **catchup**: When True, Airflow will create and run DAG runs for every missed interval between start_date and the current date when a DAG is first turned on. Set to False to only run from "now" forward.
- **max_active_runs**: Limits how many DAG run instances can execute concurrently for a given DAG.

## Backfilling

Backfilling is the process of running a DAG for past dates that haven't been processed yet, either automatically via catchup or manually via the `airflow dags backfill` command. Backfills can be resource-intensive if many historical runs are triggered at once.

## Common Scheduling Issues

- DAG not triggering: often caused by an incorrect start_date in the future, a paused DAG, or the scheduler not picking up a newly added DAG file due to file scan delay.
- Unexpected backfill runs: usually caused by catchup=True combined with a start_date far in the past.
