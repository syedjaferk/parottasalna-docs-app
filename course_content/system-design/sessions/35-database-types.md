# Chapter 35 · Types of databases

## The big idea

There is no single best database. Each **type** is built around one **shape of data** and one **access
pattern**, and is very good at that and poor at others. Picking a type is matching the tool to the job.

**Everyday example:** a kitchen has a knife, a blender and a pressure cooker. You could chop onions with
the blender, but you would be fighting the tool. Databases are the same.

```{raw} html
:file: ../diagrams/database-types.html
```

## 1. Relational (SQL)

**Shape:** tables with rows and columns, joined by keys. **Strong:** transactions, ad-hoc queries, integrity.

- Examples: PostgreSQL, MySQL, SQL Server, Oracle.
- Use for: orders, payments, users, inventory, almost any business data.

## 2. Key-value stores

**Shape:** `key -> value`, like a giant dictionary. **Strong:** blazing fast lookups by key, easy to scale.
**Weak:** no queries on the value.

- Examples: Redis, Memcached, DynamoDB, etcd.
- Use for: caches, sessions, shopping carts, feature flags, rate-limit counters.

## 3. Document stores

**Shape:** self-contained JSON-like documents, nested. **Strong:** flexible schema, one read gets the whole
object. **Weak:** joins, multi-document transactions.

- Examples: MongoDB, Couchbase, Firestore.
- Use for: product catalogues, user profiles, content management.

## 4. Wide-column stores

**Shape:** rows with a huge, sparse set of columns, grouped in **column families**; data **partitioned by key**
and sorted inside a partition. **Strong:** enormous write throughput, linear scaling, multi-region.
**Weak:** you must design tables for your queries; no joins.

- Examples: Cassandra, HBase, Bigtable, ScyllaDB.
- Use for: time-series events, messaging history, IoT, activity feeds.

## 5. Column-oriented (analytics / OLAP)

**Shape:** data stored **column by column**, compressed. **Strong:** scanning and aggregating billions of rows
on a few columns (`SUM(amount) GROUP BY day`). **Weak:** single-row updates.

- Examples: BigQuery, Snowflake, Redshift, ClickHouse, Parquet files.
- Use for: reports, dashboards, data warehouses.

## 6. Graph databases

**Shape:** nodes and edges. **Strong:** following relationships many hops deep ("friends of friends who
like cricket"). **Weak:** bulk analytics.

- Examples: Neo4j, Amazon Neptune.
- Use for: social networks, fraud rings, recommendations, knowledge graphs.

## 7. Time-series databases

**Shape:** timestamped measurements. **Strong:** fast append, rollups, retention policies, downsampling.

- Examples: InfluxDB, TimescaleDB, Prometheus.
- Use for: metrics, monitoring, sensor data, stock ticks.

## 8. Search engines

**Shape:** an **inverted index** (word -> documents). **Strong:** full-text search, relevance ranking,
fuzzy matching, faceting.

- Examples: Elasticsearch, OpenSearch, Solr.
- Use for: product search, log search.

## 9. Others you may meet

- **Vector databases** (Pinecone, pgvector): find **similar** items by embedding distance; AI search/RAG.
- **Object storage** (S3): store files and blobs cheaply and durably.
- **NewSQL / distributed SQL** (CockroachDB, Spanner, TiDB): SQL and ACID with horizontal scale.
- **In-memory databases** (Redis, Memcached): data in RAM, microsecond latency.
- **Ledger / blockchain** databases: immutable, verifiable history.

## Row store vs column store (a worked example)

```python
# 1 million orders, each with 10 fields. Query: total of the "amount" field.
rows = 1_000_000
fields = 10
bytes_per_field = 8

row_store_read = rows * fields * bytes_per_field          # must read whole rows
col_store_read = rows * 1 * bytes_per_field               # reads just the one column

print(f"row store reads   : {row_store_read / 1e6:6.1f} MB")
print(f"column store reads: {col_store_read / 1e6:6.1f} MB  ({fields}x less, and columns compress better)")
```

**Output:**

```text
row store reads   :   80.0 MB
column store reads:    8.0 MB  (10x less, and columns compress better)
```

That is why analytics databases are column-oriented, while transactional databases (which read and
write whole rows) are row-oriented.

## Matching type to workload

| Need | Pick |
|---|---|
| Money, orders, relationships, reporting | Relational |
| Sub-millisecond lookups, cache, sessions | Key-value / in-memory |
| Flexible product documents | Document |
| 100k+ writes per second, time-ordered events | Wide-column |
| Analytics over billions of rows | Column store / warehouse |
| "Friends of friends" queries | Graph |
| Metrics and sensors | Time-series |
| Search box | Search engine |
| "More like this" using AI embeddings | Vector |
| Photos, videos, backups | Object storage |

## Common mistakes

:::{warning}
- Using one database for everything, or one new database for each idea.
- Using a transactional database for heavy analytics (it slows the production workload).
- Choosing by popularity instead of the **access pattern**.
- Forgetting the cost of operating many different systems.
:::

## Try it yourself

1. Which database type for: a leaderboard, the ride-history of 50 million users, a company's monthly revenue dashboard, "customers who bought this also bought"?
2. Why is a column store a poor fit for a banking transaction system?
3. Why does Cassandra require you to design tables around your queries?

<details class="solution"><summary>Answers</summary>

1. Leaderboard: Redis (sorted set). Ride history: wide-column (Cassandra). Revenue dashboard: column-store warehouse (BigQuery/Snowflake). Recommendations: graph or relational with careful indexes; or a vector/recommendation system.
2. It is optimised for scanning columns, not for many small transactional single-row updates with strict ACID.
3. Data is partitioned by key and there are no joins, so each query needs a table already organised by its partition and sort key; you duplicate data across tables.

</details>

:::{admonition} Next
:class: important
A clever small structure that saves a lot of database lookups: [Bloom filters](36-bloom-filters.md).
:::
