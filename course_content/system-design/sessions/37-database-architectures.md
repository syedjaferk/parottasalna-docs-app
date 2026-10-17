# Chapter 37 · Database architectures

## The big idea

Beyond choosing a database, you choose **how copies of it are arranged** across machines, zones and
regions. The arrangement decides your **availability, latency, consistency and cost**. This chapter is
the catalogue of common arrangements.

**Everyday example:** a chain of banks. One head office that everything flows through (simple, but if it
fails the chain stops). Or each city branch can do business on its own and sync later (fast locally, but
two branches might approve conflicting things). The arrangement of offices is the architecture.

```{raw} html
:file: ../diagrams/database-architectures.html
```

## 1. Single node

One database server. Simple, strongly consistent, cheap. **A SPOF** and capped by one machine. Fine for
prototypes and small products with good backups.

## 2. Primary with replicas (active-passive)

One **primary** takes writes, **replicas** serve reads and stand ready for failover.

- Simple and the default for most applications.
- Reads scale, writes do not. Failover takes seconds to a minute.
- **Within a region**, spread replicas across availability zones.

## 3. Multi-AZ synchronous standby

A **synchronous replica in another availability zone** is kept in lockstep, so a zone failure loses no
committed data (RPO about 0). Managed services (AWS RDS Multi-AZ) do this. Writes pay a small latency
cost (about 1 to 3 ms).

## 4. Primary with cross-region read replicas

Replicas in other **regions** serve **local reads** to far-away users, and act as **disaster recovery**.
Replication is asynchronous (tens to hundreds of ms lag). **All writes still go to one region**, so
remote users pay a long round trip for writes.

## 5. Active-active (multi-primary / multi-region writes)

Several regions **accept writes** at the same time.

```text
Users in India  -> writes to Mumbai primary   \
Users in EU     -> writes to Frankfurt primary  >  replicate to each other
Users in US     -> writes to Virginia primary /
```

- **Pro:** low write latency everywhere; a region failure just redirects users; no idle standby.
- **Con:** **conflicts**: two regions update the same record at the same moment. Strategies:
  - **Partition ownership** (best): each record has a **home region** (a user is homed in India), so only
    one region writes it. Conflicts vanish; cross-region access is slower.
  - **Last write wins** (timestamps): simple, can silently lose updates and suffers from clock skew.
  - **Merge** with CRDTs or application logic (shopping carts).
  - **Consensus-based global databases** (Spanner, CockroachDB): strongly consistent, but each write pays
    cross-region latency (tens to hundreds of ms).
- Examples: Cassandra, DynamoDB Global Tables, MongoDB with zone sharding, Spanner.

### Comparing the options

| Architecture | Writes | Failover | Consistency | Complexity | Typical use |
|---|---|---|---|---|---|
| Single node | One | Manual restore | Strong | Lowest | Prototype |
| Primary + replicas | One region | Seconds to minutes | Strong on primary, lag on replicas | Low | Most apps |
| Multi-AZ sync standby | One region | Seconds, no data loss | Strong | Low (managed) | Production default |
| Cross-region replicas | One region | Minutes (manual or scripted) | Eventual remote reads | Medium | Global reads, DR |
| Active-active multi-region | **All regions** | Instant for users | Eventual or conflict rules | **High** | Global, always-on products |

## Disaster recovery strategies (how much to pay)

| Strategy | RTO | RPO | Cost |
|---|---|---|---|
| **Backup and restore** | Hours | Hours (since last backup) | Lowest |
| **Pilot light** (core DB replicated, rest switched off) | Tens of minutes | Seconds to minutes | Low |
| **Warm standby** (scaled-down copy running) | Minutes | Seconds | Medium |
| **Active-active** | ~0 | ~0 | Highest |

## Choosing

```python
def choose(needs_global_writes, can_lose_seconds_of_data, minutes_of_downtime_ok, budget):
    if needs_global_writes:
        return "active-active, with record ownership by home region to avoid conflicts"
    if not can_lose_seconds_of_data:
        return "primary + synchronous standby in another zone (multi-AZ)"
    if minutes_of_downtime_ok and budget == "low":
        return "primary + read replica(s); restore from backups in a disaster"
    return "primary + multi-AZ standby + cross-region read replica for DR"

print(choose(False, False, False, "high"))
print(choose(True, True, True, "high"))
print(choose(False, True, True, "low"))
print(choose(False, True, False, "high"))
```

**Output:**

```text
primary + synchronous standby in another zone (multi-AZ)
active-active, with record ownership by home region to avoid conflicts
primary + read replica(s); restore from backups in a disaster
primary + multi-AZ standby + cross-region read replica for DR
```

## Related patterns

- **CQRS:** separate the **write model** from one or more **read models** (a search index, a cache, a
  reporting table) kept up to date through events or change data capture.
- **Read replicas for analytics:** isolate heavy reports from production traffic.
- **Shard + replicate:** each shard has its own primary and replicas (the typical large-scale design).

## Common mistakes

:::{warning}
- Active-active without a conflict strategy.
- Cross-region replicas but no tested failover runbook.
- Believing multi-AZ protects against a **regional** outage (it does not).
- Paying for active-active when a warm standby would meet the business RTO and RPO.
:::

## Try it yourself

1. A product needs zero data loss on a zone failure but not on a region failure. What do you choose?
2. A global app has users in three continents who edit their own profiles only. How can you do active-active without conflicts?
3. What is the difference between RTO and RPO?

<details class="solution"><summary>Answers</summary>

1. **Primary with a synchronous standby in another AZ** (multi-AZ), plus async cross-region replica for DR.
2. **Home region per user**: each user's data is written only in their home region, so no two regions write the same record.
3. **RTO** is how long you can be down; **RPO** is how much recent data you can lose.

</details>

:::{admonition} Next
:class: important
One more database topic you will need in nearly every design: generating unique ids across many machines. Next: [unique IDs](38-unique-ids.md).
:::
