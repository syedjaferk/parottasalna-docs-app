# Chapter 20 · Load balancing

## The big idea

A **load balancer** sits in front of many identical servers and decides **which server handles each
request**. It also notices dead servers and stops using them.

**Everyday example:** a supermarket with 8 checkout counters and a person at the front pointing to the
shortest queue. Without them, everyone picks counter 1, and it jams while seven counters sit idle.

```{raw} html
:file: ../diagrams/load-balancing.html
```

## What a load balancer gives you

1. **Scale:** add servers to add capacity.
2. **Availability:** if one server dies, traffic goes to the rest.
3. **Zero-downtime deploys:** take servers out one at a time, update, put back.
4. **A single address** for clients, whatever happens behind it.

## Layer 4 vs Layer 7

- **Layer 4 (transport):** looks only at IP and port. It forwards TCP connections. Very fast, cheap,
  does not read the request. (AWS NLB, HAProxy in TCP mode.)
- **Layer 7 (application):** reads the HTTP request, so it can route by **path, header, cookie or
  host**, terminate TLS, rewrite, cache and compress. Slower but far more flexible. (Nginx, AWS ALB,
  Envoy.)

Example of L7 routing: `/api/*` to the API pool, `/images/*` to an image service, `/admin` only from
the office IP range.

## The algorithms, with code

```python
import random
import itertools
from collections import Counter

servers = ["s1", "s2", "s3"]
random.seed(11)

# 1. Round robin: take turns
rr = itertools.cycle(servers)
round_robin = [next(rr) for _ in range(9)]

# 2. Weighted round robin: s1 is twice as big
weights = {"s1": 2, "s2": 1, "s3": 1}
pool = [s for s, w in weights.items() for _ in range(w)]
wr = itertools.cycle(pool)
weighted = [next(wr) for _ in range(8)]

# 3. IP hash: the same client always lands on the same server
def ip_hash(ip):
    return servers[sum(ip.encode()) % len(servers)]

print("round robin :", round_robin)
print("weighted    :", weighted)
print("ip hash     :", [ip_hash(ip) for ip in ("1.1.1.1", "2.2.2.2", "1.1.1.1", "3.3.3.3", "2.2.2.2")])
```

**Output:**

```text
round robin : ['s1', 's2', 's3', 's1', 's2', 's3', 's1', 's2', 's3']
weighted    : ['s1', 's1', 's2', 's3', 's1', 's1', 's2', 's3']
ip hash     : ['s2', 's3', 's2', 's1', 's3']
```

### Which one when?

| Algorithm | How it picks | Best when | Weakness |
|---|---|---|---|
| **Round robin** | Take turns | Equal servers, short similar requests | Ignores how busy each server is |
| **Weighted round robin** | Turns proportional to capacity | Servers of different size | Static weights |
| **Least connections** | Fewest open connections | Requests of **very different length** (uploads, reports) | Needs live counts |
| **Least response time** | Fastest recent responses | Mixed performance | Needs measurement |
| **IP hash / consistent hash** | Hash of client IP or key | Need the same client to hit the same server (local cache) | Uneven if few clients; use consistent hashing so adding a server does not reshuffle all |
| **Random with two choices** | Pick 2 at random, send to the less busy | Large fleets | Slightly more logic |

### Why least connections beats round robin for uneven work

```python
import random
random.seed(5)

def simulate(strategy, requests=3000, n_servers=4):
    busy_until = [0.0] * n_servers          # when each server becomes free
    t = 0.0
    rr_i = 0
    waits = []
    for _ in range(requests):
        t += 0.02                            # a request arrives every 20 ms
        cost = random.choice([0.01, 0.01, 0.01, 0.2])   # 1 in 4 requests is slow
        if strategy == "round_robin":
            i = rr_i % n_servers; rr_i += 1
        else:                                # least busy: soonest to be free
            i = min(range(n_servers), key=lambda s: busy_until[s])
        start = max(t, busy_until[i])
        waits.append(start - t)
        busy_until[i] = start + cost
    waits.sort()
    return sum(waits) / len(waits), waits[int(len(waits) * 0.99)]

for name in ("round_robin", "least_busy"):
    avg, p99 = simulate(name)
    print(f"{name:12} average wait {avg * 1000:6.1f} ms   p99 wait {p99 * 1000:7.1f} ms")
```

**Output:**

```text
round_robin  average wait  113.9 ms   p99 wait   540.0 ms
least_busy   average wait   14.6 ms   p99 wait   200.0 ms
```

When some requests are long, round robin keeps queuing work behind a slow one. Choosing the least
busy server shortens the wait, especially the **tail (p99)**.

## Health checks

A balancer must know which servers are alive.

- **Active:** every few seconds, call `GET /health` on each server. Mark it **down after 3 failures in
  a row**, **up after 2 successes** (avoid flapping).
- **Passive:** watch real traffic. A burst of errors or timeouts ejects the server.
- **Deep vs shallow checks:** a shallow check ("process is up") misses a server whose database
  connection is broken. A deep check ("can I query the DB?") can, in turn, take **every** server out
  when the DB hiccups. Use shallow checks for liveness and be careful with dependency checks.
- **Connection draining:** when removing a server, stop new requests but let in-flight ones finish.

## Sticky sessions

Sending a user to the **same server** every time (via cookie or IP hash). Convenient if the server
keeps session data in memory, but:

- Load becomes uneven, and a dead server logs its users out.
- Scaling down is awkward.

Better: **stateless servers**, session data in Redis. Use stickiness only for performance (a warm local cache).

## Making the load balancer itself reliable

The balancer is a SPOF unless you duplicate it:

- **Active-passive pair** sharing a **floating (virtual) IP**; a heartbeat detects failure and the
  standby takes the IP (VRRP, keepalived).
- **DNS or anycast** pointing at several balancers.
- **Cloud managed balancers** (ALB, NLB, GCLB) run across zones for you.
- At very high scale: **layers**. DNS or anycast, then L4 balancers, then L7 balancers, then servers.

## Global server load balancing

Send users to the **nearest healthy region**: DNS latency or geo routing, or anycast. Combined with
health checks, it also gives **regional failover**.

## Common mistakes

:::{warning}
- Round robin for requests that vary from 5 ms to 5 s.
- One load balancer (a new SPOF).
- A health check that tests the database, so one DB blip empties the whole pool.
- Sticky sessions as the way to store logins.
:::

## Try it yourself

1. Servers have 2, 4 and 8 cores. How do you set weights for weighted round robin?
2. Your app has long file-export requests and quick API calls on the same servers. Which algorithm?
3. After a deploy all users are logged out. The servers kept sessions in memory behind sticky sessions. What is the fix?

<details class="solution"><summary>Answers</summary>

1. Weights **2 : 4 : 8** (or 1 : 2 : 4), proportional to capacity.
2. **Least connections** (or least response time), because request cost varies widely. Even better: route exports to a separate pool.
3. Move sessions to a **shared store (Redis)** or use signed tokens, so any server can serve any user and restarts lose nothing.

</details>

:::{admonition} Next
:class: important
The network side is done. Next, what clients ask servers for: [what is an API?](21-apis.md).
:::
