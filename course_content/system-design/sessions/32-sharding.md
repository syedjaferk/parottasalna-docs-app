# Chapter 32 · Database sharding

## The big idea

**Sharding** splits one big database into **several smaller databases (shards)**, each holding a
**part of the data** on its own machine. Together they hold everything; each handles only its share of
the traffic.

**Everyday example:** a library with 10 million books in **one room** has one queue and one
librarian. Split the books by author surname across **26 rooms** (A, B, C...), each with its own
librarian, and 26 people can be served at once. The rule "which room has this book?" is the **shard key**.

```{raw} html
:file: ../diagrams/sharding.html
```

## Why shard?

A single database server eventually hits a ceiling:

- **Storage:** the data no longer fits on one disk (tens of TB).
- **Write throughput:** one primary can only commit so many writes per second.
- **Read throughput:** replicas help reads, but not writes, and still hold the **entire** dataset.
- **Memory:** the working set no longer fits in RAM, so every query touches disk.

Replication copies the *same* data; sharding splits **different** data. Large systems use both.

:::{admonition} Shard late
:class: warning
Sharding is expensive: harder queries, harder transactions, harder operations. Try, in order:
better indexes, caching, read replicas, bigger machine, archiving old data. Shard only when the numbers
say so.
:::

## Sharding strategies

### 1. Range-based

Shard by **ranges of the key**: user ids 1-1M on shard 1, 1M-2M on shard 2.

- **Pro:** simple; efficient **range queries**.
- **Con:** **hot spots**. With auto-increment ids, all new writes land on the **last** shard. Uneven
  growth.

### 2. Hash-based

`shard = hash(key) % number_of_shards`

- **Pro:** spreads load evenly.
- **Con:** range queries touch every shard; changing the number of shards moves almost all data
  (use **consistent hashing** or a fixed large number of **virtual shards**).

### 3. Directory-based (lookup table)

A **lookup service** maps each key (or tenant) to a shard.

- **Pro:** flexible; move one customer without moving others; allows uneven shard sizes.
- **Con:** the directory is another component to scale and keep consistent (and a SPOF).

### 4. Geographic

Shard by region (EU users in an EU database). Good for latency and data-residency law.

```python
import hashlib

def stable_hash(key):
    return int(hashlib.md5(str(key).encode()).hexdigest(), 16)

N_SHARDS = 4

def hash_shard(user_id):
    return stable_hash(user_id) % N_SHARDS

def range_shard(user_id, size=250_000):
    return min(user_id // size, N_SHARDS - 1)

users = [10, 260_000, 510_000, 760_000, 900_000, 12345]
print("user_id   range-shard  hash-shard")
for u in users:
    print(f"{u:>8}  {range_shard(u):^11}  {hash_shard(u):^10}")

# new signups all get the highest ids: where do they land?
new_ids = range(900_000, 900_100)
print("range: new signups land on shards", sorted({range_shard(u) for u in new_ids}))
print("hash : new signups land on shards", sorted({hash_shard(u) for u in new_ids}))
```

**Output:**

```text
user_id   range-shard  hash-shard
      10       0           0     
  260000       1           2     
  510000       2           1     
  760000       3           0     
  900000       3           1     
   12345       0           3     
range: new signups land on shards [3]
hash : new signups land on shards [0, 1, 2, 3]
```

All fresh sign-ups hit one shard under range sharding (a **hot shard**), but spread across all under hash.

## Choosing the shard key (the most important decision)

A good shard key:

1. **High cardinality**: many distinct values (user_id, not country).
2. **Even distribution**: no value or shard gets most of the traffic.
3. **Matches the main query**: most queries include the key, so each touches **one** shard.
4. **Rarely changes.**

| Product | Good key | Bad key | Why |
|---|---|---|---|
| Social app | user_id | country | A few huge countries; uneven |
| Multi-tenant SaaS | tenant_id | created_at | New data piles on the newest shard |
| Chat | conversation_id | message_id | A chat's messages stay together |
| E-commerce orders | customer_id | order_status | Status has only 4 values |

## What gets harder

- **Cross-shard queries and joins:** `SELECT ... JOIN` across shards must **scatter-gather** (ask all
  shards, merge results). Slow. Design so common queries hit one shard; keep small shared tables
  (countries, currencies) **replicated to every shard**.
- **Transactions across shards:** no simple ACID. Use sagas or two-phase commit (slow), or design so a
  transaction stays inside one shard.
- **Unique ids:** auto-increment no longer works across shards. Use UUIDs, Snowflake-style ids, or per-shard
  ranges (see the unique IDs chapter).
- **Resharding:** moving data when you add shards is the scariest operation. Plan for it:
  start with **many logical shards** (say 1,024) mapped to few physical machines; adding a machine means
  **moving whole logical shards**, never splitting rows.
- **Hot keys:** one celebrity user gets millions of reads. Add caching, replicate that shard, or split that
  key.
- **Operations:** backups, migrations and monitoring multiply by the number of shards.

## Routing: who knows which shard?

- A **routing layer** (proxy such as Vitess or ProxySQL) hides sharding from the app.
- A **client library** computes the shard from the key.
- A **coordinator/config service** (ZooKeeper, etcd) holds the shard map.

## Real examples

- **Instagram** sharded PostgreSQL by user using logical shards and embedded shard ids inside photo ids.
- **Vitess** (YouTube) shards MySQL.
- **MongoDB, Cassandra, DynamoDB, CockroachDB** shard automatically (partition by key).

## Common mistakes

:::{warning}
- Sharding too early.
- A shard key that makes one shard hot (timestamps, auto-increment ids with range sharding).
- Using `hash % N` and then being unable to add shards without moving 80% of the data.
- Designing queries that need to join across shards constantly.
- Forgetting a plan for **rebalancing**.
:::

## Try it yourself

1. An orders table of 20 TB with queries mostly "all orders of one customer". Propose a shard key and a strategy.
2. Why is `hash(key) % N` painful when N changes?
3. How do you handle a lookup table like "countries" that every query joins against?

<details class="solution"><summary>Answers</summary>

1. Shard by **customer_id** with hash-based placement across many logical shards, so a customer's orders stay together.
2. Changing N reassigns most keys (around 80% when going from 4 to 5), forcing massive data movement. Use consistent hashing or logical shards.
3. **Replicate it to every shard** (it is small and rarely changes), so joins stay local.

</details>

:::{admonition} Next
:class: important
Sharding splits data; replication **copies** it for safety and read capacity: [replication](33-replication.md).
:::
