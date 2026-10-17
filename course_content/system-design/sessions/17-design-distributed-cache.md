# Chapter 17 · Design a distributed cache

## The problem

Build a shared, in-memory cache like Redis or Memcached cluster: many application servers read and
write it, it must be much faster than the database, and it must keep working as nodes come and go.

```{raw} html
:file: ../diagrams/distributed-cache.html
```

## Requirements

- `get(key)`, `set(key, value, ttl)`, `delete(key)` in about **1 ms**.
- Hold hundreds of GB, hundreds of thousands of operations per second.
- Survive a node failure without a flood of database traffic.
- Eviction when memory is full.

## Single node first

A hash map gives O(1) lookup. To evict in O(1), combine it with a **doubly linked list** for **LRU**:
the hash map points into the list; each access moves the node to the front; evict from the tail.

```python
from collections import OrderedDict

class LRU:
    def __init__(self, capacity):
        self.cap, self.data = capacity, OrderedDict()
    def get(self, key):
        if key not in self.data: return None
        self.data.move_to_end(key)           # most recently used
        return self.data[key]
    def set(self, key, value):
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.cap:
            self.data.popitem(last=False)    # evict least recently used
```

Other policies: **LFU** (least frequently used), **FIFO**, **TTL** based. LRU is the default answer.

## Going distributed

- **Sharding by consistent hashing.** The client library (or a proxy) hashes the key to a node, so
  adding a node moves only about 1/N of the keys.
- **Replication.** Each shard has a replica; promote it if the primary dies. Replication is async,
  so a failover can lose a few recent writes, which is acceptable for a cache.
- **Hot keys.** One celebrity key overloads one node. Fixes: a short **local in-process cache**, or
  replicate the hot key to several nodes with suffixes.

## Cache patterns

- **Cache-aside** (default): app reads cache, on a miss reads the database and fills the cache.
- **Read-through / write-through:** the cache layer talks to the database for you; writes are
  consistent but slower.
- **Write-behind:** write to the cache, flush later; fast but risky.

## Failure modes

| Problem | What happens | Defence |
|---|---|---|
| **Stampede** | A hot key expires; thousands of requests hit the DB | Request coalescing / locks, early refresh |
| **Penetration** | Requests for keys that do not exist bypass the cache | Cache the "not found" result briefly, Bloom filter |
| **Avalanche** | Many keys expire together | Add random jitter to TTLs |
| **Stale data** | DB changed but the cache did not | Delete on write, short TTLs |

## Common mistakes

- Treating the cache as the source of truth.
- `hash % N` placement.
- No TTL jitter, no plan for a cold cache after a restart.

:::{admonition} Try it in the playground
:class: important
Build it in [Design a Distributed Cache](/system-design/distributed-cache/).
:::
