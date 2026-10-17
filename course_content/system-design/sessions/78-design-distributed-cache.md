# Chapter 78 · Design a distributed cache

## Concepts to review first

This design is built from earlier chapters. Skim them if any term feels new:

- [Caching 101](39-caching-101.md)
- [Cache eviction policies](41-eviction-policies.md)
- [Distributed caching](42-distributed-caching.md)
- [Consistent hashing](11-consistent-hashing.md)
- [Bloom filters](36-bloom-filters.md)
- [Read-through vs write-through cache](67-read-through-vs-write-through-cache.md)

## The problem

Build a shared, in-memory cache like a **Redis or Memcached cluster**: many application servers read and write it, it
must be far faster than the database, and it must **keep working as nodes come and go**.

```{raw} html
:file: ../diagrams/distributed-cache.html
```

## Step 1: clarify requirements

**Functional:** `get(key)`, `set(key, value, ttl)`, `delete(key)`; **evict** entries when memory is full; **add and
remove nodes** without an outage.

**Non-functional:** about **1 ms** latency; hundreds of thousands of operations per second; hundreds of GB of
capacity; **a node failure must not send a flood of queries to the database**.

**Out of scope:** durable storage (the database is the source of truth), transactions, multi-region replication.

## Step 2: estimate memory and nodes

```python
import math

items = 200_000_000
hot_share = 0.20
item_bytes = 1_000
overhead = 1.5                   # keys, pointers and allocator overhead
replicas = 2                     # one primary plus one replica per shard
usable_gb_per_node = 48          # of a 64 GB machine, after the OS and headroom
ops_per_s = 400_000
ops_per_node = 100_000

hot_gb = items * hot_share * item_bytes * overhead / 1e9
total_gb = hot_gb * replicas
nodes_for_memory = math.ceil(total_gb / usable_gb_per_node)
nodes_for_ops = math.ceil(ops_per_s / ops_per_node) * replicas

print(f"hot data          : {hot_gb:.0f} GB")
print(f"with replicas     : {total_gb:.0f} GB")
print(f"nodes for memory  : {nodes_for_memory}")
print(f"nodes for traffic : {nodes_for_ops}")
print(f"plan for          : {max(nodes_for_memory, nodes_for_ops)} nodes")
```

**Output:**

```text
hot data          : 60 GB
with replicas     : 120 GB
nodes for memory  : 3
nodes for traffic : 8
plan for          : 8 nodes
```

## Step 3: one node, an LRU cache with TTL (O(1) get and set)

```python
from collections import OrderedDict

class CacheNode:
    def __init__(self, capacity, clock):
        self.capacity, self.clock, self.data = capacity, clock, OrderedDict()    # key -> (value, expires_at)

    def get(self, key):
        item = self.data.get(key)
        if item is None:
            return None
        value, expires_at = item
        if self.clock() >= expires_at:                 # expired: behave as a miss and free the space
            del self.data[key]
            return None
        self.data.move_to_end(key)                       # most recently used
        return value

    def set(self, key, value, ttl):
        self.data[key] = (value, self.clock() + ttl)
        self.data.move_to_end(key)
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)                # evict the least recently used

now = [0]
node = CacheNode(capacity=2, clock=lambda: now[0])
node.set("a", 1, ttl=10); node.set("b", 2, ttl=10)
print("get a            :", node.get("a"))
node.set("c", 3, ttl=10)                                 # full: evicts b (a was just used)
print("get b (evicted)  :", node.get("b"))
now[0] = 11                                              # time passes
print("get a (expired)  :", node.get("a"))
```

**Output:**

```text
get a            : 1
get b (evicted)  : None
get a (expired)  : None
```

## Step 4: the cluster, sharding with consistent hashing

```python
import bisect
import hashlib
import random
from collections import OrderedDict

def h(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)

class Ring:
    def __init__(self, names, vnodes=100):
        self.entries = sorted((h(f"{n}#{i}"), n) for n in names for i in range(vnodes))
        self.points = [p for p, _ in self.entries]
    def owner(self, key):
        return self.entries[bisect.bisect(self.points, h(key)) % len(self.entries)][1]

keys = [f"product:{i}" for i in range(20_000)]
before = Ring(["c1", "c2", "c3", "c4", "c5"])
after = Ring(["c1", "c2", "c3", "c4", "c5", "c6"])             # add a node

moved = sum(1 for k in keys if before.owner(k) != after.owner(k))
modulo_moved = sum(1 for k in keys if h(k) % 5 != h(k) % 6)
print(f"add a 6th node, consistent hashing: {moved / len(keys):.0%} of keys move")
print(f"add a 6th node, hash % N          : {modulo_moved / len(keys):.0%} of keys move (cache nearly wiped)")
```

**Output:**

```text
add a 6th node, consistent hashing: 15% of keys move
add a 6th node, hash % N          : 83% of keys move (cache nearly wiped)
```

## Step 5: what happens when a node dies (with and without a replica)

Simulate a Zipf-like workload against a 5-node cluster, kill one node, and count the **database queries** each design
causes:

