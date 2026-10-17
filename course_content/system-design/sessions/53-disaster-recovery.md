# Chapter 53 · Disaster recovery

## The big idea

**Disaster recovery (DR)** is the plan and tooling to **get your system back** after something big and
unlikely destroys it: a data-centre fire, a cloud region outage, ransomware, a bad deploy that corrupts data,
a human running `DROP DATABASE` in production.

**Everyday example:** the **fire drill and the insurance policy** of a company. You hope never to use them.
But if the building burns, the question is how quickly staff can work from somewhere else, and how much of
the paperwork survived. DR is deciding that **in advance, in writing, and practising it**.

```{raw} html
:file: ../diagrams/disaster-recovery.html
```

## HA vs DR

| | High availability | Disaster recovery |
|---|---|---|
| Protects against | A **component** failing (server, disk, zone) | A **whole site or region** lost, or **data** destroyed |
| Typical recovery time | Seconds | Minutes to hours |
| How | Redundancy within a region | A copy in **another region**, backups |
| Cost | Moderate | Varies with how fast you must recover |

A multi-AZ database is **HA**, not DR: a **regional** outage or a corrupted table takes it all.

## The two numbers that drive everything

- **RTO, Recovery Time Objective:** how long you may be **down**.
- **RPO, Recovery Point Objective:** how much recent **data you may lose** (measured in time).

```text
            last good copy                disaster                  service back
 ----------------|--------------------------|--------------------------|-----------> time
                 |<------ data lost -------->|<------- downtime ------->|
                          (RPO)                          (RTO)
```

Both are **business decisions**: ask what an hour of downtime or an hour of lost orders costs.

| Product | Reasonable RTO | Reasonable RPO |
|---|---|---|
| Internal wiki | 1 day | 1 day |
| Online shop | 1 hour | 5 minutes |
| Payments / UPI | Minutes | **Zero** |

## The four standard strategies

| Strategy | What you keep running | RTO | RPO | Cost |
|---|---|---|---|---|
| **Backup and restore** | Nothing: backups in another region | Hours | Hours (since last backup) | Lowest |
| **Pilot light** | Core data replicated; app servers **off** | Tens of minutes | Seconds to minutes | Low |
| **Warm standby** | A **scaled-down** full copy, running | Minutes | Seconds | Medium |
| **Multi-site active-active** | Full capacity in 2+ regions | **~0** | **~0** | Highest |

```python
STRATEGIES = [
    ("backup and restore", 240, 360, 1),     # name, RTO minutes, RPO minutes, relative cost
    ("pilot light",         30,   5, 2),
    ("warm standby",         5,   1, 4),
    ("active-active",        0,   0, 8),
]

def cheapest(max_rto_min, max_rpo_min):
    ok = [s for s in STRATEGIES if s[1] <= max_rto_min and s[2] <= max_rpo_min]
    return min(ok, key=lambda s: s[3])[0] if ok else "none: relax the targets or budget more"

needs = {"internal wiki": (1440, 1440), "online shop": (60, 5), "payments": (5, 0), "a blog": (1440, 720)}
for product, (rto, rpo) in needs.items():
    print(f"{product:<14} RTO<={rto:>4} min, RPO<={rpo:>4} min -> {cheapest(rto, rpo)}")
```

**Output:**

```text
internal wiki  RTO<=1440 min, RPO<=1440 min -> backup and restore
online shop    RTO<=  60 min, RPO<=   5 min -> pilot light
payments       RTO<=   5 min, RPO<=   0 min -> active-active
a blog         RTO<=1440 min, RPO<= 720 min -> backup and restore
```

Notice that the **cheapest option that meets "zero data loss" is active-active**: only synchronous or
multi-site designs reach an RPO of zero, which is why payments pay for the most expensive strategy while a
blog gets by with nightly backups.

## What a DR plan contains

1. **Inventory and priority:** which systems matter most, in what order to restore.
2. **Backups:** automated, **encrypted**, **versioned**, stored in **another region/account** (so a stolen
   credential or ransomware cannot delete them), with **immutability (object lock)**.
3. **Replication:** databases and object storage replicated to the DR region.
4. **Infrastructure as code:** the whole environment can be recreated from code (Terraform, CloudFormation),
   not from someone's memory.
5. **Runbooks:** step-by-step instructions anyone on call can follow at 3 am.
6. **Failover and failback procedure:** how to switch traffic (DNS, global load balancer) and how to return.
7. **Communication plan:** who is told what, and how, during an incident.
8. **Regular drills.**

## Backups: the 3-2-1 rule

- **3** copies of the data,
- on **2** different kinds of media,
- with **1** copy **off-site** (another region or provider).

Plus: **point-in-time recovery** (restore to 14:32, just before the bad delete), and **test restores**.

> A backup you have never restored is not a backup. It is a hope.

## Common disaster types and answers

| Disaster | Answer |
|---|---|
| Server or disk failure | HA (replicas, failover) |
| Availability-zone outage | Multi-AZ |
| **Region** outage | Cross-region replication + DR strategy |
| **Bad deployment / corrupted data** | **Rollback**, point-in-time restore (replication copies the corruption!) |
| **Ransomware / malicious deletion** | Immutable, off-account backups |
| **Cloud provider or vendor failure** | Multi-cloud or portable design (rarely worth it) |
| **Human error** | Least-privilege access, change review, deletion protection |

## Testing: the part everyone skips

- **Backup restore tests** on a schedule. Measure the real restore time (it is almost always longer than
  guessed).
- **Game days / failover drills:** actually switch to the DR region and run traffic there.
- **Chaos engineering:** inject failures in controlled ways.
- **Tabletop exercises:** walk through scenarios on paper.
- **Measure** actual RTO and RPO and fix the gap.

## Common mistakes

:::{warning}
- Assuming replication equals backup (a delete or corruption replicates instantly).
- Backups in the **same account and region** as production.
- Never testing a restore, or never timing it.
- A DR region that has **not been scaled, patched or kept in sync**.
- A runbook that depends on a system that is itself down (the wiki hosted in the failed region).
- Forgetting **DNS TTLs, secrets, certificates and third-party allow-lists** in the DR site.
:::

## Try it yourself

1. An online shop can lose at most 5 minutes of orders and be down at most 1 hour. Which strategy is the cheapest that meets this?
2. Why is a read replica not a disaster-recovery backup against accidental deletion?
3. What does the 3-2-1 backup rule say?

<details class="solution"><summary>Answers</summary>

1. **Pilot light** (RTO about 30 minutes, RPO about 5 minutes) or warm standby if you want margin; backup and restore is too slow.
2. The `DELETE` or `DROP` is replicated to the replica within seconds, so the data is gone from every copy. You need **point-in-time backups**.
3. Keep **3 copies**, on **2 media types**, with **1 copy off-site**.

</details>

:::{admonition} Next
:class: important
When something does go wrong in a system of dozens of services, how do you find the culprit? [Distributed
tracing](54-distributed-tracing.md).
:::
