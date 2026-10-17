# Chapter 34 · Database scaling

## The big idea

A database becomes slow or full in different ways, and each problem has a **different cure**. Scaling a
database is about **diagnosing the bottleneck first**, then applying the cheapest fix that works, and only
moving to the next step when the numbers demand it.

**Everyday example:** a clinic with a growing queue. First you stop wasting time (better paperwork:
**indexes**), then you put a receptionist who answers common questions without bothering the doctor
(**cache**), then you add more doctors who see patients with the same records (**read replicas**), then
you buy a bigger building (**vertical scaling**), and finally you open branch clinics for different
neighbourhoods (**sharding**).

```{raw} html
:file: ../diagrams/database-scaling.html
```

## First: find what is actually slow

| Symptom | Likely cause | First thing to try |
|---|---|---|
| A few queries take seconds | Missing index, bad query | `EXPLAIN`, add an index, rewrite |
| Everything is slow under read load | Too many reads on one node | Cache, then read replicas |
| Writes are slow or queue up | Primary is the bottleneck | Batch writes, reduce indexes, then shard |
| CPU high | Heavy queries/aggregations | Optimise, move reports to a replica |
| Disk full | Too much data | Archive/partition old data, then shard |
| Connections exhausted | Too many app connections | Connection pooling (PgBouncer) |
| Memory misses (disk reads) | Working set larger than RAM | More RAM, caching |

## The ladder, in the right order

### Step 1: Optimise queries and indexes (free)

Add indexes, remove `SELECT *`, fix N+1 queries, paginate with cursors. This alone often gives 10x to 1000x.

### Step 2: Connection pooling

A database handles a few hundred connections well, not thousands. Put a **pool** (PgBouncer, RDS Proxy) between
many app servers and the database.

### Step 3: Caching

Put **Redis** in front of hot reads (cache-aside). A 90% hit rate removes 90% of read load.

### Step 4: Vertical scaling (scale up)

A bigger machine: more CPU, RAM, faster NVMe. Quick, no code change. Limits: price curve and a ceiling.

### Step 5: Read replicas (scale reads)

Writes go to the primary; reads spread over replicas. Handle **replication lag** (read-your-writes).
Works when reads dominate (most applications are 90%+ reads).

### Step 6: Partitioning (split one table inside one server)

Split a huge table by range (e.g. one partition per month). Old partitions are cheap to **archive or drop**,
queries that name a date touch only a few partitions. This is **not** sharding: it is still one server.

### Step 7: Archiving and tiering

Move cold data (orders older than 2 years) to cheaper storage or a data warehouse. A smaller hot dataset
means faster everything.

### Step 8: Functional split (federation / vertical partitioning)

Separate databases by **feature**: users, orders, catalogue, each with its own server. Teams scale independently.
Cost: no joins across them.

### Step 9: Sharding (scale writes and storage)

Split rows across servers by a shard key. The most powerful and the most expensive step.

### Step 10: Change the engine

Move specific workloads to a better-fitting store: time-series DB, search engine, key-value store,
column store for analytics.

## A capacity calculation

```python
def plan(reads_per_s, writes_per_s, data_gb,
         node_reads=5_000, node_writes=1_000, node_storage_gb=500, cache_hit=0.0):
    effective_reads = reads_per_s * (1 - cache_hit)
    replicas_for_reads = max(1, -(-int(effective_reads) // node_reads))      # ceiling division
    shards_for_writes = max(1, -(-int(writes_per_s) // node_writes))
    shards_for_data = max(1, -(-int(data_gb) // node_storage_gb))
    shards = max(shards_for_writes, shards_for_data)
    return effective_reads, replicas_for_reads, shards

cases = {
    "small shop       ": dict(reads_per_s=800, writes_per_s=40, data_gb=20),
    "popular app      ": dict(reads_per_s=40_000, writes_per_s=800, data_gb=300),
    "popular + cache  ": dict(reads_per_s=40_000, writes_per_s=800, data_gb=300, cache_hit=0.9),
    "write-heavy feed ": dict(reads_per_s=10_000, writes_per_s=25_000, data_gb=4_000),
}
for name, kw in cases.items():
    reads, replicas, shards = plan(**kw)
    print(f"{name}: effective reads {reads:>7,.0f}/s -> {replicas} read node(s) per shard, {shards} shard(s)")
```

**Output:**

```text
small shop       : effective reads     800/s -> 1 read node(s) per shard, 1 shard(s)
popular app      : effective reads  40,000/s -> 8 read node(s) per shard, 1 shard(s)
popular + cache  : effective reads   4,000/s -> 1 read node(s) per shard, 1 shard(s)
write-heavy feed : effective reads  10,000/s -> 2 read node(s) per shard, 25 shard(s)
```

A "popular app" needs 8 read nodes without a cache but **2** with a 90% hit rate. Only the write-heavy
feed truly needs sharding (25 shards). The numbers tell you the step.

## Replicas vs sharding vs cache, in one table

| Technique | Fixes | Does not fix |
|---|---|---|
| Index | Slow queries | Pure volume |
| Cache | Read load, latency | Writes; cold start |
| Read replicas | Read load, availability | Write load, storage |
| Vertical scaling | Everything, temporarily | Ceiling, SPOF |
| Partitioning | Table size, archiving | Single-server limits |
| Sharding | Writes, storage | Cross-shard queries (gets worse) |

## What to say in an interview

"At 4,000 reads and 40 writes a second, one PostgreSQL primary with two replicas and a Redis cache is
plenty. I would shard only if sustained writes passed roughly 10,000 per second or data passed several TB,
and I would choose `user_id` as the shard key with consistent hashing."

## Common mistakes

:::{warning}
- Jumping to sharding because "it is a big system".
- Adding replicas when the real problem is a missing index.
- Forgetting replication lag after adding replicas.
- Scaling the database when the cache hit rate is just poor.
:::

## Try it yourself

1. Order the following by what you try first: shard the database, add an index, add read replicas, add a cache.
2. A table with 5 years of orders slows down. Queries mostly look at the last 30 days. What helps?
3. The primary is at 95% CPU from heavy nightly reports. Cheapest fix?

<details class="solution"><summary>Answers</summary>

1. Add an index, add a cache, add read replicas, shard (last).
2. **Partition by date** and **archive** old partitions; ensure an index on the date column.
3. Run the reports on a **read replica** (or a warehouse), not the primary.

</details>

:::{admonition} Next
:class: important
"SQL or NoSQL" is too coarse. A tour of the main database families: [types of databases](35-database-types.md).
:::
