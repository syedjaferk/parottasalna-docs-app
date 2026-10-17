# Chapter 73 · Design a load balancer

## Concepts to review first

This design is built from earlier chapters. Skim them if any term feels new:

- [Load balancing](20-load-balancing.md)
- [Single point of failure](07-spof.md)
- [Failover](08-failover.md)
- [Heartbeats](47-heartbeats.md)
- [DNS](17-dns.md)
- [The OSI model](13-osi-model.md)
- [Proxy vs reverse proxy](18-proxy-vs-reverse-proxy.md)

## The problem

Design the **load balancer itself**: accept client connections, choose a healthy backend server for each request,
notice failures, and keep working when servers **or the balancer** fail. Think of AWS ALB/NLB, Nginx or HAProxy.

```{raw} html
:file: ../diagrams/load-balancer.html
```

## Step 1: clarify requirements

**Functional**

- Distribute requests across a **pool** of backend servers using a configurable algorithm.
- **Health checks**: stop sending traffic to unhealthy servers, resume when they recover.
- Add and remove servers **without dropping traffic** (deployments, autoscaling).
- Layer 7 extras: route by path/host, terminate TLS, optional sticky sessions.

**Non-functional:** adds well under a millisecond or two of latency; **no single point of failure**; scales to
hundreds of thousands of connections.

**Out of scope:** web application firewall rules, DDoS scrubbing internals, billing.

## Step 2: estimate

```python
import math

requests_per_day = 50_000_000
peak_factor = 3
server_rps = 500                 # one backend server at a comfortable CPU
spare = 0.3                      # headroom for failures and deploys

avg_rps = requests_per_day / 86_400
peak_rps = avg_rps * peak_factor
servers = math.ceil(peak_rps / server_rps)
servers_with_headroom = math.ceil(servers * (1 + spare))

# a balancer node comfortably forwards tens of thousands of requests per second
lb_rps_capacity = 20_000
lb_nodes = max(2, math.ceil(peak_rps / lb_rps_capacity))      # never fewer than 2 (no single point of failure)

print(f"average {avg_rps:,.0f} rps, peak {peak_rps:,.0f} rps")
print(f"backend servers: {servers}, with {int(spare * 100)}% headroom: {servers_with_headroom}")
print(f"load balancer nodes: {lb_nodes} (one active plus one standby is the minimum)")
```

**Output:**

```text
average 579 rps, peak 1,736 rps
backend servers: 4, with 30% headroom: 6
load balancer nodes: 2 (one active plus one standby is the minimum)
```

The lesson: the **balancer is rarely the limit**. The fleet behind it grows; the balancer must simply never be a
single machine.

## Step 3: Layer 4 or Layer 7?

| | **Layer 4** | **Layer 7** |
|---|---|---|
| Sees | IP address and port | The whole HTTP request |
| Can route by URL, header, cookie | No | **Yes** |
| TLS termination | No (passes bytes through) | **Yes** |
| Speed | Fastest, cheapest | Slower, more CPU |
| Use for | Databases, raw TCP, a first tier at huge scale | Web and API traffic, path routing |

A very large site often uses **both**: an L4 tier (anycast or ECMP) spreads connections across a tier of L7
balancers, which route to services.

## Step 4: the control plane (how servers join and leave)

```text
POST   /pools/web/servers      {"address": "10.0.1.11:8000", "weight": 2}    register
DELETE /pools/web/servers/{id}                                                drain, then remove
GET    /pools/web/servers                                                      list with health and connection counts
PUT    /pools/web/algorithm    {"type": "least_connections"}                   change algorithm
```

In the cloud, **autoscaling groups register and deregister instances automatically**. On removal, the balancer
performs **connection draining**: it stops sending new requests but lets in-flight requests finish (up to a timeout).

## Step 5: health checks, the heart of the design

Every few seconds the balancer calls `GET /health` on each server. To avoid flapping, use **two thresholds**:

- mark a server **down after N consecutive failures** (for example 3),
- mark it **up after M consecutive successes** (for example 2).

```python
class HealthTracker:
    def __init__(self, fall=3, rise=2):
        self.fall, self.rise = fall, rise
        self.healthy, self.fails, self.passes = True, 0, 0

    def record(self, ok):
        if ok:
            self.fails, self.passes = 0, self.passes + 1
            if not self.healthy and self.passes >= self.rise:
                self.healthy = True
        else:
            self.passes, self.fails = 0, self.fails + 1
            if self.healthy and self.fails >= self.fall:
                self.healthy = False
        return self.healthy

tracker = HealthTracker(fall=3, rise=2)
checks = [True, True, False, True, False, False, False, True, False, True, True, True]   # one blip, then a real outage, then recovery
for second, ok in enumerate(checks):
    state = tracker.record(ok)
    print(f"check {second:>2}: {'pass' if ok else 'FAIL'}  ->  server is {'healthy' if state else 'DOWN'}")
```

**Output:**

