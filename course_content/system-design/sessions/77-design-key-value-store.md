# Chapter 77 · Design a distributed key-value store

## Concepts to review first

This design is built from earlier chapters. Skim them if any term feels new:

- [Consistent hashing](11-consistent-hashing.md)
- [Data replication](33-replication.md)
- [CAP theorem](12-cap-theorem.md)
- [Strong vs eventual consistency](66-strong-vs-eventual-consistency.md)
- [Gossip protocol](51-gossip-protocol.md)
- [Heartbeats](47-heartbeats.md)
- [Bloom filters](36-bloom-filters.md)
- [Checksums](16-checksums.md)

## The problem

Build something like **DynamoDB or Cassandra**: `put(key, value)` and `get(key)` over many machines, for far more
data than one machine holds, with low latency, and **no single point of failure**.

```{raw} html
:file: ../diagrams/key-value-store.html
```

## Step 1: clarify requirements

**Functional:** `get`, `put`, `delete`; values up to about 1 MB; scale by **adding nodes** with no downtime; let callers
choose between faster and fresher reads (**tunable consistency**).

**Non-functional:** **always available** for reads and writes even when nodes fail; single-digit-millisecond latency;
horizontal scalability to many TB and millions of operations per second; durability (acknowledged writes survive).

**Out of scope:** secondary indexes, SQL, multi-key transactions. In CAP terms we are choosing **AP with a dial**
(see the CAP chapter).

## Step 2: estimate

```python
import math

data_tb = 100                  # before replication
replicas = 3
node_tb = 10                   # usable disk per node
headroom = 1.3                 # compaction needs free space; nodes fail

stored_tb = data_tb * replicas
nodes_min = math.ceil(stored_tb / node_tb)
nodes_plan = math.ceil(nodes_min * headroom)

ops_per_s = 2_000_000
ops_per_node = 20_000
nodes_for_ops = math.ceil(ops_per_s / ops_per_node)

print(f"data on disk with {replicas} copies: {stored_tb} TB")
print(f"nodes for storage: {nodes_min}, with headroom: {nodes_plan}")
print(f"nodes for throughput ({ops_per_s:,} ops/s): {nodes_for_ops}")
print(f"plan for: {max(nodes_plan, nodes_for_ops)} nodes")
```

**Output:**

```text
data on disk with 3 copies: 300 TB
nodes for storage: 30, with headroom: 39
nodes for throughput (2,000,000 ops/s): 100
plan for: 100 nodes
```

Replication triples the storage, and here **throughput** (not storage) decides the size. Both numbers say the same
thing: this must be **many machines**, so partitioning and failure handling are the heart of the design.

## Step 3: partitioning with a consistent hash ring

Every node is placed on a **ring** (with many virtual nodes). A key goes to the first node clockwise from `hash(key)`.
Adding a node moves only about 1/N of the keys. (See the consistent hashing chapter for why `hash % N` would be a
disaster.)

## Step 4: replication, quorums, hinted handoff and read repair

- **Replicas:** each key lives on the next **N = 3** distinct nodes on the ring.
- **Quorums:** a write is acknowledged after **W** replicas confirm; a read asks **R** replicas. With **R + W > N**,
  every read overlaps the latest write. Common setting: **N=3, W=2, R=2**.
- **Hinted handoff:** if a replica is down during a write, another node **holds the write as a hint** and replays it
  when the replica returns, so a short outage costs nothing.
- **Read repair:** a read that finds an out-of-date replica **writes the newest value back to it**.

A working miniature of all four:

