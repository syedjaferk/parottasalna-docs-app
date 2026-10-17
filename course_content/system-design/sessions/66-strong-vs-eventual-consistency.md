# Chapter 66 · Strong vs eventual consistency

## The big idea

When data is copied to several places, **consistency** describes **what a reader sees right after a write**.

- **Strong consistency:** after a write succeeds, **every** reader, anywhere, sees the **new** value. It behaves
  as if there were only one copy.
- **Eventual consistency:** after a write, readers **may see the old value for a while**, but if no new writes
  happen, **all copies eventually become identical**.

**Everyday example:** a **railway reservation chart**. With strong consistency, the moment one counter sells
seat 12A, every other counter in the country instantly knows it is gone: nobody can sell it twice, but each sale
must wait for the whole network to confirm. With eventual consistency, each counter sells from its own copy and
the copies sync every few minutes: sales are fast and the system keeps working if a link is down, but two
counters could sell **the same seat** before they sync.

```{raw} html
:file: ../diagrams/strong-vs-eventual.html
```

## What readers see

```text
t=0   Primary: x=1     Replica A: x=1     Replica B: x=1
t=1   client writes x=2 to the primary
t=2   Primary: x=2     Replica A: x=1     Replica B: x=1     <- replicas have not caught up
        STRONG:    read from A is forced to wait / go to primary -> returns 2
        EVENTUAL:  read from A returns 1  (stale)
t=3   Primary: x=2     Replica A: x=2     Replica B: x=1
t=4   all copies:  x=2                                         <- converged
```

## Comparison

| | **Strong** | **Eventual** |
|---|---|---|
| Read after write | Always the latest | **May be stale** |
| Write latency | Higher (wait for replicas / quorum) | **Lower** (acknowledge early) |
| Availability during partitions | Lower (may refuse requests) | **Higher** (always answers) |
| Throughput | Lower (coordination) | **Higher** |
| Reasoning for developers | **Easy**: like one database | Hard: anomalies, conflicts |
| Conflict handling | Prevented (single order) | Must be **resolved** (last-write-wins, merge) |
| Examples | Bank ledger, inventory of the last item, locks, Spanner, etcd, SQL primary | Social feeds, likes, DNS, CDN, shopping carts, Cassandra, DynamoDB (default) |

## Spectrum, not a switch

Between the extremes are useful middle grounds:

| Model | Guarantee |
|---|---|
| **Linearizable (strong)** | Operations appear to happen instantly in one global order |
| **Sequential** | All see the same order, not necessarily real time |
| **Causal** | If B depends on A (a reply to a comment), everyone sees A before B |
| **Read-your-writes** | **You** always see your own updates |
| **Monotonic reads** | You never see data **go back in time** |
| **Eventual** | Converges when updates stop |

Many systems offer **tunable** consistency (Cassandra and DynamoDB: choose per query).

## Simulating the difference

```python
import random
random.seed(6)

class Replica:
    def __init__(self):
        self.value, self.version = 0, 0

primary = Replica()
replicas = [Replica(), Replica()]

def write(value, strong):
    primary.value, primary.version = value, primary.version + 1
    if strong:                                    # strong: replicate to ALL replicas before acknowledging
        for r in replicas:
            r.value, r.version = primary.value, primary.version
    else:                                         # eventual: acknowledge now, replicas catch up later
        pass

def background_sync():
    r = random.choice(replicas)
    r.value, r.version = primary.value, primary.version

def read():
    return random.choice(replicas).value

for mode in ("strong", "eventual"):
    primary.value = primary.version = 0
    for r in replicas:
        r.value = r.version = 0
    stale = 0
    for step in range(1, 41):
        write(step, strong=(mode == "strong"))
        if mode == "eventual" and step % 3 == 0:
            background_sync()                     # replicas catch up only now and then
        if read() != step:
            stale += 1                            # the reader saw an older value than the latest write
    print(f"{mode:<9}: {stale:>2} of 40 reads right after a write were stale")
```

