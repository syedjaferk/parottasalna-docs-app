# Chapter 60 · Top system design trade-offs

## The big idea

There is **no perfect design**, only designs that **give up the right things**. Every choice in system design
buys something and costs something. An interviewer is not looking for "the correct" architecture; they want to
hear you **name the trade-off, pick a side for a reason, and say when you would pick the other side**.

**Everyday example:** buying a vehicle. A bike is cheap and flexible but slow and unprotected from rain. A car
is fast and comfortable but costly and stuck in traffic. A train is cheap per person but only goes where the
tracks go. Nobody says one is "best": it depends on distance, budget and how many people travel.

```{raw} html
:file: ../diagrams/tradeoffs.html
```

## The master list

| # | Trade-off | You gain | You pay |
|---|---|---|---|
| 1 | **Latency vs throughput** | Batching raises throughput | Each item waits longer |
| 2 | **Consistency vs availability** (CAP/PACELC) | Always-correct reads **or** always-answering | Refused requests **or** stale data |
| 3 | **Strong vs eventual consistency** | Simple reasoning **or** speed and uptime | Slower writes **or** anomalies |
| 4 | **Vertical vs horizontal scaling** | Simplicity **or** near-unlimited growth | A ceiling and SPOF **or** distributed complexity |
| 5 | **SQL vs NoSQL** | Transactions and queries **or** scale and flexibility | Hard to shard **or** weaker guarantees |
| 6 | **Cache vs freshness** | Speed, lower load | Stale data, invalidation bugs |
| 7 | **Read-through vs write-through caching** | Simple reads **or** always-fresh cache | First-read miss **or** slower writes |
| 8 | **Push vs pull** | Instant delivery **or** consumer control | Fan-out cost **or** polling delay and waste |
| 9 | **Synchronous vs asynchronous** | Immediate answer **or** resilience and speed | Tight coupling **or** eventual results |
| 10 | **Stateful vs stateless** | Local speed **or** easy scaling | Hard to scale **or** repeated lookups |
| 11 | **Batch vs stream processing** | Efficiency **or** freshness | Delay **or** complexity |
| 12 | **REST vs RPC** | Uniform and cacheable **or** fast and typed | Verbose **or** tightly coupled |
| 13 | **Long polling vs WebSockets** | Simplicity **or** efficiency | Wasteful **or** stateful servers |
| 14 | **Monolith vs microservices** | Simplicity **or** team and scaling independence | Scaling limits **or** operational complexity |
| 15 | **Normalisation vs denormalisation** | No duplication **or** fast reads | Joins **or** update anomalies |
| 16 | **Space vs time** | Precomputed answers (indexes, caches) | Storage, slower writes |
| 17 | **Durability vs write speed** | Never lose data **or** very fast writes | Slower (fsync, sync replicas) **or** possible loss |
| 18 | **Cost vs performance / reliability** | Cheaper **or** faster and safer | Slower and riskier **or** more expensive |

The following chapters give each major pair its own detailed treatment.

## How to use a trade-off in an interview

A strong answer has four parts:

1. **State the decision:** "Should the notification service call the email provider synchronously?"
2. **State the options and what each buys:** "Sync gives the user an immediate result; async makes the request fast and
   survives provider outages."
3. **Pick, with a reason tied to the requirements and numbers:** "The user does not need to wait for the email, and
   the provider is flaky, so async with a queue."
4. **Say what would change your mind:** "If the email were a one-time login code that blocks sign-in, I would
   make the request wait, with a timeout and a fallback provider."

```python
def decide(topic, options, requirement):
    """A tiny template for stating trade-offs out loud."""
    choice, reason = options[requirement]
    others = [o for o in options if o != requirement]
    return f"{topic}: for '{requirement}' choose {choice} because {reason}; I'd reconsider for '{others[0]}'."

print(decide(
    "Order confirmation email",
    {"user waits for it": ("synchronous", "the user needs the result"),
     "user does not wait": ("a queue (asynchronous)", "it keeps the request fast and survives provider outages")},
    "user does not wait",
))
```

**Output:**

```text
Order confirmation email: for 'user does not wait' choose a queue (asynchronous) because it keeps the request fast and survives provider outages; I'd reconsider for 'user waits for it'.
```

## Questions to ask yourself for any choice

- **What is the requirement that decides this?** (latency target? consistency need? budget?)
- **What are the numbers?** (requests per second, data size, read/write ratio)
- **What fails, and how badly?**
- **What does it cost** in money, complexity, or people?
- **Is the decision reversible?** Choose simply when you can change later; invest carefully when you cannot (the shard key, the primary data model).
- **Which constraint is most important right now?** Optimise for it, and write down what you chose to neglect.

## Heuristics

| If the requirement is... | Lean towards |
|---|---|
| Money, inventory, bookings | Consistency, ACID, synchronous |
| Social feeds, likes, view counts | Availability, eventual consistency, async |
| Read-heavy | Caching, replicas, denormalisation, CDN |
| Write-heavy | Sharding, queues and batching, LSM stores |
| Small team, early product | Monolith, a single database, managed services |
| Huge scale, many teams | Services, sharding, async events |
| Latency-sensitive | Edge/CDN, caches, fewer hops, async for the rest |
| Spiky traffic | Queues, autoscaling, serverless |

## Common mistakes

:::{warning}
- Presenting a design as "the best" without naming what it costs.
- Naming trade-offs generically ("it depends") without tying them to the **numbers and requirements**.
- Choosing complexity (microservices, sharding) before the numbers demand it.
- Not saying what would make you change the decision.
:::

## Try it yourself

1. Pick any two rows of the table and, for a URL shortener, state the decision, the choice and what would change it.
2. A "like" counter: availability or consistency? What if it were a bank balance?
3. For each of these, name the trade-off in one phrase: adding an index, adding a cache, adding replicas.

<details class="solution"><summary>Answers</summary>

1. Example: "302 vs 301: 302 keeps click counting and expiry working but sends more traffic to us; I would switch to 301 if analytics were out of scope and load were a problem."
2. Likes: **availability** (eventual consistency, approximate counts are fine). Bank balance: **consistency**, even at the cost of refusing requests during a partition.
3. Index: faster reads vs slower writes and more storage. Cache: speed vs staleness and invalidation. Replicas: read scale and availability vs replication lag and cost.

</details>

:::{admonition} Next
:class: important
Details for each pair, starting with the most basic scaling decision: [vertical vs horizontal
scaling](61-vertical-vs-horizontal-scaling.md).
:::
