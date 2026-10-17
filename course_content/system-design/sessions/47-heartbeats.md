# Chapter 47 · Heartbeats

## The big idea

A **heartbeat** is a small message a node sends **regularly** to say "I am alive". If the heartbeats stop,
others conclude the node has probably failed and react (stop sending it traffic, elect a new leader,
restart its work).

**Everyday example:** a **hospital heart monitor**. The beeps mean the patient is fine. If the beeps stop for
a few seconds, an alarm sounds. The monitor cannot tell *why* it stopped (a failing heart, or a loose
wire), only that it did.

```{raw} html
:file: ../diagrams/heartbeats.html
```

## Why distributed systems need them

In a cluster nobody can **see** another machine. A node that has crashed, a node stuck in a long
garbage-collection pause, a node on the other side of a broken network and a node that is just slow all look
the same from outside: **silence**. Heartbeats are the practical way to *suspect* failure, so the system can:

- **Remove a dead server** from a load balancer,
- **Promote a new leader** (a database primary, a Kafka controller),
- **Reassign work** (a job a dead worker was running),
- **Release locks and leases** held by a dead client.

## Two styles

### Push: "I am alive"

Each node sends a heartbeat to a monitor or its peers every `T` seconds.

### Pull: "are you alive?"

A monitor **pings** each node (a health check) and expects a reply.

| | Push | Pull |
|---|---|---|
| Who initiates | The node | The monitor |
| Monitor load | Receives N messages | Sends N pings |
| Firewalls/NAT | Easy (node calls out) | The monitor must reach every node |
| Used by | Kafka, ZooKeeper sessions, Kubernetes node leases, workers | Load balancer health checks, Prometheus scraping |

## Detecting failure: the timeout

```text
heartbeat interval T = 1 s
failure timeout      = 3 x T = 3 s   (miss 3 beats in a row -> declare dead)
```

The timeout is a **trade-off**:

- **Too short:** a slow network or a GC pause causes a **false positive**, so a healthy node is declared
  dead, and possibly replaced while still running (split brain risk).
- **Too long:** a real failure goes unnoticed for a long time, hurting availability.

```python
import random
def detect(interval=1.0, missed_allowed=3, jitter=1.5, drop_chance=0.2, ticks=2000):
    """Count false alarms when the node is actually healthy but the network is slightly unreliable."""
    random.seed(5)
    last_seen, false_alarms = 0.0, 0
    for tick in range(1, ticks + 1):
        now = tick * interval
        if random.random() > drop_chance:            # this heartbeat arrives (maybe a bit late)
            last_seen = now + random.uniform(0, jitter)
        if now - last_seen > interval * missed_allowed:
            false_alarms += 1
            last_seen = now                            # the node "comes back"
    return false_alarms

for missed in (1, 2, 3, 5):
    print(f"declare dead after {missed} missed beat(s): {detect(missed_allowed=missed):>3} false alarms in 2,000 beats")
```

**Output:**

```text
declare dead after 1 missed beat(s):  58 false alarms in 2,000 beats
declare dead after 2 missed beat(s):  14 false alarms in 2,000 beats
declare dead after 3 missed beat(s):   3 false alarms in 2,000 beats
declare dead after 5 missed beat(s):   1 false alarms in 2,000 beats
```

On a network that drops 1 beat in 5, allowing only 1 missed heartbeat raises dozens of false alarms; waiting for 3 to 5 misses
removes nearly all of them, at the price of detecting a real failure 2 to 4 seconds later.
(Real failure detectors such as the **phi accrual detector** in Cassandra and Akka adapt the threshold to
observed network variation instead of using a fixed count.)

## What a heartbeat should contain

A bare "I am alive" is good; more useful ones carry:

- **Node id and a generation/epoch number** (to recognise a node that restarted),
- **Load and capacity** (CPU, queue depth) so schedulers can balance,
- **Version** of data or configuration it holds,
- **Term/leader information** (Raft leader heartbeats carry log positions).

## Liveness vs readiness

- **Liveness:** "is the process running?" (if not, restart it).
- **Readiness:** "can it serve traffic right now?" (not while warming up or when a dependency is down).

Kubernetes has both probes. A node that is alive but not ready should stay running but receive no traffic.
Shallow checks (process responds) are safe; **deep checks** (can I reach the database?) can cause a **mass
outage** if the database blips and every server marks itself unhealthy at once.

## Heartbeats in real systems

| System | Use |
|---|---|
| **Load balancers** | Health checks to remove dead servers |
| **Raft / ZooKeeper / etcd** | Leader sends heartbeats; followers that time out start an election |
| **Kafka** | Consumers heartbeat to the group coordinator; silence triggers a rebalance |
| **Kubernetes** | Kubelets update node leases; missing leases mark the node `NotReady` |
| **Cassandra, Consul** | Gossip-based failure detection |
| **Databases** | Replication heartbeats to detect a dead primary |

## Common mistakes

:::{warning}
- A fixed, tiny timeout that triggers on every garbage-collection pause.
- Treating "no heartbeat" as **proof** of death (it is only suspicion); fence the old node.
- Deep health checks that fail everyone at once when a shared dependency is slow.
- Heartbeats sharing a network path or thread pool with heavy traffic, so they are delayed under load, which is exactly when you need them.
:::

## Try it yourself

1. Heartbeats every 2 seconds and a timeout of 3 missed beats. How long can a failure go undetected?
2. A node is paused by a 20-second garbage collection. What do peers conclude, and what risk follows when it wakes up?
3. Why use a separate readiness check from the liveness check?

<details class="solution"><summary>Answers</summary>

1. Up to **about 6 to 8 seconds** (3 x 2 s, plus up to one more interval before the first miss is noticed).
2. They declare it dead and may replace it. When it wakes it still believes it is the leader/owner: **split brain**. Fence it with epochs or leases.
3. A starting or overloaded process is alive (restarting it would only make things worse) but should not receive traffic until it is ready.

</details>

:::{admonition} Next
:class: important
Once you know who is alive, clients must find them: [service discovery](48-service-discovery.md).
:::
