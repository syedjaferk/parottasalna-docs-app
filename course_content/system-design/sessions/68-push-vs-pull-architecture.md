# Chapter 68 · Push vs pull architecture

## The big idea

When data has to travel from a **producer** to a **consumer**, someone must **start** the transfer:

- **Push:** the **producer sends** the data to consumers as soon as it is available.
- **Pull:** the **consumer asks** for the data when it wants it.

**Everyday example:** **news delivery**. A **newspaper delivered to your door** is *push*: it arrives whether or
not you are free to read it. **Walking to the newsstand** is *pull*: you decide when, and what you take. Push is
timely and effortless for you; pull lets you control the pace and avoids waste when you are away.

```{raw} html
:file: ../diagrams/push-vs-pull.html
```

## Side by side

| | **Push** | **Pull** |
|---|---|---|
| Who starts | Producer | Consumer |
| Delivery timing | **Immediate** | At the next poll or request |
| Wasted work | Can send to consumers who are offline or busy | Empty polls when there is nothing new |
| Consumer control | Low: can be **overwhelmed** (needs back pressure) | **High**: takes only what it can handle |
| Producer must know consumers | **Yes** (a list, addresses, subscriptions) | **No** |
| Slow or dead consumers | A problem for the producer (retries, buffers) | Their own problem |
| Latency | Low | Up to the polling interval |
| Examples | WebSockets, webhooks, mobile push notifications, RabbitMQ delivery to consumers | HTTP GET, polling, SQS receive, **Kafka consumers**, Prometheus scraping |

## The hybrid reality

- **Kafka consumers pull**, even though it feels like a stream. Pulling lets each consumer read at **its own
  speed** and replay.
- **Prometheus pulls** metrics from services (scrape); **StatsD and the Datadog agent push**.
- **SQS and message queues:** consumers **pull**; some brokers (RabbitMQ) **push** to consumers with a
  **prefetch limit** (a back-pressure window).
- **Long polling** is *pull that behaves like push*; **webhooks** are push between servers.

## Fan-out: the classic push-vs-pull design problem

Social feeds (Twitter, Instagram): when **a user posts**, how do followers see it?

### Push (fan-out on write)

On posting, **copy the post id into every follower's feed cache** immediately.

- **Read is trivial and fast**: the feed is precomputed.
- **Write is expensive**: a user with 10 million followers triggers **10 million writes**.
- Wastes work for **inactive** followers who never open the app.

### Pull (fan-out on read)

On opening the app, **fetch recent posts from everyone you follow and merge** them.

- **Writes are cheap**: just store the post once.
- **Reads are expensive**: for someone following 1,000 accounts, 1,000 lookups per refresh.

```python
def push_cost(followers_of_poster, posts_per_day_per_user, avg_followers=200):
    # every post is copied into every follower's feed
    return followers_of_poster * posts_per_day_per_user

def pull_cost(accounts_followed, opens_per_day):
    # every feed refresh queries every account the user follows
    return accounts_followed * opens_per_day

# Regular user: 200 followers, follows 300, posts twice a day, opens the app 20 times a day
print("regular user:")
print("  push: writes per day per user:", push_cost(200, 2))
print("  pull: reads per day per user :", pull_cost(300, 20))

# Celebrity: 20 million followers, posts 3 times a day
print("celebrity:")
print("  push: feed writes per day:", f"{push_cost(20_000_000, 3):,}")
print("  pull: stored once, merged on read (cost spread across 20M readers' opens)")
```

**Output:**

```text
regular user:
  push: writes per day per user: 400
  pull: reads per day per user : 6000
celebrity:
  push: feed writes per day: 60,000,000
  pull: stored once, merged on read (cost spread across 20M readers' opens)
```

For regular users, **push** (precompute) is cheap. For celebrities push would mean 60 million writes a day for
three posts.

### The real answer: hybrid

Twitter and others use **push for normal users** (fast reads) and **pull for celebrities** (merge their recent
posts into the feed at read time). The rule of thumb: **push when fan-out is small and reads are frequent; pull
when fan-out is huge or readers are mostly inactive.**

## Other places the choice appears

| Problem | Push | Pull |
|---|---|---|
| Notifications | Mobile push (FCM/APNs), WebSockets | App checks periodically |
| Monitoring | Agents send metrics | Server scrapes (Prometheus) |
| Task distribution | Dispatcher assigns jobs to workers | Workers pull from a queue (better load balance, natural back pressure) |
| Config changes | Control plane pushes to hosts | Hosts poll for the latest version |
| Cache updates | Publish invalidation events | Entries expire by TTL |
| Data sync | CDC pushes changes | Periodic query |

### Why work distribution prefers pull

A dispatcher pushing jobs must know each worker's speed and load. If workers **pull** a job when ready, a fast
worker takes more, a slow one fewer, and a crashed one takes none: **automatic load balancing**.

## Back pressure

A push system can overwhelm consumers. Remedies: **bounded buffers**, **credit/window-based flow control**
("send me at most 100 more"), dropping or sampling, or switching to **pull**.

## Choosing

| Prefer push when | Prefer pull when |
|---|---|
| Updates are **rare but urgent** (alerts) | Updates are frequent and consumers differ in speed |
| Latency matters | Consumers should control the pace |
| Few consumers, known to the producer | Very many or unknown consumers |
| Consumers are usually online | Consumers are often offline or intermittent |
| | You want simple producers and easy scaling of consumers |

## Common mistakes

:::{warning}
- Polling every second at scale where push (or long polling) would do.
- Pushing to consumers with no back pressure or retry limits.
- Fan-out on write for accounts with millions of followers.
- Pushing to offline devices forever (no TTL or expiry on queued notifications).
:::

## Try it yourself

1. A system distributes image-resizing jobs to 50 workers of different speeds. Push or pull?
2. Why do big social networks use a hybrid for feeds?
3. Prometheus scrapes services, while StatsD receives pushes. Name a benefit of pull for monitoring.

<details class="solution"><summary>Answers</summary>

1. **Pull**: workers take jobs when ready, giving automatic load balancing and back pressure.
2. Push (precompute) is great for normal users but explodes for celebrities with millions of followers, so celebrity posts are **pulled and merged at read time**.
3. The monitoring server controls the rate and knows immediately when a target is down (the scrape fails); services need no knowledge of the monitoring system.

</details>

:::{admonition} Next
:class: important
Two styles of calling remote services: [REST vs RPC](69-rest-vs-rpc.md).
:::
