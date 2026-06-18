# Common Hive Errors (in ETL/Airflow Pipelines)

## HiveException: Unable to fetch table

Usually means the referenced table doesn't exist in the specified database/schema, or the metastore connection is misconfigured. Fix: verify the table name, database, and that the Hive metastore service is reachable.

## Semantic Analysis Error: Partition Not Found

Occurs when a query references a partition that hasn't been created or registered yet (common in ETL pipelines where a downstream job runs before the upstream partition write/registration completes). Fix: ensure proper task ordering/sensors in Airflow, and consider running `MSCK REPAIR TABLE` or explicit partition registration if partitions exist on storage but aren't recognized by Hive's metastore.

## Too Many Dynamic Partitions

Raised when a query tries to create more dynamic partitions than Hive's configured limit (`hive.exec.max.dynamic.partitions`). Fix: increase the limit if appropriate, or reduce the cardinality of the partitioning column, or add a stricter WHERE clause to limit the partitions touched.

## OutOfMemoryError in Hive on MapReduce/Tez

Similar root causes to Spark OOM errors — large joins, data skew, or insufficient container memory. Fixes include increasing `mapreduce.map.memory.mb` / `mapreduce.reduce.memory.mb` (or Tez container size), or optimizing the query (e.g., using map-side joins for small tables).

## ORA- Errors (Oracle, in mixed ETL pipelines)

When an Airflow pipeline integrates with an Oracle database (often via a JDBC hook or operator), ORA- prefixed errors originate from Oracle itself. Common examples: ORA-00001 (unique constraint violated), ORA-12154 (TNS could not resolve connect identifier), ORA-01017 (invalid username/password). Fix depends on the specific ORA code; always look up the exact code for the precise cause.
