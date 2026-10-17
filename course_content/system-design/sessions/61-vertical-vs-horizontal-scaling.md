# Chapter 61 · Vertical vs horizontal scaling

## The big idea

When load grows you can make **one machine stronger** (**vertical scaling**, "scale up") or **add more
machines** (**horizontal scaling**, "scale out").

**Everyday example:** a pizza shop with a growing queue. Vertical: buy a **bigger oven** and hire a **faster
chef**. Horizontal: **open more outlets** and share the customers among them. The bigger oven is easy to set
up but has a maximum size; more outlets can grow without limit but now you must manage many shops and make
sure their menus match.

```{raw} html
:file: ../diagrams/vertical-vs-horizontal.html
```

## Side by side

| | **Vertical (scale up)** | **Horizontal (scale out)** |
|---|---|---|
| How | Bigger CPU, more RAM, faster disks | More machines behind a load balancer |
| Code changes | **None** | App must be **stateless**; data must be partitioned |
| Limit | **Hard ceiling** (biggest machine available) | Practically very high |
| Cost curve | **Super-linear**: 2x capacity costs more than 2x | Roughly linear (commodity machines) |
| Failure | **SPOF**: one machine | **Redundant**: lose one of many |
| Downtime to scale | Often needs a restart | **None**: add and remove nodes live |
| Complexity | Low | High: load balancing, consistency, discovery, deployment |
| Data consistency | Easy (one machine) | Harder (replication, sharding) |
| Latency between parts | None (in process) | Network hops |

## The cost curve in numbers

```python
# Illustrative cloud prices: price roughly doubles with each size step, capacity doubles, but there is a ceiling
sizes = [("small", 2, 70), ("medium", 4, 150), ("large", 8, 330), ("xlarge", 16, 720), ("2xlarge", 32, 1600), ("mega", 64, 3600)]
print("size      vCPU   $/month   $ per vCPU")
for name, cpu, price in sizes:
    print(f"{name:<9} {cpu:>4}   {price:>7,}   {price / cpu:>8.1f}")

target_cpu = 128
mega_cost = 2 * 3600                                    # two of the biggest machines (still the maximum per box)
small_cost = (target_cpu // 2) * 70                     # sixty-four small machines
print(f"\nneed {target_cpu} vCPU: two 'mega' boxes cost ${mega_cost:,}; 64 small boxes cost ${small_cost:,}")
print("but horizontal needs a load balancer, stateless code and 64 machines to operate and monitor")
```

**Output:**

```text
size      vCPU   $/month   $ per vCPU
small        2        70       35.0
medium       4       150       37.5
large        8       330       41.2
xlarge      16       720       45.0
2xlarge     32     1,600       50.0
mega        64     3,600       56.2

need 128 vCPU: two 'mega' boxes cost $7,200; 64 small boxes cost $4,480
but horizontal needs a load balancer, stateless code and 64 machines to operate and monitor
```

Per-unit price rises as the machine grows, until you simply **cannot buy a bigger one**. Horizontal scaling
trades **money** for **operational complexity**.

## What makes horizontal scaling possible

1. **Stateless application servers:** any server can handle any request; sessions live in a shared store.
2. **A load balancer** to spread requests.
3. **Shared or partitioned data:** replicas for reads, **sharding** for writes and size.
4. **Service discovery and automated deployment** (containers, orchestration).
5. **Idempotent, retry-safe operations**, since more parts means more failures.

State is the enemy of horizontal scaling. Databases are the hardest layer, because **data cannot be
duplicated freely**, which is why they are often scaled **vertically first** and horizontally later.

## When to choose which

| Situation | Choice |
|---|---|
| Early product, small team, quick fix | **Vertical**: simplest |
| Relational database not yet at its limits | **Vertical** first (plus replicas and caching) |
| Stateless web/API tier | **Horizontal** (easy, cheap, resilient) |
| Need high availability | **Horizontal** (more than one node, by definition) |
| Traffic is spiky or unpredictable | **Horizontal** with autoscaling |
| Workload that cannot be split (one big in-memory graph, a legacy app) | **Vertical** |
| Beyond the biggest machine | **Horizontal** |

Most real systems do **both**: scale each machine up to a sensible size, then scale out, and use **vertical
for the database primary**, **horizontal for everything stateless**.

## Autoscaling

Horizontal scaling can be **automatic**: add servers when CPU, queue depth or request rate cross a threshold,
remove them when load falls.

```python
def desired_servers(current, cpu_percent, target=60, min_servers=2, max_servers=20):
    """Target tracking, like AWS target-tracking scaling: scale proportionally to how far from the target we are."""
    wanted = -(-current * cpu_percent // target)           # ceiling of current * cpu / target
    return max(min_servers, min(max_servers, int(wanted)))

servers = 4
for cpu in (55, 90, 95, 70, 40, 25, 20):
    servers = desired_servers(servers, cpu)
    print(f"CPU {cpu:>3}% -> run {servers:>2} server(s)")
```

**Output:**

```text
CPU  55% -> run  4 server(s)
CPU  90% -> run  6 server(s)
CPU  95% -> run 10 server(s)
CPU  70% -> run 12 server(s)
CPU  40% -> run  8 server(s)
CPU  25% -> run  4 server(s)
CPU  20% -> run  2 server(s)
```

Mind the **lag** (new servers take a minute or more to start), keep **headroom**, and set a **minimum** so a
failure does not leave you with one server.

## Common mistakes

:::{warning}
- Scaling out an application that keeps session state in memory.
- Scaling the app tier when the **database** is the bottleneck (more app servers means more load on the same database).
- Buying ever-bigger machines instead of fixing a bad query.
- Forgetting that more machines mean **more failures** and need automation.
:::

## Try it yourself

1. Your web tier is stateless and CPU-bound; your database is at 40% CPU. Which scaling approach for each?
2. Why is vertical scaling a single point of failure?
3. Two 8-core servers behind a load balancer versus one 16-core server: which is more available, and why?

<details class="solution"><summary>Answers</summary>

1. Web tier: **horizontal** (add servers). Database: not yet needed; if it grows, scale **vertically** and add read replicas and caching first.
2. All the load lives on one machine; if it fails (or is restarted for an upgrade) the service is down.
3. The two servers: one can fail and the other keeps serving (at reduced capacity). The single 16-core machine takes everything down when it fails.

</details>

:::{admonition} Next
:class: important
Doing more things at once: [concurrency vs parallelism](62-concurrency-vs-parallelism.md).
:::
