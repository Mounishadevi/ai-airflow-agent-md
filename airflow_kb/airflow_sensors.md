# Airflow Sensors

Sensors are a special type of Operator that wait (poll) for a certain condition to become true before allowing downstream tasks to run. They are commonly used to wait for files, database rows, partitions, or external events.

## Common Sensors

- **FileSensor**: Waits for a file to appear at a given filesystem path.
- **ExternalTaskSensor**: Waits for a task in another DAG to reach a certain state.
- **S3KeySensor**: Waits for a specific key (object) to appear in an S3 bucket.
- **SqlSensor**: Waits until a SQL query returns a truthy result.
- **TimeDeltaSensor / TimeSensor**: Waits until a certain amount of time has passed or a certain time of day is reached.

## Poke vs Reschedule Mode

- **poke mode** (default): The sensor's worker slot is occupied continuously while it repeatedly checks the condition, which can waste resources for long waits.
- **reschedule mode**: The sensor releases its worker slot between checks and reschedules itself, which is more resource-efficient for long-running waits.

## Deferrable Sensors

Newer "deferrable" (or "smart") sensors release their worker slot entirely while waiting, using a separate triggerer process to check the condition asynchronously. This significantly reduces resource usage for DAGs with many long-running sensors.

## Common Pitfall

Sensors left in poke mode with long timeouts can exhaust the worker pool, causing other tasks across the Airflow instance to queue up and stall. Switching to reschedule mode or deferrable sensors is a common fix for this kind of resource starvation.
