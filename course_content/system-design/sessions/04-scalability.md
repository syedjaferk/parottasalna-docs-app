# Chapter 4 · Scalability

## The big idea

A system is **scalable** if it keeps working well when the load grows, and you can fix the growth by
**adding resources** instead of rewriting everything.

**Everyday example:** Ravi opens a tea stall. On day one he serves 20 customers with one stove and
nobody notices the work. By the festival he has 2,000 customers. The queue is out of the street. He
has three choices: buy a bigger stove (**scale up**), open ten more stalls (**scale out**), or make
tea faster with a better process (**optimise**). Real systems face the same three choices.

:::{admonition} Two different problems
:class: tip
- **Performance problem:** the system is slow for *one* user.
- **Scalability problem:** the system is fast for one user and **slow or broken for a million**.

Always ask which one you have. Adding servers does not fix a slow query for a single user.
:::

## What "load" means

Load is not just "users". Pick the number that actually hurts:

| System | The load number | Why it matters |
|---|---|---|
| Web API | requests per second (RPS) | CPU and threads |
| Chat app | concurrent connections | memory per connection |
| Video site | outbound bandwidth (Gbit/s) | network links |
| Database | reads and writes per second, data size | disk and RAM |
| Search | queries per second **and** index size | both |

## Vertical scaling (scale up)

Buy a bigger machine: more CPU, RAM, faster disks.

- **Pro:** nothing changes in the code. One machine, no network hops, simple transactions.
- **Con:** there is a **ceiling** (the biggest server money can buy), cost rises faster than capacity,
  and one machine is a **single point of failure**. Upgrading often needs downtime.

## Horizontal scaling (scale out)

Add more machines and spread the work across them.

- **Pro:** nearly no ceiling, cheaper commodity machines, losing one machine loses a small share.
- **Con:** now you need a **load balancer**, servers must be **stateless**, and data needs
  **sharding and replication**. Everything becomes a distributed-systems problem.

```{raw} html
:file: ../diagrams/scaling-journey.html
```

## A worked example: how many servers?

Your API gets **30 million requests a day**. One server handles **250 requests per second** at a
comfortable 60% CPU. Peak is **3 times** the average. How many servers?

```python
import math

requests_per_day = 30_000_000
avg_rps = requests_per_day / 86_400
peak_rps = avg_rps * 3
per_server = 250

servers = math.ceil(peak_rps / per_server)
spare = math.ceil(servers * 0.3)         # N+30% headroom for failures and deploys
print(f"average: {avg_rps:.0f} rps, peak: {peak_rps:.0f} rps")
print(f"servers at peak: {servers}, with headroom: {servers + spare}")
```

**Output:**

```text
average: 347 rps, peak: 1042 rps
servers at peak: 5, with headroom: 7
```

The lesson: **one server is not enough at peak**, but the answer is a small number. Do the arithmetic
before drawing a big architecture.

## The scaling journey, in order

Do these in order. Each step solves the problem the previous one created.

1. **One server** runs the app and the database. Fine up to a few hundred users.
2. **Split the database** onto its own machine. The app and the data can now grow separately.
3. **Add a load balancer and a second app server.** Needs **stateless** servers: keep sessions in a
   shared store, not in server memory.
4. **Add a cache** (Redis) in front of the database. Most reads never reach it.
5. **Add read replicas.** Writes go to the primary, reads spread over copies.
6. **Put static files on a CDN.** Images and scripts stop touching your servers.
7. **Move slow work to a queue** (emails, thumbnails, reports). Users stop waiting for it.
8. **Shard the database** when one primary cannot take the writes or hold the data.
9. **Go multi-region** for latency and disaster recovery.

:::{admonition} Interview habit
:class: important
Never jump to step 8. Say: "At our numbers a single primary with replicas is enough, I would only
shard when writes exceed X per second or data exceeds Y TB." That sentence shows judgement.
:::

## Stateless vs stateful servers

A **stateless** server keeps nothing about a user between requests. Any server can answer any
request, so you can add, remove or restart servers freely.

```text
Stateful (hard to scale)              Stateless (easy to scale)
user -> server A (has the cart)       user -> any server -> cart in Redis
user -> server B  ... cart is gone    every server sees the same cart
```

If you must keep state (a WebSocket connection, a game room), keep it small, and make it
recoverable from a shared store.

## What usually blocks scaling

- **A shared bottleneck:** one database, one lock, one queue consumer. Find it by asking "what does
  every request touch?"
- **Hot spots:** one celebrity key or one popular shard takes most of the traffic.
- **Chatty designs:** a page that makes 50 internal calls multiplies latency and load.
- **Coordination:** anything needing all nodes to agree (global locks, strict ordering) limits speed.

## Common mistakes

:::{warning}
- Saying "just add more servers" without saying what keeps the servers independent (stateless, shared store).
- Sharding on day one. It makes every query and every deploy harder.
- Scaling the app tier when the **database** is the bottleneck.
- Forgetting that **cost** scales too: ask what the design costs per million requests.
:::

## Try it yourself

1. A service has 50 million requests a day and peak 4 times average. One server does 400 rps. How many servers, with 30% headroom?
2. Your login page is slow for one user (2 seconds) but fine under load. Is this a performance or a scalability problem?
3. Your app stores the shopping cart in server memory behind a load balancer. What breaks, and what is the smallest fix?

<details class="solution"><summary>Answers</summary>

1. 50M / 86,400 = 579 rps average; peak = 2,315 rps; 2,315 / 400 = 5.8, so **6 servers**; +30% = **8 servers**.
2. **Performance.** Fast under load means it is not a capacity issue. Profile the code and the queries.
3. The user may land on a different server and the cart vanishes. Smallest fix: store carts in **Redis keyed by user or session id**.

</details>

:::{admonition} Next
:class: important
Scaling makes failures more likely: more machines, more things to break. Next, keeping the system **up**: [availability](05-availability.md).
:::
