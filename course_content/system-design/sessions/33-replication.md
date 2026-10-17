# Chapter 33 · Data replication

## The big idea

**Replication** keeps **copies of the same data on several machines**, so one failure does not lose the
data and more machines can answer reads.

**Everyday example:** a teacher writes the day's notes on the board (the **primary**) and students copy
them into their notebooks (the **replicas**). If the board is erased, the notes still exist. Many students
can answer a question about the notes at once. But a student who copied late has slightly **old notes**
for a moment, which is the "replication lag".

```{raw} html
:file: ../diagrams/replication.html
```

## Why replicate

1. **Durability and availability:** a copy survives when a disk or machine dies; a replica can take over.
2. **Read scaling:** spread reads across replicas.
3. **Lower latency:** put a copy near users in another region.
4. **Operational safety:** run backups and heavy reports on a replica without slowing production.

## Leader-follower (primary-replica)

The most common design:

- **One leader** accepts **all writes**, and writes them to its log.
- **Followers** receive the log and apply it. They serve **reads**.
- If the leader dies, a follower is **promoted** (failover).

### Synchronous vs asynchronous

| | Synchronous | Asynchronous |
|---|---|---|
| Leader waits for follower's ack? | **Yes** | No |
| Write latency | Higher | Lower |
| Data safety on leader crash | No loss | **Last few writes may be lost** |
| If a follower is down | Writes may block | Writes continue |
| Reads on followers | Fresh | **Possibly stale** (replication lag) |

Common compromise: **semi-synchronous**: one follower is synchronous, the others asynchronous.

```python
import random
random.seed(2)

class Replica:
    def __init__(self, name):
        self.name, self.data = name, {}

leader = Replica("leader")
followers = [Replica("f1"), Replica("f2")]
pending = []                                  # asynchronous replication queue: (follower, key, value)

def write(key, value):
    leader.data[key] = value                   # leader commits immediately
    for f in followers:
        pending.append((f, key, value))        # ...and ships the change later

def replicate(n):
    for _ in range(min(n, len(pending))):
        f, k, v = pending.pop(0)
        f.data[k] = v

write("balance", 500)
print("right after write :", [f.data.get("balance") for f in followers], "(followers are behind)")
replicate(1)
print("after 1 delivery  :", [f.data.get("balance") for f in followers])
replicate(1)
print("after 2 deliveries:", [f.data.get("balance") for f in followers], "(caught up)")
```

**Output:**

```text
right after write : [None, None] (followers are behind)
after 1 delivery  : [500, None]
after 2 deliveries: [500, 500] (caught up)
```

A read sent to a follower right after the write returns nothing or an old value. That window is the
**replication lag**.

## Replication lag and its anomalies

| Problem | What the user sees | Fix |
|---|---|---|
| **Read-your-writes** | You post a comment, refresh, and it is gone | After a write, read **from the leader** for a while (or the same replica); or use a session token with the last log position |
| **Monotonic reads** | The page shows newer data, then older data on refresh (different replicas) | Pin a user to one replica |
| **Consistent prefix** | A reply shows before the question | Replicate causally related writes together |

## Failover problems

- **Detecting** a dead leader (timeouts) without false alarms.
- **Choosing** the most up-to-date follower.
- **Split brain:** old leader returns and thinks it is still leader. Use fencing and leader epochs.
- **Lost writes** with async replication (the new leader lacks the last few).

## Other topologies

- **Multi-leader:** several nodes accept writes (one per region). Good for local write latency and
  offline use. Cost: **write conflicts** must be resolved (last-write-wins, merge, CRDTs).
- **Leaderless (Dynamo, Cassandra):** any node accepts writes; clients write to W nodes and read from R
  nodes (quorums, R + W > N). Highly available, eventually consistent, uses read repair and hinted
  handoff.

| Topology | Writes | Conflicts | Used by |
|---|---|---|---|
| Single leader | One node | None | PostgreSQL, MySQL, MongoDB replica sets |
| Multi-leader | Many nodes | Possible | Multi-region setups, CouchDB |
| Leaderless | Any node | Possible | Cassandra, DynamoDB, Riak |

## Replication methods (how changes travel)

- **Statement-based:** ship the SQL. Breaks with non-deterministic functions (`NOW()`, `RANDOM()`).
- **Write-ahead log shipping:** ship the physical log (PostgreSQL streaming). Exact, version-coupled.
- **Logical / row-based:** ship row changes (MySQL row binlog, PostgreSQL logical). Flexible; the basis of
  **change data capture**.

## Replication vs sharding vs backups

| | Purpose | Copies the same data? |
|---|---|---|
| **Replication** | Availability, read scale | Yes |
| **Sharding** | Write and storage scale | No: splits the data |
| **Backups** | Recover from mistakes (a `DROP TABLE` replicates instantly!) | Point-in-time copies |

Replication is **not a backup**: a bad delete or corruption is copied to every replica.

## Common mistakes

:::{warning}
- Sending reads to replicas without handling lag (users cannot see their own writes).
- Treating replicas as backups.
- Replicas in the same rack or zone.
- Never testing failover, or having no plan for split brain.
:::

## Try it yourself

1. A user changes their profile photo and refreshes; the old photo shows. Why, and what is a simple fix?
2. With asynchronous replication, the leader crashes right after acknowledging a write. What can happen?
3. Why is a replica not a replacement for backups?

<details class="solution"><summary>Answers</summary>

1. The refresh was served by a lagging replica. Simple fix: read from the **leader for a short time after a write** (or stick the user to the leader/one replica).
2. That write may exist only on the old leader. If a follower is promoted without it, the write is **lost** (and the old leader may later conflict).
3. Mistakes (accidental delete, bad migration, corruption) replicate to all copies immediately. Backups keep older point-in-time states.

</details>

:::{admonition} Next
:class: important
Putting indexes, replicas and shards together in the order you should use them: [database scaling](34-database-scaling.md).
:::