```text
check  0: pass  ->  server is healthy
check  1: pass  ->  server is healthy
check  2: FAIL  ->  server is healthy
check  3: pass  ->  server is healthy
check  4: FAIL  ->  server is healthy
check  5: FAIL  ->  server is healthy
check  6: FAIL  ->  server is DOWN
check  7: pass  ->  server is DOWN
check  8: FAIL  ->  server is DOWN
check  9: pass  ->  server is DOWN
check 10: pass  ->  server is healthy
check 11: pass  ->  server is healthy
```

The single failure at check 2 did **not** remove the server (a blip), three in a row did, and it needed **two**
successes to return. Combine this **active** checking with **passive** checking: if real requests to a server start
returning errors or timeouts, eject it immediately instead of waiting for the next probe.

## Step 6: choosing a server, with a working balancer

```python
import random

class Backend:
    def __init__(self, name, weight=1):
        self.name, self.weight, self.active, self.healthy = name, weight, 0, True

class LoadBalancer:
    def __init__(self, backends):
        self.backends = backends

    def pick(self):
        live = [b for b in self.backends if b.healthy]
        if not live:
            raise RuntimeError("503: no healthy backends")
        two = random.sample(live, min(2, len(live)))                  # power of two choices
        return min(two, key=lambda b: b.active / b.weight)          # fewer active connections per unit of weight

random.seed(2)
pool = [Backend("s1", weight=2), Backend("s2"), Backend("s3")]
lb = LoadBalancer(pool)

served = {b.name: 0 for b in pool}
for i in range(3000):
    if i == 1000:
        pool[1].healthy = False                # s2 fails (the health checker noticed)
    if i == 2000:
        pool[1].healthy = True                 # s2 recovers
    b = lb.pick()
    b.active += 1                               # request starts ...
    served[b.name] += 1
    if i % 5 == 0:                              # ... and requests finish at a steady rate
        for backend in pool:
            backend.active = max(0, backend.active - 3)
print("requests served:", served)
```

**Output:**

```text
requests served: {'s1': 1444, 's2': 574, 's3': 982}
```

Server `s1` has weight 2 so it takes the largest share; `s2` served nothing while it was marked down (it handled
only the requests before and after) and resumed when it recovered. **Power of two choices** (pick two at random, send to the less busy) is cheap and avoids the
herd effect of everyone choosing the single "least busy" server at the same instant.

Other algorithms to name: **round robin**, **weighted round robin**, **least connections**, **IP hash** and
**consistent hashing** (same client or key to the same server, for cache locality).

## Step 7: the balancer must not be a single point of failure

- An **active-passive pair** shares a **floating (virtual) IP**; a heartbeat between them (VRRP, keepalived) lets the
  standby take the IP within seconds.
- Or **active-active** balancers behind **DNS** or **anycast**, each handling a share.
- Spread them across **availability zones**. In the cloud, a managed balancer does this for you.
- Keep balancers **stateless** where you can (sticky-session tables and connection tracking are the exceptions and
  need replication or acceptable loss).

## Step 8: edge cases and trade-offs

| Question | Answer |
|---|---|
| Long-lived connections (WebSockets)? | Balance by **least connections**; expect uneven spread after a deploy; drain gracefully |
| Slow clients tying up connections? | L7 balancer buffers requests; set timeouts |
| Sticky sessions? | Use only as an optimisation; keep session data in a shared store |
| TLS cost? | Terminate at the L7 tier with session resumption; use hardware or the edge for huge scale |
| Retry storms? | Limit retries; use circuit breaking; do not retry non-idempotent requests |

| Choice | You gain | You pay |
|---|---|---|
| Layer 7 | Smart routing, TLS, observability | More latency and CPU than Layer 4 |
| Least connections | Adapts to uneven requests | Needs per-server connection counts |
| Active-passive pair | Simple failover | An idle standby; seconds of disruption |
| Passive plus active health checks | Fast and accurate failure detection | More logic and more traffic |

## Common mistakes

:::{warning}
- Round robin for requests that vary from 5 ms to 5 s.
- One load balancer (a new single point of failure).
- A health check that tests the database, so one database blip empties the entire pool.
- Removing a server without draining, which cuts users off mid-request.
- Sticky sessions as the place where logins live.
:::

## Try it yourself

1. Servers with 2, 4 and 8 cores: what weights would you set?
2. Why require several consecutive failures before marking a server down?
3. Why are two balancers better than one very powerful balancer?

<details class="solution"><summary>Answers</summary>

1. Proportional to capacity: **2 : 4 : 8** (or 1 : 2 : 4).
2. A single failed probe may be a network blip or a brief pause. Several in a row indicates a real problem and avoids flapping servers in and out of the pool.
3. A single powerful balancer is still a **single point of failure** and has a hard ceiling. Two (in different zones) survive a failure and can share the load.

</details>

:::{admonition} Try it in the playground
:class: important
Design it in [Design a Load Balancer](/system-design/load-balancer/).
:::

:::{admonition} Next
:class: important
Next case study: [Design a content delivery network (CDN)](74-design-cdn.md).
:::
