# Chapter 8 · Failover

## The big idea

**Failover** is automatically switching to a **backup** when the main component fails, so users see
little or no interruption.

**Everyday example:** a hospital's power. When the grid fails, a diesel generator starts within seconds
and the operating theatre keeps its lights. Nobody carries candles. Failover is the generator.

```{raw} html
:file: ../diagrams/failover.html
```

## The three parts of any failover

1. **Detect** that the primary is down (health checks, heartbeats).
2. **Decide** who takes over (a standby, or an election).
3. **Redirect** traffic (move a floating IP, update DNS, tell the load balancer).

The time between failure and recovery is the **failover time**. It is made of detection time + decision
time + redirect time, and it is the "downtime" in your availability maths.

## Patterns

### Active-passive (hot standby)

One node serves; a standby is kept in sync and idles until needed.

```text
t=0s   primary serves, standby replicates
t=1s   primary dies
t=4s   health check misses 3 beats -> declared dead
t=5s   standby is promoted and takes the floating IP
t=6s   traffic flows again          (about 5 seconds of errors)
```

- **Pro:** simple; only one node accepts writes, so no conflicts.
- **Con:** the standby is idle capacity; with **asynchronous replication**, writes the primary accepted
  but had not yet copied are **lost**.

### Active-active

Two or more nodes serve at once. If one dies, the others absorb its load.

- **Pro:** no idle machines, almost instant recovery.
- **Con:** each node must have headroom for the extra load (**N+1 sizing**), and for data, concurrent
  writers can **conflict**.

### Warm and cold standby

- **Warm:** a small copy runs, and is scaled up on failover. Recovers in minutes.
- **Cold:** the backup is built from backups or images when needed. Cheapest, recovers in hours.

| Pattern | Recovery time | Cost | Data-loss risk |
|---|---|---|---|
| Active-active | Seconds or none | Highest | Low (conflict handling needed) |
| Active-passive hot | Seconds to a minute | High | Small (replication lag) |
| Warm standby | Minutes | Medium | Medium |
| Cold standby | Hours | Lowest | Highest |

## Split brain: the dangerous failure

If the standby **thinks** the primary is dead (a network glitch) and promotes itself while the primary
is still alive, **both accept writes** and your data diverges.

Defences:

- **Quorum:** a node may be primary only if it can reach a **majority** of nodes. Use an odd number
  (3 or 5).
- **Fencing:** the new primary makes storage reject the old one (STONITH).
- **Leases:** the primary holds a time-limited lease and must stop serving if it cannot renew it.

## A failover simulation

```python
import random
random.seed(7)

servers = {"A": True, "B": True, "C": True}      # True = healthy

def pick():
    healthy = [name for name, ok in servers.items() if ok]
    if not healthy:
        raise RuntimeError("total outage")
    return random.choice(healthy)

served = {"A": 0, "B": 0, "C": 0}
for i in range(300):
    if i == 100:
        servers["B"] = False           # B crashes after request 100
    if i == 200:
        servers["B"] = True            # B is repaired
    served[pick()] += 1
print(served)
```

**Output:**

```text
{'A': 120, 'B': 59, 'C': 121}
```

All 300 requests were served although B was down for a third of the run. B simply received fewer.

## RTO and RPO

- **RTO (recovery time objective):** how long you may be down.
- **RPO (recovery point objective):** how much **data** you may lose.

Synchronous replication gives RPO close to zero but slower writes. Asynchronous replication is faster
but loses the last few seconds on failover. Pick from the business need.

## Common mistakes

:::{warning}
- Never **testing** failover. Untested failover usually fails the first time it is needed.
- Failover that overloads the survivors (3 nodes at 80% CPU cannot lose one).
- Ignoring split brain.
- Forgetting that **clients and caches** must notice the change: a long DNS TTL delays recovery.
:::

## Try it yourself

1. Three servers share load. What is the maximum safe average CPU each should run at so that losing one is survivable?
2. Why is a cluster of **2** nodes a poor choice for automatic failover, and what number is better?
3. Your database has async replication. What does failover cost you?

<details class="solution"><summary>Answers</summary>

1. The two survivors carry 3/2 = 1.5x load, so run at no more than about **60%** (60 x 1.5 = 90%).
2. With 2 nodes, a partition leaves each side with no majority, so you cannot tell who is right. Use **3 or 5** so a majority exists.
3. Writes acknowledged by the old primary but not yet replicated are **lost** (data-loss window = replication lag).

</details>

:::{admonition} Next
:class: important
Failover recovers quickly. **Fault tolerance** aims to hide the failure completely:
[fault tolerance](09-fault-tolerance.md).
:::
