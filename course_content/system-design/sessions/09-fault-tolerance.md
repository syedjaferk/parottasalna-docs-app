# Chapter 9 · Fault tolerance

## The big idea

A **fault-tolerant** system **keeps working correctly while parts of it are failing**, with no visible
interruption. High availability says "recover fast". Fault tolerance says "do not even blink".

**Everyday example:** a passenger aircraft has two or more engines. If one fails mid-flight, the plane
keeps flying and lands normally. A car with one engine is "highly available" only as long as the engine
works, and it is not fault tolerant.

```{raw} html
:file: ../diagrams/fault-tolerance.html
```

## Fault, error, failure

Three different words:

- A **fault** is the cause (a disk dies, a bug, a network cable cut).
- An **error** is the wrong internal state the fault produces.
- A **failure** is what the user sees. Fault tolerance is **stopping faults from becoming failures**.

## Techniques

### 1. Redundancy (spare capacity)

Extra copies of compute, data and network paths. **N+1** (one spare) or **N+2** (two spares).

### 2. Replication with voting

Keep several copies and let the majority decide. Three replicas tolerate one wrong or dead copy
(**2f+1 nodes tolerate f failures**).

### 3. Graceful degradation

When a non-essential part fails, drop *that* feature and keep the core working.

```python
def product_page(product_id, recommendation_service_up=True):
    page = {"title": f"Product {product_id}", "price": 499}          # core: must work
    try:
        if not recommendation_service_up:
            raise TimeoutError("recommendations are down")
        page["recommended"] = ["Item A", "Item B"]
    except TimeoutError:
        page["recommended"] = []                                      # degrade, do not fail the page
        page["notice"] = "Recommendations are temporarily unavailable"
    return page

print(product_page(7))
print(product_page(7, recommendation_service_up=False))
```

**Output:**

```text
{'title': 'Product 7', 'price': 499, 'recommended': ['Item A', 'Item B']}
{'title': 'Product 7', 'price': 499, 'recommended': [], 'notice': 'Recommendations are temporarily unavailable'}
```

The shop still sells things when the recommendation engine is down. Decide in advance which features
are **critical** and which are **nice to have**.

### 4. Isolation (bulkheads)

Ships have watertight compartments so one hole does not sink the whole ship. In software: separate
thread pools, queues or even clusters per feature or per customer, so one overloaded part cannot eat
all resources.

### 5. Timeouts, retries and circuit breakers

Never wait forever; retry with backoff; stop calling a sick dependency (see the circuit breaker chapter).

### 6. Checkpointing and replay

Long jobs save progress, so a crash restarts from the last checkpoint instead of from zero. Streaming
systems replay from a log offset.

### 7. Self-healing

Orchestrators (Kubernetes) restart crashed containers and move work off dead machines automatically.

### 8. Testing failures: chaos engineering

You do not know you are fault tolerant until you have tried to break the system. **Chaos Monkey** kills
random servers in production hours so that teams build systems that survive it. Game days, fault
injection and failover drills do the same.

## Fault tolerance vs high availability vs disaster recovery

| | Goal | Typical downtime | Cost |
|---|---|---|---|
| **High availability** | Recover fast from component failure | Seconds to minutes | Medium |
| **Fault tolerance** | No interruption despite component failure | Zero | High |
| **Disaster recovery** | Recover from losing an entire site or region | Minutes to hours | Varies |

Choose by the cost of downtime. A life-support system pays for fault tolerance. A blog does not.

## Common mistakes

:::{warning}
- Aiming for full fault tolerance everywhere. It is expensive: protect the **critical path** only.
- Copies that fail together (same bug, same rack, same dependency).
- No graceful degradation: a failure in a minor feature breaks the whole page.
- Never injecting faults, so the first real fault is also the first test.
:::

## Try it yourself

1. Name three features of an online shop that can degrade and one that must not.
2. A system has 5 replicas voting on every write. How many can fail while it still works?
3. Why do aircraft use redundant systems built by different teams or vendors?

<details class="solution"><summary>Answers</summary>

1. Can degrade: recommendations, reviews, recently-viewed. Must not: checkout and payment.
2. Majority is 3 of 5, so **2** can fail.
3. Two copies of the same design share the same bugs. **Diverse** implementations are unlikely to fail in the same way (design diversity).

</details>

:::{admonition} Next
:class: important
The core vocabulary of speed: [latency, throughput and bandwidth](10-latency-throughput-and-bandwidth.md).
:::
