# Chapter 48 · Service discovery

## The big idea

In a system of many services whose instances **start, stop and move constantly**, a client cannot have an
address hard-coded. **Service discovery** is how a service finds **where another service is running right
now**.

**Everyday example:** a **phone directory that updates itself**. A taxi company has 200 cabs that come
and go all day. You do not memorise cab numbers; you call the dispatcher, who knows which cabs are
available and gives you one.

```{raw} html
:file: ../diagrams/service-discovery.html
```

## The problem

In the cloud, the order service might have 5 instances today and 12 tomorrow. IP addresses change on every
deploy, restart or autoscale event. A config file with `10.0.1.17:8000` becomes wrong within minutes.

## The pieces

1. **Service registry:** a database of `service name -> list of healthy instances (ip:port)`.
2. **Registration:** how instances get into the registry.
   - **Self-registration:** each instance registers itself on start and sends **heartbeats**; it is removed
     when heartbeats stop (Eureka, Consul agents).
   - **Third-party registration:** the platform registers instances (Kubernetes, ECS) for you.
3. **Health checking:** unhealthy instances are removed (see heartbeats).
4. **Discovery:** how a client **looks up** an instance.

## Two ways to discover

### Client-side discovery

The **client** asks the registry for the instance list and **chooses one** (round robin, least loaded)
itself.

- **Pro:** no extra hop; the client can use smart routing.
- **Con:** every client needs discovery and load-balancing logic in every language; couples clients to
  the registry. (Netflix Eureka + Ribbon.)

### Server-side discovery

The client calls a **fixed address** (a load balancer or router); **it** queries the registry and forwards.

- **Pro:** clients stay simple; one place to change logic.
- **Con:** an extra hop; the router must be highly available. (AWS ALB with target groups, Kubernetes
  Services, Nginx + Consul-template.)

| | Client-side | Server-side |
|---|---|---|
| Who picks the instance | The client | A router / load balancer |
| Extra network hop | No | Yes |
| Client complexity | High | Low |
| Typical stack | Eureka, gRPC with a resolver, Consul | Kubernetes Service, ALB, Envoy |

## DNS-based discovery

Register services in **DNS** (`orders.internal` resolves to several IPs). Simple and universal. Weaknesses:
DNS caching (stale answers after a TTL), clients that resolve once and cache forever, and no health-aware
load balancing by default. Kubernetes solves much of this with **Service** virtual IPs and CoreDNS.

## A working registry

```python
import time

class Registry:
    def __init__(self, ttl=3.0):
        self.ttl = ttl
        self.instances = {}                       # service -> {address: last_heartbeat_time}

    def register(self, service, address, now):
        self.instances.setdefault(service, {})[address] = now

    heartbeat = register                          # a heartbeat just refreshes the timestamp

    def lookup(self, service, now):
        alive = [a for a, t in self.instances.get(service, {}).items() if now - t <= self.ttl]
        return sorted(alive)

reg = Registry(ttl=3.0)
reg.register("orders", "10.0.1.11:8000", now=0)
reg.register("orders", "10.0.1.12:8000", now=0)
reg.register("orders", "10.0.1.13:8000", now=0)
print("t=1 lookup:", reg.lookup("orders", now=1))

reg.heartbeat("orders", "10.0.1.11:8000", now=2)
reg.heartbeat("orders", "10.0.1.12:8000", now=2)       # .13 stopped sending heartbeats (it crashed)
print("t=4 lookup:", reg.lookup("orders", now=4), "<- 10.0.1.13 expired")

reg.register("orders", "10.0.1.14:8000", now=5)         # autoscaling adds a new instance
print("t=5 lookup:", reg.lookup("orders", now=5))
```

**Output:**

```text
t=1 lookup: ['10.0.1.11:8000', '10.0.1.12:8000', '10.0.1.13:8000']
t=4 lookup: ['10.0.1.11:8000', '10.0.1.12:8000'] <- 10.0.1.13 expired
t=5 lookup: ['10.0.1.11:8000', '10.0.1.12:8000', '10.0.1.14:8000']
```

Instances appear and disappear without anyone editing a config file.

## Technologies

| Tool | Notes |
|---|---|
| **Consul** | Registry + health checks + key/value; DNS and HTTP interfaces |
| **etcd / ZooKeeper** | Strongly consistent stores that discovery systems build on |
| **Eureka** | Netflix's AP registry for client-side discovery |
| **Kubernetes Services + CoreDNS** | Built in: stable name and virtual IP over changing pods |
| **Envoy / Istio (service mesh)** | Sidecar proxies discover and load-balance for you |
| **AWS Cloud Map, ECS service discovery** | Managed |

## Design questions

- **Consistency of the registry:** CP (etcd, Consul) never returns a wrong set but may be unavailable in a
  partition; AP (Eureka) always answers, possibly **stale**. For discovery, **availability usually wins**:
  a slightly stale list is better than none, and clients **retry** another instance when a connection fails.
- **Caching on the client** with a short TTL so the registry is not hit per request, and a **fallback to the
  last known list** if the registry is down.
- **Self-preservation:** during a mass network failure do not delete everything (Eureka stops expiring
  instances if too many vanish at once, assuming the network, not the servers, is at fault).

## Common mistakes

:::{warning}
- Hard-coding IPs.
- Relying on DNS with a long TTL for fast-changing instances.
- No health checks, so traffic goes to dead instances.
- The registry itself being a SPOF (run it as a cluster).
- Clients with no retry or fallback when the chosen instance is down.
:::

## Try it yourself

1. Compare client-side and server-side discovery in one sentence each.
2. An instance crashes without deregistering. How does the registry notice?
3. Why might a discovery system prefer availability over consistency?

<details class="solution"><summary>Answers</summary>

1. Client-side: the client looks up the instance list and picks one. Server-side: the client calls a router that does the lookup and forwards.
2. Its **heartbeats stop**; after the TTL the registry marks it expired and removes it from lookups.
3. A stale list of instances is still mostly right (clients retry on failure), whereas an unavailable registry would stop every service from finding any other.

</details>

:::{admonition} Next
:class: important
When nodes must **agree** on something (who is leader), you need [consensus algorithms](49-consensus.md).
:::
