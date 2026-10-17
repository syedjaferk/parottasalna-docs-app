# Chapter 12 · Design a load balancer

## The problem

Design the load balancer itself: accept client connections, pick a healthy backend server for each
request, and keep going when servers (or the balancer) fail.

```{raw} html
:file: ../diagrams/load-balancer.html
```

## Requirements

- Distribute traffic across a pool of servers; add and remove servers without downtime.
- Detect unhealthy servers and stop using them (**health checks**).
- Very low added latency, very high availability, no single point of failure.
- Optional: TLS termination, sticky sessions, rate limiting.

## Layer 4 or Layer 7?

| | L4 | L7 |
|---|---|---|
| Looks at | IP and port | HTTP path, headers, cookies |
| Speed | Fastest | Slower, more flexible |
| Use | Databases, raw TCP, very high traffic | Routing `/api` and `/images` to different pools, TLS |

## Algorithms

- **Round robin:** simple, assumes equal servers and requests.
- **Weighted round robin:** bigger servers take more.
- **Least connections:** good when request durations vary.
- **IP hash / consistent hashing:** same client or key goes to the same server (useful for caches).
- **Power of two choices:** pick two random servers, send to the less busy. Cheap and surprisingly good.

## Health checks

- **Active:** the balancer pings `/health` every few seconds. Mark a server down after N failures, up
  again after M successes (avoid flapping).
- **Passive:** watch real traffic; a burst of 5xx errors ejects the server.
- **Connection draining:** when removing a server, let in-flight requests finish.

## Making the balancer itself reliable

- Run an **active-passive pair** sharing a floating IP, or **active-active** behind DNS or anycast.
- Standby watches a **heartbeat**; on silence it takes over the IP.
- In the cloud this is a managed service (ALB, NLB) spread over zones.

## Scaling the balancer

One balancer handles tens of thousands of connections. Beyond that: a tier of L4 balancers (ECMP or
anycast) in front of a tier of L7 balancers in front of servers.

## Common mistakes

- "Round robin" for everything, with no mention of long-lived connections.
- Forgetting that the balancer is a single point of failure.
- No health-check design, or sticky sessions that make scaling down hard.

:::{admonition} Try it in the playground
:class: important
Design it in [Design a Load Balancer](/system-design/load-balancer/).
:::
