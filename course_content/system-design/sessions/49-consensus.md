# Chapter 49 · Consensus algorithms

## The big idea

**Consensus** is how several machines **agree on one value** (who is the leader, what the next log entry
is, whether a transaction committed), even when some machines crash or messages are lost or delayed.

**Everyday example:** five friends decide where to eat over a flaky group chat, and some phones go offline.
They need a rule so that the group ends up with **one** restaurant, nobody picks two different ones, and a
decision once made is never reversed. The rule is: **a decision counts only when a majority (3 of 5) has
accepted it.** Any two majorities overlap, so no two conflicting decisions can both be approved.

```{raw} html
:file: ../diagrams/consensus.html
```

## Why it is hard

- Machines can **crash** at any time, or be paused.
- Messages can be **lost, duplicated, delayed or reordered**.
- You cannot tell a **dead** machine from a **slow** one.
- The famous **FLP result** says that with a purely asynchronous network and even one possible crash,
  no algorithm can *guarantee* agreement in bounded time. Practical algorithms use **timeouts** and accept
  that, in rare conditions, they may pause (stay safe, lose liveness) rather than disagree.

## Where consensus is used

| Problem | Example |
|---|---|
| **Leader election** | Which database node is primary? |
| **Replicated log / state machine** | Every replica applies the same commands in the same order |
| **Distributed locks and configuration** | etcd, ZooKeeper, Consul |
| **Atomic commit across nodes** | Spanner transactions |
| **Membership and metadata** | Which nodes are in the cluster? Kafka controller, Kubernetes state in etcd |

## The majority rule (quorum)

With **N** nodes, a decision needs **floor(N/2) + 1** votes. A cluster of N nodes tolerates
**floor((N-1)/2)** failures.

| Nodes | Majority needed | Failures tolerated |
|---|---|---|
| 1 | 1 | 0 |
| 2 | 2 | **0** (worse than 1 node: two ways to fail) |
| 3 | 2 | 1 |
| 4 | 3 | 1 (no better than 3) |
| 5 | 3 | 2 |
| 7 | 4 | 3 |

So use an **odd** number: 3 or 5 (7 rarely). More nodes tolerate more failures but make every decision slower
(more votes to collect).

## Paxos and Raft in one page

**Paxos** (Lamport, 1989) is the original, famously hard to understand. **Raft** (2014) was designed to be
understandable and is used in etcd, Consul, CockroachDB, TiKV and Kafka's KRaft.

### Raft in three parts

**1. Leader election.** Time is divided into **terms**. Each node is a **follower**, **candidate** or
**leader**. The leader sends **heartbeats**. A follower that hears nothing for a random timeout (150 to 300 ms)
becomes a **candidate**, increments the term and asks for votes. A node votes **once per term**; a
candidate with **a majority** becomes leader. Random timeouts avoid split votes.

**2. Log replication.** Clients send commands to the **leader**. It appends the command to its log and
sends it to followers. When **a majority** has stored it, the entry is **committed**, applied to the state
machine, and the client gets its answer.

**3. Safety.** A candidate can only win if its log is **at least as up to date** as a majority's, so a
committed entry is never lost. A new leader never overwrites committed entries.

```text
client --"set x=5"--> LEADER (term 3)
                       |-- append to log, send to F1, F2, F3, F4
                       |<- F1 ack, F2 ack          (3 of 5 have it = majority)
                       |-- COMMIT, apply, reply "ok"
                       |-- tell followers the new commit index in the next heartbeat
```

## Majority voting in code

```python
import random
random.seed(9)

def election(n_nodes, down, term=1):
    """Each live node votes for the first candidate that asks in this term. Candidates start in random order."""
    alive = [i for i in range(n_nodes) if i not in down]
    candidates = alive[:]
    random.shuffle(candidates)                    # whoever times out first asks first
    votes = {}
    for c in candidates:
        # a candidate asks everyone; a live node that has not voted yet in this term votes for it
        for voter in alive:
            if voter not in votes:
                votes[voter] = c
                if list(votes.values()).count(c) > n_nodes // 2:
                    return c, term
    return None, term

for n, down in [(5, set()), (5, {0, 1}), (5, {0, 1, 2}), (3, {0}), (3, {0, 1})]:
    leader, _ = election(n, down)
    status = f"leader = node {leader}" if leader is not None else "NO LEADER (no majority: cluster stays safe but stops)"
    print(f"{n} nodes, {len(down)} down -> {status}")
```

**Output:**

```text
5 nodes, 0 down -> leader = node 4
5 nodes, 2 down -> leader = node 3
5 nodes, 3 down -> NO LEADER (no majority: cluster stays safe but stops)
3 nodes, 1 down -> leader = node 1
3 nodes, 2 down -> NO LEADER (no majority: cluster stays safe but stops)
```

With 5 nodes the cluster survives 2 failures; with 3 failures it **refuses to elect a leader** rather than risk
two leaders. That is the safety-over-liveness choice.

## Alternatives and variants

| Algorithm | Notes |
|---|---|
| **Paxos / Multi-Paxos** | Original; Google Chubby, Spanner |
| **Raft** | Understandable; etcd, Consul, CockroachDB |
| **ZAB** | ZooKeeper's protocol |
| **Viewstamped Replication** | Older cousin of Raft |
| **PBFT / blockchains (PoW, PoS)** | **Byzantine** fault tolerant: tolerate nodes that **lie**; needs 3f+1 nodes |

Crash-fault-tolerant algorithms (Raft, Paxos) assume nodes fail by stopping, not by lying. Inside your own
data centre that is the right assumption.

## Practical design advice

- **Do not implement consensus yourself.** Use etcd, ZooKeeper or Consul, and keep the data small: they
  store **coordination metadata** (leaders, locks, configs), not your business data.
- **Spread nodes across failure domains** (3 zones). With 3 nodes in one zone, a zone outage kills consensus.
- **Latency:** every write needs a round trip to a majority, so keep the cluster within one region (or accept
  cross-region latency as Spanner does).
- **Throughput** is limited by the leader.

## Consensus vs the things that look similar

- **Replication** copies data; consensus decides **the order/agreement** of the copies.
- **Two-phase commit (2PC)** needs **all** participants to agree and blocks if the coordinator dies;
  consensus needs only a **majority** and tolerates failure.
- **Gossip** spreads information eventually but **does not** give agreement.

## Common mistakes

:::{warning}
- A two-node or four-node cluster (even numbers add cost, not tolerance).
- Placing all consensus nodes in one availability zone.
- Putting large application data through the consensus store.
- Rolling your own Paxos or Raft.
:::

## Try it yourself

1. How many failures does a 7-node Raft cluster tolerate, and how many votes does it need to commit?
2. Why does Raft use randomised election timeouts?
3. What happens in a 5-node cluster split by a network partition into groups of 3 and 2?

<details class="solution"><summary>Answers</summary>

1. Majority is 4, so it tolerates **3** failures and needs **4** acknowledgements.
2. So nodes rarely time out at the same moment; otherwise they would split the votes and need to retry indefinitely.
3. The group of **3 has a majority** and can elect a leader and commit. The group of 2 cannot, so it becomes read-only/unavailable: no two leaders exist.

</details>

:::{admonition} Next
:class: important
A very common use of consensus: letting only one process do something at a time, i.e. [distributed
locking](50-distributed-locking.md).
:::