```python
import bisect
import hashlib

def h(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)

class Node:
    def __init__(self, name):
        self.name, self.up, self.data, self.hints = name, True, {}, []        # data: key -> (version, value)

class Cluster:
    def __init__(self, names, n=3, w=2, r=2, vnodes=50):
        self.nodes = {name: Node(name) for name in names}
        self.n, self.w, self.r, self.version = n, w, r, 0
        self.ring = sorted((h(f"{name}#{i}"), name) for name in names for i in range(vnodes))
        self.points = [p for p, _ in self.ring]

    def replicas(self, key):
        start, chosen = bisect.bisect(self.points, h(key)) % len(self.ring), []
        for i in range(len(self.ring)):
            name = self.ring[(start + i) % len(self.ring)][1]
            if name not in chosen:
                chosen.append(name)
            if len(chosen) == self.n:
                break
        return chosen                                                      # the next N distinct nodes clockwise

    def put(self, key, value):
        self.version += 1
        acks = 0
        for name in self.replicas(key):
            node = self.nodes[name]
            if node.up:
                node.data[key] = (self.version, value)
                acks += 1
            else:                                                           # hinted handoff: a live node keeps the write
                holder = next(x for x in self.nodes.values() if x.up and x.name not in self.replicas(key))
                holder.hints.append((name, key, (self.version, value)))
        return "ok" if acks >= self.w else "FAILED: not enough replicas"

    def get(self, key):
        contacted = [self.nodes[name] for name in self.replicas(key) if self.nodes[name].up][: self.r]
        if len(contacted) < self.r:
            return None, "FAILED: not enough replicas"
        answers = [(node.data.get(key, (0, None)), node) for node in contacted]
        (best_version, best_value), _ = max(answers, key=lambda a: a[0][0])
        repaired = []
        for (version, _), node in answers:
            if version < best_version:                                      # read repair
                node.data[key] = (best_version, best_value)
                repaired.append(node.name)
        return best_value, f"repaired {repaired}" if repaired else "consistent"

    def recover(self, name):
        self.nodes[name].up = True
        for holder in self.nodes.values():                                  # replay hints addressed to the recovered node
            for hint in [x for x in holder.hints if x[0] == name]:
                self.nodes[name].data[hint[1]] = hint[2]
                holder.hints.remove(hint)

cluster = Cluster(["n1", "n2", "n3", "n4", "n5"])
key = "user:42"
owners = cluster.replicas(key)
print("replicas for", key, ":", owners)

print("1. put v1                 :", cluster.put(key, "v1"))
cluster.nodes[owners[0]].up = False
print(f"2. {owners[0]} goes down; put v2   :", cluster.put(key, "v2"), "(W=2 of 3 is enough)")
print("3. get (R=2)              :", cluster.get(key))

cluster.nodes[owners[0]].up = True                         # it returns WITHOUT replaying hints, still holding v1
print(f"4. {owners[0]} back, still stale   :", cluster.nodes[owners[0]].data.get(key))
print("5. get (R=2) hits the stale node:", cluster.get(key))
print(f"6. {owners[0]} now holds           :", cluster.nodes[owners[0]].data.get(key))

cluster.nodes[owners[1]].up = cluster.nodes[owners[2]].up = False
print("7. two replicas down; get :", cluster.get(key))
print("8. two replicas down; put :", cluster.put(key, "v3"))
```

**Output:**

```text
replicas for user:42 : ['n4', 'n1', 'n2']
1. put v1                 : ok
2. n4 goes down; put v2   : ok (W=2 of 3 is enough)
3. get (R=2)              : ('v2', 'consistent')
4. n4 back, still stale   : (1, 'v1')
5. get (R=2) hits the stale node: ('v2', "repaired ['n4']")
6. n4 now holds           : (2, 'v2')
7. two replicas down; get : (None, 'FAILED: not enough replicas')
8. two replicas down; put : FAILED: not enough replicas
```

Follow the story: with one replica down the write still met **W=2** and a hint was stored; when a read happened to
contact the stale node the **newest version won** and the stale node was **repaired**; and with two of three replicas
down the cluster **refused** to answer rather than risk returning old data: that is the consistency side of the dial
(set R=1 and W=1 and it would answer, with the risk of staleness).

## Step 5: conflicts and detecting failure

- **Concurrent writes** to the same key on different replicas need a rule. **Last-write-wins** (highest timestamp) is
  simple but can silently lose a write and relies on synchronised clocks. **Vector clocks** record each replica's
  version so the system can tell "newer" from "concurrent" and hand the conflict to the application to merge (a
  shopping cart merges by union).
