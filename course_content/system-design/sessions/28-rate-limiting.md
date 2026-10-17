# Chapter 28 · Rate limiting

## The big idea

**Rate limiting** controls **how many requests** a client may make in a time window. Beyond the limit,
requests are rejected (or delayed) instead of overloading the system.

**Everyday example:** a nightclub bouncer who lets in **20 people per 10 minutes**. If 500 people arrive
at once, the dance floor does not collapse: most wait outside. The bouncer also stops one rowdy group
from taking every spot.

```{raw} html
:file: ../diagrams/rate-limiting.html
```

## Why limit?

1. **Protect the service** from overload (traffic spike, runaway client loop, retry storm).
2. **Fairness:** one heavy user must not starve everyone else.
3. **Security:** slow down brute-force logins, credential stuffing, scraping and denial of service.
4. **Cost control:** each call may cost money (database, SMS, third-party API).
5. **Business plans:** free = 100 requests per hour, paid = 10,000.

## What to limit by

| Key | Use | Caveat |
|---|---|---|
| **API key / user id** | Fair per-customer plans | Needs authentication first |
| **IP address** | Anonymous traffic, login pages | Offices and mobile carriers share one IP via NAT |
| **Endpoint** | Protect expensive routes (search, export) | |
| **Global** | Last-resort protection of a dependency | Punishes everyone |

Real systems combine them: per-user **and** per-IP **and** per-endpoint.

## The algorithms

### 1. Fixed window counter

Count requests in each clock window (e.g. each minute). Reset at the boundary.

- **Pro:** trivial, tiny memory (one counter per key).
- **Con:** the **boundary burst**: 100 requests at 12:00:59 and 100 more at 12:01:00 means 200 requests in
  2 seconds while still "within the limit".

### 2. Sliding window log

Store the **timestamp of each request**; count those in the last 60 seconds.

- **Pro:** exact, no boundary burst.
- **Con:** memory proportional to the limit (stores every timestamp).

### 3. Sliding window counter

Blend the current and previous fixed windows: `count = current + previous x (share of previous window
still inside the sliding window)`. Cheap and close to exact.

### 4. Token bucket (the most common)

A bucket holds up to **B tokens** and is refilled at **R tokens per second**. Each request takes one
token; with an empty bucket it is rejected.

- **Pro:** allows **short bursts** (up to B) while enforcing a long-run average rate R. Tiny memory.
- **Con:** two numbers to tune.

### 5. Leaky bucket

Requests enter a queue and are processed at a **constant rate**. Excess requests overflow and are
dropped. Smooths traffic into a steady stream (good for protecting a fragile downstream).

```{raw} html
:file: ../diagrams/token-bucket.html
```

## The algorithms in code

```python
class FixedWindow:
    def __init__(self, limit, window):
        self.limit, self.window, self.counts = limit, window, {}
    def allow(self, now):
        bucket = int(now // self.window)
        self.counts[bucket] = self.counts.get(bucket, 0) + 1
        return self.counts[bucket] <= self.limit

class SlidingLog:
    def __init__(self, limit, window):
        self.limit, self.window, self.log = limit, window, []
    def allow(self, now):
        self.log = [t for t in self.log if t > now - self.window]
        if len(self.log) < self.limit:
            self.log.append(now)
            return True
        return False

class TokenBucket:
    def __init__(self, capacity, refill_per_sec):
        self.capacity, self.rate = capacity, refill_per_sec
        self.tokens, self.last = capacity, 0.0
    def allow(self, now):
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

# Limit: 5 requests per 10 seconds. A client sends 5 at t=9.9..9.99 and 5 more at t=10.0..10.09
burst = [9.90, 9.92, 9.94, 9.96, 9.98, 10.00, 10.02, 10.04, 10.06, 10.08]

fixed, log, bucket = FixedWindow(5, 10), SlidingLog(5, 10), TokenBucket(5, 0.5)
print("time   fixed  sliding  token")
for t in burst:
    print(f"{t:5.2f}  {str(fixed.allow(t)):<6} {str(log.allow(t)):<8} {bucket.allow(t)}")
```

**Output:**

```text
time   fixed  sliding  token
 9.90  True   True     True
 9.92  True   True     True
 9.94  True   True     True
 9.96  True   True     True
 9.98  True   True     True
10.00  True   False    False
10.02  True   False    False
10.04  True   False    False
10.06  True   False    False
10.08  True   False    False
```

The fixed window let **all ten** through (five at the end of one window, five at the start of the
next): a burst of 10 in 0.2 seconds against a limit of 5 per 10 s. The sliding log and the token bucket
enforced the limit.

## What the client should see

```text
HTTP/1.1 429 Too Many Requests
Retry-After: 12
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1718000000
```

Always return **429** (not 500) with **Retry-After**, so well-behaved clients wait instead of hammering.
Good clients respond with **exponential backoff and jitter**.

## Rate limiting across many servers

Counters must be **shared**, or each server allows the full limit (with 10 servers, a "100 per minute"
limit becomes 1,000).

- **Central store (Redis):** `INCR key` + `EXPIRE` for fixed windows; a small **Lua script** makes
  token bucket checks atomic. Fast (sub-millisecond), but a dependency to keep alive.
- **Local limiting with sync:** each server enforces a share (limit / servers) and syncs periodically.
  Cheaper, slightly inexact.
- **At the edge:** the **API gateway, CDN or load balancer** enforces limits before traffic reaches your
  servers.
- **If Redis is down:** decide **fail open** (allow, risk overload) or **fail closed** (reject, risk
  outage). Most APIs fail open for general traffic and fail closed for login endpoints.

```text
-- Redis fixed window, atomic:
INCR   rl:user:42:2024-06-10T12:01
EXPIRE rl:user:42:2024-06-10T12:01 60      (only when the counter was just created)
if count > limit -> 429
```

## Limiting vs shedding vs backpressure

- **Rate limiting:** protects against *clients* sending too much.
- **Load shedding:** the server drops low-priority work when *it* is overloaded.
- **Backpressure:** a slow consumer tells producers to slow down (queues, streams).
- **Throttling:** slowing (delaying) instead of rejecting.

## Common mistakes

:::{warning}
- Per-server in-memory counters behind a load balancer (the limit multiplies by the number of servers).
- Limiting only by IP: NAT punishes offices; attackers rotate IPs.
- Returning `500` or silently dropping instead of `429` + `Retry-After`.
- Fixed windows without thinking about the boundary burst.
- A rate limiter that is itself a SPOF with no fail-open/closed decision.
:::

## Try it yourself

1. Design a limit of 100 requests per minute per user with bursts of up to 20 allowed. Which algorithm and parameters?
2. A fixed window limit is 60 per minute. What is the largest burst a client can send in two seconds?
3. You run 8 API servers each with a local 100-per-minute counter. What is the real limit?

<details class="solution"><summary>Answers</summary>

1. **Token bucket**: capacity 20, refill 100/60 = about 1.67 tokens per second.
2. **120** (60 at the end of one window, 60 at the start of the next).
3. About **800 per minute** (if traffic spreads evenly). Use a shared counter instead.

</details>

:::{admonition} Next
:class: important
APIs are covered. Now the data behind them, starting with transactions: [ACID](29-acid.md).
:::
