# Chapter 51 · Gossip protocol

## The big idea

In a **gossip protocol** every node, at regular intervals, picks a **few random peers** and **shares what it
knows** with them. Information spreads through the cluster **like a rumour**: exponentially fast, with no
central coordinator.

**Everyday example:** office gossip. One person hears "the boss is leaving". Over lunch they tell two
colleagues. Each of them tells two more at the next break. Within a few rounds **everyone knows**, and no
one had to send a company-wide email or maintain a list of whom to tell.

```{raw} html
:file: ../diagrams/gossip.html
```

## The problem it solves

In a large cluster (hundreds or thousands of nodes) you need every node to know **who is in the cluster and
who is alive**, and to share small bits of state (load, configuration, schema version). The obvious options
do not scale:

| Approach | Problem |
|---|---|
| **Central registry** | A SPOF and a bottleneck |
| **Every node tells every node (broadcast)** | N x N messages: 1,000 nodes means 1,000,000 messages per round |
| **A ring of heartbeats** | One broken node breaks the chain |

Gossip uses a **constant amount of work per node** and still reaches everyone in about **log(N)** rounds.

## How it works

Each round (say once per second), every node:

1. Picks a few (say 3) **random peers**.
2. Exchanges its **view of the cluster** (list of nodes with heartbeat counters/versions, application state).
3. **Merges** what it receives: keep the **newer** version of each entry.

If node A knows "node 7 heartbeat = 105" and B knows "node 7 heartbeat = 98", after they gossip B holds 105.
If a node's heartbeat counter **stops increasing** for long enough, others **suspect** it and eventually mark
it dead.

## The speed of rumours

```python
import random
random.seed(1)

def rounds_to_spread(n, fanout=2):
    """One node learns a fact. Each round, every informed node tells `fanout` random nodes. Count rounds until all know."""
    informed = {0}
    rounds = 0
    while len(informed) < n:
        newly = set()
        for node in informed:
            newly.update(random.sample(range(n), fanout))
        informed |= newly
        rounds += 1
    return rounds

print(" nodes   rounds until everyone knows")
for n in (10, 100, 1_000, 10_000, 100_000):
    avg = sum(rounds_to_spread(n) for _ in range(5)) / 5
    print(f"{n:>6}   {avg:5.1f}")
```

**Output:**

```text
 nodes   rounds until everyone knows
    10     4.4
   100     7.0
  1000    10.2
 10000    14.2
100000    17.8
```

Growing the cluster **10,000 times** adds only a handful of rounds. That logarithmic growth is why gossip scales.

## Failure detection with gossip

```python
import random
rng = random.Random(3)
N, ROUNDS, SUSPECT_AFTER = 8, 30, 8

counters = {n: {m: 0 for m in range(N)} for n in range(N)}     # what each node believes each heartbeat counter is
changed = {n: {m: 0 for m in range(N)} for n in range(N)}      # round when that belief last increased
alive = set(range(N))

def merge(a, b, r):
    """Two nodes exchange tables and both keep the higher counter for every node."""
    for m in range(N):
        top = max(counters[a][m], counters[b][m])
        for x in (a, b):
            if counters[x][m] < top:
                counters[x][m] = top
                changed[x][m] = r

for r in range(1, ROUNDS + 1):
    if r == 10:
        alive.discard(5)                                         # node 5 crashes at round 10
    for n in alive:
        counters[n][n] += 1                                      # each live node bumps its own heartbeat
        changed[n][n] = r
    for n in sorted(alive):
        peer = rng.choice([p for p in sorted(alive) if p != n])
        merge(n, peer, r)

observer = 2
suspects = [m for m in range(N) if ROUNDS - changed[observer][m] > SUSPECT_AFTER]
print("node 2 suspects (no heartbeat increase for more than", SUSPECT_AFTER, "rounds):", suspects)
```

**Output:**

```text
node 2 suspects (no heartbeat increase for more than 8 rounds): [5]
```

Nobody was told node 5 had died. Its heartbeat simply **stopped increasing**, and every node reached the
same conclusion on its own.

## Variations

- **Push gossip:** I send my news to peers.
- **Pull gossip:** I ask peers for their news.
- **Push-pull:** both; fastest convergence.
- **Anti-entropy:** periodically compare whole datasets (using Merkle trees) to repair differences.
- **Rumour mongering:** spread a new update until it is "old news" (peers already know it).
- **SWIM:** a protocol with direct and indirect pings and a gossip-spread suspicion list; used by Consul and
  Serf. Lower false positives than naive heartbeats.

## Where gossip is used

| System | What is gossiped |
|---|---|
| **Cassandra** | Cluster membership, node state, tokens |
| **DynamoDB (original), Riak** | Ring membership |
| **Consul / Serf** | Membership and failure detection (SWIM) |
| **Redis Cluster** | Node states, slot ownership |
| **Bitcoin / Ethereum** | Transactions and blocks spread peer to peer |
| **Amazon S3 (historically)** | State propagation |

## Strengths and weaknesses

| Strengths | Weaknesses |
|---|---|
| **Scales** to thousands of nodes | **Eventual**: no strong consistency, no agreement |
| **No single point of failure** | Takes several rounds to converge, so there is a delay |
| **Robust** to node and message loss (redundant paths) | Redundant messages waste some bandwidth |
| Simple to reason about and implement | Hard to *debug* (non-deterministic) and to bound exactly |
| Tunable (interval, fanout) | Needs seed nodes to bootstrap new members |

Gossip is for **membership, failure detection and loosely consistent metadata**. For decisions that must be
**agreed** (who is the leader), use **consensus**.

## Common mistakes

:::{warning}
- Using gossip where you need strong agreement (leader election, locks).
- A tiny cluster (under about 10 nodes) where a simple heartbeat to every peer is simpler.
- Gossip interval too short (bandwidth) or too long (slow detection).
- No seed nodes for new members to join through.
:::

## Try it yourself

1. Why does gossip need roughly log(N) rounds rather than N?
2. A node's gossiped heartbeat has not increased for 10 rounds. What do others do, and why not declare it dead immediately?
3. Why would you not use gossip to elect a leader?

<details class="solution"><summary>Answers</summary>

1. The number of informed nodes roughly **doubles** each round (each tells a few more), so reaching N takes about log2(N) rounds.
2. They **suspect** it, then declare it dead after more time/confirmation. A slow network or paused process looks the same as a crash; being hasty causes false positives.
3. Gossip only spreads information **eventually**; different nodes may hold different views for a while, so two nodes could both think they lead. Elections need consensus.

</details>

:::{admonition} Next
:class: important
A dependency that fails must not take you down with it: the [circuit breaker](52-circuit-breaker.md).
:::
