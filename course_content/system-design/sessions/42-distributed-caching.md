# Chapter 42 · Distributed caching

## The big idea

One cache server has limits: its **memory**, its **network**, and it is a **single point of failure**.
A **distributed cache** spreads cached data across **many nodes** that act as one big, fast, shared memory
for all your application servers.

**Everyday example:** one tea stall can only stock so much and has one stove. A **chain of stalls** across
the city, each responsible for a few streets (shards), serves far more customers, and if one closes the
others still work.

```{raw} html
:file: ../diagrams/distributed-caching.html
```

## Why not just a local cache per app server?

| | Local (in-process) cache | Distributed (shared) cache |
|---|---|---|
| Speed | Nanoseconds | About 1 ms (network) |
| Shared across servers? | **No**: each server has its own copy | **Yes** |
| Memory efficiency | Duplicated N times | Stored once |
| Consistency | Each copy can be stale differently | One copy |
| Survives an app restart? | No | Yes |
| Best for | Tiny, very hot, rarely changing data | Large shared working sets, sessions |

Real systems use **both**: a tiny local cache for the hottest keys in front of the shared cache
(a **two-level cache**).

## Placing keys: sharding the cache

Which node holds a key? Options:

- **`hash(key) % N`:** simple but, when N changes, almost every key moves, so the **entire cache goes cold**
  and the database is flooded.
- **Consistent hashing:** adding or removing a node moves only about `1/N` of keys. The standard answer.
- **Hash slots (Redis Cluster):** 16,384 fixed slots assigned to nodes; resharding moves whole slots.

```python
import hashlib

def h(key): return int(hashlib.md5(key.encode()).hexdigest(), 16)

keys = [f"product:{i}" for i in range(20_000)]

def modulo_moved(old, new):
    return sum(1 for k in keys if h(k) % old != h(k) % new) / len(keys)

print(f"modulo placement, 5 -> 6 nodes: {modulo_moved(5, 6):.0%} of cached keys are lost")
print("consistent hashing, 5 -> 6 nodes: about", f"{1/6:.0%}", "of keys move (the new node's fair share)")
```

**Output:**

```text
modulo placement, 5 -> 6 nodes: 83% of cached keys are lost
consistent hashing, 5 -> 6 nodes: about 17% of keys move (the new node's fair share)
```

Losing 83% of the cache means 83% of reads suddenly hit the database. Consistent hashing (see its chapter)
limits that.

## Topologies

1. **Client-side sharding:** the client library hashes the key and talks to the right node directly. Fastest;
   every client needs the node list (Memcached).
2. **Proxy-based:** clients talk to a proxy (Twemproxy, Envoy) that routes. Simpler clients, one more hop.
3. **Cluster-aware (Redis Cluster):** nodes know the slot map and **redirect** (`MOVED`) clients that ask the
   wrong node.

## Replication for availability

If a cache node dies, its keys vanish and requests fall through to the database. Protect against it:

- **Replicas** per shard (primary and one or two replicas). If the primary dies, a replica is promoted
  (Redis Sentinel/Cluster). Replication is **asynchronous**, so a failover may lose a few recent writes;
  acceptable for a cache.
- **Multiple zones** for the replicas.
- **Warm replacement:** pre-load a new node (from the replica or a snapshot) before sending it traffic.

## Problems you must be able to name (and fix)

| Problem | What happens | Defence |
|---|---|---|
| **Cache stampede** | A hot key expires, thousands of requests hit the DB together | Request coalescing, per-key lock, serve stale while refreshing, refresh-ahead |
| **Cache penetration** | Requests for keys that **do not exist** always miss and hit the DB | Cache "not found" briefly; **Bloom filter** in front |
| **Cache avalanche** | Many keys expire at the same time (or a node dies) and the DB collapses | **TTL jitter**, replicas, rate limit the database |
| **Hot key** | One key (a celebrity) overloads one node | Local in-process cache, **replicate the hot key** to several nodes (`key#1`, `key#2`), split by suffix |
| **Big key** | A 50 MB value blocks the single-threaded node | Split into chunks; keep values small |
| **Cold start** | Empty cache after restart | Warm up, gradual traffic shift |
| **Inconsistency** | Cache differs from DB | Delete on write, short TTLs, versioned keys |

