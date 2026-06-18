# Airflow Pools and Priority Weights

## Pools

Pools let you limit the number of concurrent task instances that can run against a shared, limited resource (like a database connection limit or an external API rate limit). Each task can be assigned to a pool with a fixed number of "slots"; only that many tasks across all DAGs can run in that pool simultaneously.

Example use case: limiting all tasks that query a particular external API to 5 concurrent slots, even if many DAGs across the Airflow instance want to call that API at once.

## Priority Weights

When multiple tasks are queued and competing for limited pool slots or worker capacity, Airflow uses `priority_weight` to decide which queued tasks should be scheduled first. Higher priority_weight values are scheduled before lower ones, all else being equal.

`weight_rule` can be set to control how priority propagates through a DAG (e.g., `downstream`, `upstream`, or `absolute`), affecting whether a task's priority is influenced by its position in the dependency graph.

## Common Pitfall

If too many tasks are assigned to a small pool, tasks can queue indefinitely waiting for a free slot, which looks like a "stuck" DAG even though nothing has actually failed — the fix is usually to increase pool size or rebalance which tasks share a pool.
