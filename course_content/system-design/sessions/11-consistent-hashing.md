# Chapter 11 · Consistent hashing

## The big idea

You have data (or cache entries) spread over several servers. You need a rule that says **which
server holds which key**, and the rule must keep working when you **add or remove a server**.
**Consistent hashing** is a rule where adding or removing a server moves only a **small share** of
the keys.

**Everyday example:** a school with 5 classrooms and students assigned by roll number
(`roll % 5`). A sixth classroom opens, and the rule becomes `roll % 6`. Almost every student has to
change rooms. Consistent hashing is like seating students around a circular table and giving each
classroom a section of it: a new classroom takes a few students from its neighbours and nobody else
moves.

## The problem with `hash(key) % N`

```python
import hashlib

def h(key):
    return int(hashlib.md5(key.encode()).hexdigest(), 16)

keys = [f"user:{i}" for i in range(10_000)]

def placement(n):
    return {k: h(k) % n for k in keys}

before = placement(4)
after = placement(5)                      # add one server
moved = sum(1 for k in keys if before[k] != after[k])
print(f"servers 4 -> 5: {moved / len(keys) * 100:.0f}% of keys moved")
```

**Output:**

```text
servers 4 -> 5: 80% of keys moved
```

About **80%** of keys change servers when you go from 4 to 5. For a cache, that means 80% of lookups
miss at once and **flood the database**. For a database it means moving most of your data. This is
unacceptable.

## The hash ring

1. Imagine a **ring** of positions from 0 to 2^32 - 1 (it wraps around).
2. **Hash each server** (by name) to a position on the ring.
3. **Hash each key** to a position.
4. A key belongs to the **first server clockwise** from its position.

```{raw} html
:file: ../diagrams/hash-ring.html
```

**Add a server:** it lands at one point and takes over the keys between itself and its
counter-clockwise neighbour. **No other key moves.** **Remove a server:** its keys fall to the next
server clockwise. Only about `1/N` of the keys are affected.

## Virtual nodes

With only a few servers on the ring, the arcs are uneven: one server may own 40% and another 10%.
The fix: give each real server **many points** on the ring ("virtual nodes", say 100 to 200).
Each server then owns many small slices scattered around the ring, and the load evens out. It also
lets you give a bigger machine **more virtual nodes** (more weight).

## A working implementation

```python
import bisect
import hashlib

def h(key):
    return int(hashlib.md5(key.encode()).hexdigest(), 16)

class Ring:
    def __init__(self, vnodes=100):
        self.vnodes = vnodes
        self.points = []            # sorted hash positions
        self.owner = {}             # position -> server name

    def add(self, server):
        for i in range(self.vnodes):
            pos = h(f"{server}#{i}")
            bisect.insort(self.points, pos)
            self.owner[pos] = server

    def remove(self, server):
        self.points = [p for p in self.points if self.owner[p] != server]
        self.owner = {p: s for p, s in self.owner.items() if s != server}

    def get(self, key):
        i = bisect.bisect(self.points, h(key)) % len(self.points)   # next point clockwise, wrapping
        return self.owner[self.points[i]]

keys = [f"user:{i}" for i in range(10_000)]

ring = Ring()
for s in ("A", "B", "C", "D"):
    ring.add(s)
before = {k: ring.get(k) for k in keys}

ring.add("E")
after = {k: ring.get(k) for k in keys}
moved = sum(1 for k in keys if before[k] != after[k])
print(f"servers 4 -> 5: {moved / len(keys) * 100:.0f}% of keys moved (ideal: 20%)")

counts = {}
for k in keys:
    counts[after[k]] = counts.get(after[k], 0) + 1
print("keys per server:", dict(sorted(counts.items())))
```

**Output:**

```text
servers 4 -> 5: 19% of keys moved (ideal: 20%)
keys per server: {'A': 2089, 'B': 2239, 'C': 1969, 'D': 1814, 'E': 1889}
```

Only about **one in five** keys moved, which is exactly the share the new server should own, instead
of 80%. And with 100 virtual nodes the keys are spread fairly evenly.

## Replication on the ring

To keep **N copies** of a key, store it on the first N **distinct** servers clockwise. Skip virtual
nodes belonging to a server already chosen, and prefer servers in different racks or zones. This is
exactly how Dynamo, Cassandra and Riak place replicas.

## Where it is used

| System | Why |
|---|---|
| Distributed caches (memcached clients, Redis clusters) | Adding a cache node should not wipe the cache |
| Dynamo, Cassandra, Riak | Partition data across nodes |
| CDNs and load balancers | Send the same URL to the same edge server for cache hits |
| Sharded databases | Rebalance with minimal data movement |

## Trade-offs and limits

- Needs a **lookup structure** (sorted list or tree) and every client must know the ring.
- **Hot keys** are not fixed by hashing: one very popular key still lands on one server.
- Many virtual nodes cost memory and make membership changes slightly slower.
- Simpler alternatives exist: a **fixed number of partitions** (say 1,024) assigned to nodes, like
  Redis Cluster's 16,384 hash slots. Moving a slot is easy to reason about.

## Common mistakes

:::{warning}
- Using `hash % N` for anything that must survive a change in N.
- Too few virtual nodes: uneven load.
- Forgetting that **all clients** must agree on the ring, or the same key goes to two servers.
- Believing consistent hashing balances **load**. It balances **keys**; a hot key is still hot.
:::

## Try it yourself

1. With `hash % N`, what share of keys moves going from 10 servers to 11? With consistent hashing?
2. Why do 3 servers placed once each on a ring give uneven shares?
3. How would you give one server twice the capacity of the others?

<details class="solution"><summary>Answers</summary>

1. With modulo, about 10/11 = **91%** move. With consistent hashing, about 1/11 = **9%**.
2. Three random points split the circle into three random arcs, which are rarely equal. Many virtual nodes average the randomness out.
3. Give it **twice as many virtual nodes** (for example 200 instead of 100).

</details>

:::{admonition} Next
:class: important
Now that data lives on many machines, we must decide what to give up when machines cannot talk to each other: the [CAP theorem](12-cap-theorem.md).
:::