## Stampede protection in code

```python
import threading, time

cache, locks = {}, {}
db_calls = 0

def slow_db_read(key):
    global db_calls
    db_calls += 1
    time.sleep(0.05)
    return f"value-of-{key}"

def get(key):
    if key in cache:
        return cache[key]
    lock = locks.setdefault(key, threading.Lock())
    with lock:                                  # only one thread rebuilds; the others wait
        if key in cache:                        # re-check: someone may have filled it while we waited
            return cache[key]
        cache[key] = slow_db_read(key)
        return cache[key]

threads = [threading.Thread(target=get, args=("hot-key",)) for _ in range(50)]
for t in threads: t.start()
for t in threads: t.join()
print("50 simultaneous requests for an expired key -> database reads:", db_calls)
```

**Output:**

```text
50 simultaneous requests for an expired key -> database reads: 1
```

Without the lock this would be 50 database reads. With it, **one**. Across multiple servers use a distributed
lock (`SET key NX PX 5000`) or "single flight" logic.

## Sizing a cache cluster

```python
items = 100_000_000          # items worth caching
avg_item_bytes = 1_000       # 1 KB
overhead = 1.5               # keys, pointers, allocator overhead
replicas = 2                 # primary + 1 replica
node_ram_gb = 64             # usable ~48 GB after OS and headroom

data_gb = items * avg_item_bytes * overhead / 1e9
nodes = -(-int(data_gb * replicas) // 48)        # ceiling division
print(f"data: {data_gb:.0f} GB, with replicas {data_gb * replicas:.0f} GB -> {nodes} nodes of {node_ram_gb} GB")
print("ops capacity (100k ops/s per node):", nodes * 100_000, "ops/s")
```

**Output:**

```text
data: 150 GB, with replicas 300 GB -> 7 nodes of 64 GB
ops capacity (100k ops/s per node): 700000 ops/s
```

## Technology notes

| | Redis | Memcached |
|---|---|---|
| Data types | Strings, hashes, lists, sets, sorted sets, streams | Strings only |
| Persistence | Optional (RDB, AOF) | None |
| Replication, clustering | Built in | Client-side sharding |
| Threading | Mostly single-threaded per node | Multi-threaded |
| Extras | Pub/sub, Lua scripts, atomic counters, locks | Simple and very fast |

## Common mistakes

:::{warning}
- `hash % N` placement (a resize wipes the cache).
- No replica: one node failure sends its whole share of traffic to the database.
- Storing huge values or an unbounded list in one key.
- Using the cache as the only copy of important data.
- No jitter on TTLs, so keys expire in waves.
:::

## Try it yourself

1. Cache of 30 nodes, one dies, and the hash is `key % 30` (now `% 29`). What share of lookups become misses? What would consistent hashing give?
2. A product goes viral and one cache node is at 100% CPU. What do you do?
3. A cache node holds 5,000 keys per second of non-existent product ids requested by a scraper. What protects the database?

<details class="solution"><summary>Answers</summary>

1. About 29/30 = **97%** miss with modulo; about **1/30 = 3%** with consistent hashing.
2. A hot key: add a short **local in-process cache** on the app servers, and/or **replicate that key** to several nodes and spread reads, and rate limit if it is abuse.
3. **Cache penetration**: cache "not found" with a short TTL, put a **Bloom filter** of valid ids in front, and rate limit the scraper.

</details>

:::{admonition} Next
:class: important
The biggest cache of all, close to your users: the [CDN](43-cdn.md).
:::
