# Chapter 16 · Design a distributed key-value store

## The problem

Build something like DynamoDB or Cassandra: `put(key, value)` and `get(key)` over many machines,
for huge data, with low latency and no single point of failure.

```{raw} html
:file: ../diagrams/key-value-store.html
```

## Requirements

- `get`, `put`, `delete`; values up to about 1 MB.
- Scale to many TB and millions of operations per second by adding nodes.
- Highly available; tolerate node and zone failures.
- **Tunable consistency**: let the caller choose speed or freshness.

## The core ideas

1. **Partitioning with consistent hashing.** Nodes sit on a ring. A key goes to the first node
   clockwise from `hash(key)`. Use many **virtual nodes** per machine so load is even and adding a
   node steals small slices from many neighbours.
2. **Replication.** Copy each key to the next **N = 3** nodes on the ring (in different racks/zones).
3. **Quorums.** A write waits for **W** acks, a read asks **R** replicas. If **R + W > N** at least one
   replica in every read has the latest write. Common: N=3, W=2, R=2. Use W=1 for speed, R=1 for fast
   reads that may be stale.
4. **Any node can coordinate.** The client talks to any node; it forwards to the replicas.

## Handling failure

- **Detection:** nodes exchange state by **gossip**; no central master to fail.
- **Temporary failure:** **hinted handoff**. Another node holds the write for the dead one and hands
  it back when it returns.
- **Permanent failure:** rebuild the replica from the other copies (**anti-entropy** using
  **Merkle trees** to find the differing ranges quickly).
- **Conflicts:** two clients write the same key at the same time on different replicas. Options:
  **last write wins** (timestamps, simple, can lose data), or **vector clocks** (detect the conflict
  and let the app merge).
- **Read repair:** when a read finds a stale replica, fix it.

## Storage on each node

Writes go to a **commit log** (sequential, durable), then to an in-memory **memtable**; when full it
is flushed as an immutable sorted file (**SSTable**). Reads check the memtable and then SSTables, using
a **Bloom filter** to skip files that cannot hold the key. Background **compaction** merges files.
This is an **LSM tree**: very fast writes.

## CAP choice

This design is **AP**: during a partition it keeps answering, and repairs later. A CP store (like
etcd or ZooKeeper) would refuse writes without a majority instead.

## Common mistakes

- Using `hash(key) % N` (adding a node reshuffles almost everything).
- Saying "strong consistency" and "always available" together.
- No plan for conflicts.

:::{admonition} Try it in the playground
:class: important
Build it in [Design a Key-Value Store](/system-design/key-value-store/).
:::
