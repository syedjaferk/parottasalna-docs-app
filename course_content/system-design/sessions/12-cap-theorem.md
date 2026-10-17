# Chapter 12 · CAP theorem

## The big idea

When data is copied on several machines, the copies can **disagree** for a moment. The **CAP
theorem** says what you must give up when the network between those machines breaks.

**Everyday example:** two bank branches each keep a copy of your balance (Rs 1,000). The phone line
between the branches is cut. You walk into branch A and withdraw Rs 800. Then your friend, at branch
B, tries to withdraw Rs 800 from the same account. Branch B has two choices:

- **Refuse** ("sorry, I cannot confirm your balance right now"): safe, but B is **unavailable**.
- **Allow it** (B still thinks the balance is 1,000): B stays **available**, but the account is now
  overdrawn by Rs 600. The copies are **inconsistent**.

No third option exists while the line is cut. That is CAP.

```{raw} html
:file: ../diagrams/cap-theorem.html
```

## The three letters

- **C, Consistency:** every read sees the **latest write** (as if there were one copy).
- **A, Availability:** every request to a working node gets an **answer** (not an error).
- **P, Partition tolerance:** the system keeps working when the **network drops messages** between nodes.

:::{admonition} It is not "pick two of three"
:class: warning
In a real distributed system **partitions happen** (cables, switches, overloaded nodes that look
dead). You cannot opt out of P. So the real choice, **during a partition**, is:

- **CP:** stay consistent, refuse some requests.
- **AP:** stay available, accept that copies may disagree, repair later.

When there is **no** partition, you can have both C and A. (A "CA" distributed system only means "not
tolerant of partitions", which in practice means a single node.)
:::

## A concrete trace

Two replicas, A and B, of a counter `likes = 10`. The network between them is cut.

```text
t0  A: likes=10     B: likes=10
t1  client1 -> A: like        A: likes=11     (A cannot tell B)
t2  client2 -> B: read likes  B returns 10    <-- stale!

CP choice at t2: B says "error, cannot reach A, try later".   Consistent, not available.
AP choice at t2: B answers 10.                                  Available, not consistent.
t3  network heals: A and B exchange updates and converge to 11.
```

## What do real systems pick?

| System | Leans | During a partition |
|---|---|---|
| ZooKeeper, etcd, Consul, HBase | **CP** | The minority side stops accepting writes |
| Cassandra, DynamoDB, Riak, CouchDB | **AP** (tunable) | Both sides keep accepting reads and writes |
| Traditional SQL with sync replica | **CP** | Writes block if the replica cannot be reached |
| DNS, CDNs | **AP** | Serve what they have, even if stale |

Choose by asking **what is worse for the user, a wrong answer or no answer?**

- **Money, inventory of the last item, seat booking, leader election, locks:** wrong is worse. Choose **CP**.
- **Likes, view counts, feeds, product catalogues, shopping cart "add" actions:** stale is fine. Choose **AP**.

## Quorums: a dial between C and A

With **N** replicas, a write waits for **W** acknowledgements and a read asks **R** replicas. If
**R + W > N**, every read set overlaps every write set, so a read sees the latest value.

```python
def overlaps(n, w, r):
    return r + w > n

configs = [
    (3, 3, 1, "write to all, read one"),
    (3, 2, 2, "majority both (balanced)"),
    (3, 1, 1, "fastest, may read stale"),
    (3, 1, 3, "write one, read all"),
]
for n, w, r, label in configs:
    kind = "fresh reads" if overlaps(n, w, r) else "may be stale"
    print(f"N={n} W={w} R={r}  {label:<28} -> {kind}")
```

**Output:**

```text
N=3 W=3 R=1  write to all, read one       -> fresh reads
N=3 W=2 R=2  majority both (balanced)     -> fresh reads
N=3 W=1 R=1  fastest, may read stale      -> may be stale
N=3 W=1 R=3  write one, read all          -> fresh reads
```

`W=3` means one dead replica blocks all writes (less available). `W=1,R=1` never blocks but can read
stale data. Systems like Cassandra let you choose **per query**.

## PACELC: what about when there is no partition?

CAP only describes the partition case. **PACELC** adds: *Else* (no partition), you still trade
**Latency** against **Consistency**, because waiting for replicas to confirm costs time.

- DynamoDB and Cassandra: **PA/EL** (available during partitions, low latency otherwise).
- Spanner and most SQL clusters: **PC/EC** (consistent always, accept higher latency).

## Common mistakes

:::{warning}
- Saying "I choose CA". A distributed system cannot opt out of partitions.
- Treating CAP as a permanent label. It is a choice **during a partition**, and often per operation.
- Forgetting the **latency** cost of consistency when no partition exists (PACELC).
- Using "eventual consistency" without saying **how conflicts are resolved**.
:::

## Try it yourself

1. For each, say CP or AP: a seat-booking system, a "likes" counter, a distributed lock service.
2. N=5 replicas. What are the smallest W and R that guarantee fresh reads with W = R?
3. Why can a shopping-cart service accept writes on both sides of a partition and be fine?

<details class="solution"><summary>Answers</summary>

1. Seat booking **CP**, likes **AP**, lock service **CP**.
2. R + W > 5 with R = W gives 2W > 5, so **W = R = 3**.
3. Adding an item is commutative: merge the two carts by taking the union. Conflicts merge without losing the customer's intent (Amazon's original Dynamo cart).

</details>

:::{admonition} Next
:class: important
The core ideas are in place. Now follow a request across the network, starting with how networks are layered: [the OSI model](13-osi-model.md). (Strong versus eventual consistency gets its own chapter in the trade-offs part: [strong vs eventual consistency](66-strong-vs-eventual-consistency.md).)
:::