- **Failure detection** has no master: nodes **gossip** their view of the cluster every second; a node whose heartbeat
  counter stops increasing is suspected, then declared dead.
- **Permanent loss:** rebuild the replica from the others. **Anti-entropy** compares replicas using **Merkle trees** (a
  tree of hashes: equal roots mean identical data, otherwise descend to the differing range only).

## Step 6: the storage engine on each node (LSM tree)

Writes must be **very fast and durable**:

```python
class MiniLSM:
    """Memtable in memory, a commit log for durability, immutable sorted files when the memtable fills up."""
    def __init__(self, memtable_limit=3):
        self.log, self.memtable, self.sstables, self.limit = [], {}, [], memtable_limit

    def put(self, key, value):
        self.log.append((key, value))                     # 1. append to the commit log (sequential, durable)
        self.memtable[key] = value                         # 2. update memory
        if len(self.memtable) >= self.limit:               # 3. flush as an immutable, sorted file (an SSTable)
            self.sstables.append(dict(sorted(self.memtable.items())))
            self.memtable, self.log = {}, []

    def get(self, key):
        if key in self.memtable:                           # newest data first ...
            return self.memtable[key], "memtable"
        for i, table in enumerate(reversed(self.sstables)):    # ... then the newest file down to the oldest
            if key in table:
                return table[key], f"sstable #{len(self.sstables) - i}"
        return None, "not found"

db = MiniLSM()
for k, v in [("a", 1), ("b", 2), ("c", 3), ("a", 10), ("d", 4), ("e", 5)]:
    db.put(k, v)
print("sstables on 'disk':", db.sstables)
print("memtable          :", db.memtable)
print("get a             :", db.get("a"), "(the newer value wins)")
print("get b             :", db.get("b"))
print("get zzz           :", db.get("zzz"))
```

**Output:**

```text
sstables on 'disk': [{'a': 1, 'b': 2, 'c': 3}, {'a': 10, 'd': 4, 'e': 5}]
memtable          : {}
get a             : (10, 'sstable #2') (the newer value wins)
get b             : (2, 'sstable #1')
get zzz           : (None, 'not found')
```

Real engines add **Bloom filters** (skip files that cannot contain the key) and background **compaction** (merge files
and drop overwritten values).

## Step 7: trade-offs

| Choice | You gain | You pay |
|---|---|---|
| AP (always answer) | Availability through failures and partitions | Stale reads and conflicts to resolve |
| N=3 replicas | Survive node and rack loss | 3 times the storage |
| W=2, R=2 | Reads see the latest write | More latency than W=1, R=1 |
| Gossip membership | No master, scales to thousands | Eventual agreement, delayed detection |
| LSM storage | Very fast writes | Read amplification, compaction work |

## Common mistakes

:::{warning}
- Placing keys with `hash(key) % N` (adding a node reshuffles nearly everything).
- Claiming "strong consistency" and "always available" together.
- No plan for conflicting writes.
- All replicas in the same rack or zone.
- Forgetting repair (hints, read repair, anti-entropy).
:::

## Try it yourself

1. N=5. What W and R give fresh reads with W = R? What happens to availability when 2 nodes are down?
2. Why does a key-value store use virtual nodes?
3. Which repair mechanism fixes data a node missed during a long outage, and which fixes a short one?

<details class="solution"><summary>Answers</summary>

1. R + W > 5 with W = R gives **W = R = 3**. With 2 nodes down, 3 remain, so reads and writes at quorum 3 still work (with 3 down they would not).
2. Without them the arcs of the ring are uneven (one node owns far more) and adding a node steals from a single neighbour. Many small slices even out load and rebalancing.
3. **Hinted handoff** covers short outages; **anti-entropy with Merkle trees** repairs long ones. **Read repair** fixes whatever a read happens to find.

</details>

:::{admonition} Try it in the playground
:class: important
Build it in [Design a Key-Value Store](/system-design/key-value-store/).
:::

:::{admonition} Next
:class: important
Next case study: [Design a distributed cache](78-design-distributed-cache.md).
:::