```python
import bisect
import hashlib
import random

def h(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)

class Cluster:
    def __init__(self, names, replicate):
        self.entries = sorted((h(f"{n}#{i}"), n) for n in names for i in range(100))
        self.points = [p for p, _ in self.entries]
        self.up = {n: True for n in names}
        self.store = {n: set() for n in names}
        self.replicate, self.db_reads = replicate, 0

    def owners(self, key):
        start, out = bisect.bisect(self.points, h(key)) % len(self.entries), []
        for i in range(len(self.entries)):
            n = self.entries[(start + i) % len(self.entries)][1]
            if n not in out:
                out.append(n)
            if len(out) == (2 if self.replicate else 1):
                break
        return out

    def read(self, key):
        for n in self.owners(key):
            if self.up[n] and key in self.store[n]:
                return "hit"
        self.db_reads += 1                                   # miss: go to the database, then fill the cache
        for n in self.owners(key):
            if self.up[n]:
                self.store[n].add(key)
        return "miss"

def run(replicate):
    random.seed(8)
    cluster = Cluster(["c1", "c2", "c3", "c4", "c5"], replicate)
    keys = [f"k{i}" for i in range(3000)]
    weights = [1 / (i + 1) for i in range(len(keys))]
    for _ in range(30_000):                                     # warm the cache
        cluster.read(random.choices(keys, weights)[0])
    cluster.db_reads = 0
    cluster.up["c3"] = False                                    # a node dies
    for _ in range(10_000):
        cluster.read(random.choices(keys, weights)[0])
    return cluster.db_reads

print("database reads in the 10,000 requests after a node dies:")
print("  no replicas :", run(False))
print("  with replica:", run(True))
```

**Output:**

```text
database reads in the 10,000 requests after a node dies:
  no replicas : 1597
  with replica: 141
```

With a replica per shard, most of the dead node's keys are still served from the surviving copy, so the database
sees far fewer queries. This is the whole reliability story of a cache: **the cache protects the database, so its
failure must not become a database outage.**

## Step 6: the failure modes you must name

| Problem | What happens | Defence |
|---|---|---|
| **Stampede** | A hot key expires and thousands of requests miss together | Request coalescing, a per-key lock, refresh before expiry |
| **Penetration** | Requests for keys that do not exist always miss and hit the database | Cache "not found" briefly; a Bloom filter of valid keys |
| **Avalanche** | Many keys expire at the same time | Add random jitter to TTLs |
| **Hot key** | One key overloads one node | A tiny local in-process cache; replicate the hot key to several nodes |
| **Cold start** | An empty cache after a restart | Warm from a replica or snapshot before taking traffic |
| **Stale data** | The database changed, the cache did not | Delete the key on write; short TTLs as a safety net |

```python
import threading
import time

cache, locks, db_reads = {}, {}, 0

def slow_db(key):
    global db_reads
    db_reads += 1
    time.sleep(0.05)
    return f"value-of-{key}"

def get(key):
    if key in cache:
        return cache[key]
    lock = locks.setdefault(key, threading.Lock())
    with lock:                                   # only one thread rebuilds the entry
        if key not in cache:                     # re-check: someone may have filled it while we waited
            cache[key] = slow_db(key)
        return cache[key]

threads = [threading.Thread(target=get, args=("hot",)) for _ in range(100)]
for t in threads: t.start()
for t in threads: t.join()
print("100 simultaneous misses for one key -> database reads:", db_reads)
```

**Output:**

```text
100 simultaneous misses for one key -> database reads: 1
```

## Step 7: patterns and consistency

Use **cache-aside** by default: the app reads the cache, on a miss loads from the database and fills the cache; on a
write it updates the database and then **deletes** the cache key. Replication between a primary and replica is
**asynchronous**, so a failover may lose a few recent entries, which is fine because the cache is never the source
of truth.

## Trade-offs

| Choice | You gain | You pay |
|---|---|---|
| Cache-aside | Simple and robust | The first read of each key is slow |
| Async replication | Fast writes | A failover can lose recent entries |
| Short TTL | Fresher data | Lower hit rate, more database load |
| Consistent hashing | Cheap resizing | A client library or proxy must know the ring |

## Common mistakes

:::{warning}
- Placing keys with `hash % N` (every resize wipes the cache).
- Treating the cache as the only copy of important data.
- No TTL jitter, so keys expire in waves.
- No replica, so one node failure sends its whole share of traffic to the database.
- Huge values or unbounded lists stored under one key.
:::

## Try it yourself

1. Cache of 30 nodes, one dies, and placement is `key % 30` (then `% 29`). What share of lookups miss?
2. A product goes viral and one node is at 100% CPU. What do you do?
3. A scraper requests 5,000 non-existent product ids per second. How do you protect the database?

<details class="solution"><summary>Answers</summary>

1. About 29/30 = **97%** miss with modulo; with consistent hashing only about 1/30 = **3%** (that node's keys).
2. A **hot key**: add a small local cache on the app servers and/or replicate that key to several nodes, and rate limit if it is abuse.
3. **Cache penetration**: cache the "not found" result briefly, put a **Bloom filter** of valid ids in front of the cache, and rate limit the scraper.

</details>

:::{admonition} Try it in the playground
:class: important
Build it in [Design a Distributed Cache](/system-design/distributed-cache/).
:::

:::{admonition} Next
:class: important
Next case study: [Design an authentication system](79-design-authentication-system.md).
:::
