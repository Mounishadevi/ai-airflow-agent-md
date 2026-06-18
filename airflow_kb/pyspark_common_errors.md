# Common PySpark Errors (in ETL/Airflow Pipelines)

## Py4JJavaError

A generic wrapper PySpark raises when the underlying JVM throws an exception, since PySpark communicates with the Spark JVM via the Py4J bridge. The real cause is usually deeper in the full stack trace (often one of the errors below). Always scroll to the actual nested exception rather than reading only the top line.

## AnalysisException: Column/Table Not Found

A schema mismatch — the referenced column or table doesn't exist, was renamed, or the DataFrame schema changed earlier in the pipeline. Fix: check with `df.printSchema()` and verify upstream transformations, especially after joins or `select()` calls that rename columns.

## OutOfMemoryError / Executor Lost

Caused by executors running out of memory, often from large shuffles, data skew, or collecting too much data to the driver (e.g., calling `.collect()` or `.toPandas()` on a very large DataFrame). Fixes: increase `spark.executor.memory`, repartition skewed data, or avoid pulling full datasets into driver memory — use `.show()`, `.limit()`, or sampling instead during debugging.

## Task Not Serializable (Pickling Errors)

PySpark serializes Python closures (lambdas, UDFs) to send to executors. This error occurs when a closure references a non-picklable object (like an open file handle, database connection, or unpicklable client object). Fix: initialize such objects inside the function passed to `mapPartitions`/UDFs rather than capturing them from the outer scope, or use broadcast variables for shared read-only data.

## Python Worker Crashed / PythonException

PySpark spawns separate Python worker processes to execute UDFs and Python-based transformations. A worker can crash due to unsupported library versions, memory limits, or uncaught exceptions inside a UDF. The error often shows as "Python worker exited unexpectedly" or a wrapped `PythonException` with the original Python traceback nested inside.

## "Python in worker has different version than that in driver"

A common cluster misconfiguration where the driver and executor nodes have different Python versions installed. Fix: set the `PYSPARK_PYTHON` (and `PYSPARK_DRIVER_PYTHON`) environment variables consistently across all nodes, or use a packaged/conda environment shipped with the job.

## Slow or Failing UDFs

Plain Python UDFs incur serialization overhead moving data between the JVM and the Python process for every row, making them much slower than native Spark SQL functions. For better performance, prefer built-in `pyspark.sql.functions`, or use vectorized `pandas_udf` (Arrow-based) when a custom function is unavoidable. Errors like "TypeError: Invalid argument" inside a UDF often mean the UDF's actual return value doesn't match its declared `returnType`.

## Data Skew

When one partition holds disproportionately more data than others, causing a single task to run far longer than its peers, or repeated OOM on specific executors. Fixes include salting skewed join keys, repartitioning, or enabling Adaptive Query Execution (`spark.sql.adaptive.enabled=true`), which can automatically optimize skewed joins in recent Spark versions.