**Output:**

```text
strong   :  0 of 40 reads right after a write were stale
eventual : 31 of 40 reads right after a write were stale
```

Strong: **zero** stale reads, but every write waited for all replicas. Eventual: fast writes, many stale reads
until sync catches up.

## Conflicts under eventual consistency

If two replicas accept writes to the same item, they **disagree** and must reconcile:

- **Last-write-wins (LWW):** keep the highest timestamp. Simple; **silently loses** the other write and depends
  on clocks.
- **Version vectors:** detect that writes were **concurrent** and hand both to the application.
- **Application merge:** shopping carts merge by union.
- **CRDTs** (conflict-free replicated data types): data structures whose updates **always merge** correctly
  (counters, sets, text editing).

```python
# A grow-only counter CRDT (G-Counter): each replica counts only its own increments; merging takes the maximum per replica
def merge(a, b):
    return {r: max(a.get(r, 0), b.get(r, 0)) for r in a.keys() | b.keys()}

likes_mumbai = {"mumbai": 5}                    # 5 likes counted in Mumbai while partitioned from Chennai
likes_chennai = {"chennai": 3}                  # 3 likes counted in Chennai
merged = merge(likes_mumbai, likes_chennai)
print("merged:", merged, "-> total likes =", sum(merged.values()))
print("merging again changes nothing:", merge(merged, likes_chennai) == merged)
```

**Output:**

```text
merged: {'chennai': 3, 'mumbai': 5} -> total likes = 8
merging again changes nothing: True
```

No likes were lost, no coordination was needed, and merging in any order gives the same answer: the
essence of eventual consistency done right.

## Choosing, per piece of data

An online shop mixes both:

| Data | Model | Why |
|---|---|---|
| Payment and order total | **Strong** | Money must be exact |
| Stock of the last 3 units | **Strong** (or reserve atomically) | Do not oversell |
| Product description, images | Eventual | A minute-old text is harmless |
| "Viewed 1,203 times" | Eventual | Approximate is fine |
| Recommendations | Eventual | Nobody notices |
| Login / password change | Strong | Security |
| Social "like" count | Eventual | Fast, tolerant |

Strong everywhere is slow and expensive; eventual everywhere loses money. **Mix, per piece of data.**

## Techniques to make eventual consistency feel strong

- **Read-your-writes:** route a user's reads to the primary shortly after they write, or remember the version
  they wrote and wait for a replica to reach it.
- **Optimistic UI:** show the result immediately in the client.
- **Quorum reads and writes** (R + W > N) when you need freshness for a specific request.
- **Monotonic reads:** keep a user on one replica.
- **Idempotent, mergeable operations** that behave well when applied in any order.

## Common mistakes

:::{warning}
- Using eventual consistency for money or inventory of scarce items.
- Using strong consistency everywhere and then suffering latency and outages.
- Not saying how conflicts are resolved.
- Forgetting read-your-writes: a user posts a comment and does not see it.
:::

## Try it yourself

1. Label each strong or eventual: bank balance, tweet like count, passwords, a CDN-cached image.
2. Two replicas accept `likes += 1` simultaneously during a partition. Why is last-write-wins a bad merge here, and what works?
3. A user updates their profile and refreshes, and sees the old one. Which guarantee is missing, and a simple fix?

<details class="solution"><summary>Answers</summary>

1. Bank balance **strong**; like count **eventual**; passwords **strong**; CDN image **eventual**.
2. LWW keeps only one increment, losing the other. A **counter CRDT** (per-replica counts that merge by max) or merging increments keeps both.
3. **Read-your-writes**. Fix: read from the primary for a short time after a write (or until the replica reaches the written version).

</details>

:::{admonition} Next
:class: important
Who updates the cache, you or the cache? [Read-through vs write-through caching](67-read-through-vs-write-through-cache.md).
:::
