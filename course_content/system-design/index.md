# System Design

System design is the skill of turning a vague idea ("build something like TinyURL") into a working plan: what it
does, how big it must be, which pieces it needs and what you give up with each choice. This course teaches it **one
concept per chapter**. Every chapter has a diagram, an everyday example, worked numbers, code you can run, common
mistakes and exercises.

:::{note}
**Two ways to learn, side by side.** Read the chapters here to learn the ideas. Then open the
**[System Design playground](/system-design/)**: the problem is on the left and a guided, question-by-question solution
is on the right. You decide first, then it shows the correct reasoning and moves you on.
:::

```{raw} html
:file: diagrams/framework.html
```

## How the course is organised

| Part | What you learn |
|---|---|
| **Foundations** | The interview routine, estimating numbers, designing APIs and data |
| **Core concepts** | Scalability, availability, reliability, failure, latency vs throughput, consistent hashing, CAP |
| **Networking** | OSI, IP, TCP vs UDP, checksums, DNS, proxies, HTTP and HTTPS, load balancing |
| **APIs** | REST vs GraphQL, gateways, WebSockets, webhooks, idempotency, rate limiting, API design |
| **Databases** | ACID, SQL vs NoSQL, indexes, sharding, replication, scaling, database types, Bloom filters, unique IDs |
| **Caching and CDN** | Caching strategies, eviction, distributed caches, CDNs |
| **Asynchronous communication** | Queues, publish/subscribe, change data capture |
| **Distributed systems** | Heartbeats, discovery, consensus, locks, gossip, circuit breakers, disaster recovery, tracing |
| **Architectural patterns** | Client-server, microservices, serverless, event-driven, peer-to-peer |
| **Trade-offs** | Eleven head-to-head comparisons you can quote in an interview |
| **Case studies** | Ten full designs that use everything above |

## How each chapter works

1. **The big idea** in plain words, with an everyday example.
2. **A picture** of the idea.
3. **How it works**, with real numbers and code you can run (the output shown is what the code printed).
4. **Common mistakes** and what interviewers look for.
5. **Try it yourself**: questions first, answers hidden until you open them.

:::{tip}
Keep a notebook. For each chapter write one line: *"I would use X when Y, and it costs Z."* That sentence is exactly
what an interviewer wants to hear.
:::

```{toctree}
:maxdepth: 1
:caption: Foundations

sessions/01-interview-framework
sessions/02-back-of-envelope
sessions/03-api-and-data-model
```

```{toctree}
:maxdepth: 1
:caption: Core concepts

sessions/04-scalability
sessions/05-availability
sessions/06-reliability
sessions/07-spof
sessions/08-failover
sessions/09-fault-tolerance
sessions/10-latency-throughput-and-bandwidth
sessions/11-consistent-hashing
sessions/12-cap-theorem
```

```{toctree}
:maxdepth: 1
:caption: Networking

sessions/13-osi-model
sessions/14-ip-addresses
sessions/15-tcp-vs-udp
sessions/16-checksums
sessions/17-dns
sessions/18-proxy-vs-reverse-proxy
sessions/19-http-and-https
sessions/20-load-balancing
```

```{toctree}
:maxdepth: 1
:caption: APIs

sessions/21-apis
sessions/22-rest-vs-graphql
sessions/23-api-gateway
sessions/24-api-design
sessions/25-websockets
sessions/26-webhooks
sessions/27-idempotency
sessions/28-rate-limiting
```

```{toctree}
:maxdepth: 1
:caption: Databases

sessions/29-acid
sessions/30-sql-vs-nosql
sessions/31-database-indexes
sessions/32-sharding
sessions/33-replication
sessions/34-database-scaling
sessions/35-database-types
sessions/36-bloom-filters
sessions/37-database-architectures
sessions/38-unique-ids
```

```{toctree}
:maxdepth: 1
:caption: Caching and CDN

sessions/39-caching-101
sessions/40-caching-strategies
sessions/41-eviction-policies
sessions/42-distributed-caching
sessions/43-cdn
```

```{toctree}
:maxdepth: 1
:caption: Asynchronous communication

sessions/44-message-queues
sessions/45-pub-sub
sessions/46-change-data-capture
```

```{toctree}
:maxdepth: 1
:caption: Distributed systems

sessions/47-heartbeats
sessions/48-service-discovery
sessions/49-consensus
sessions/50-distributed-locking
sessions/51-gossip-protocol
sessions/52-circuit-breaker
sessions/53-disaster-recovery
sessions/54-distributed-tracing
```

```{toctree}
:maxdepth: 1
:caption: Architectural patterns

sessions/55-client-server-architecture
sessions/56-microservices
sessions/57-serverless-architecture
sessions/58-event-driven-architecture
sessions/59-peer-to-peer-architecture
```

```{toctree}
:maxdepth: 1
:caption: System design trade-offs

sessions/60-top-system-design-tradeoffs
sessions/61-vertical-vs-horizontal-scaling
sessions/62-concurrency-vs-parallelism
sessions/63-long-polling-vs-websockets
sessions/64-batch-vs-stream-processing
sessions/65-stateful-vs-stateless-architecture
sessions/66-strong-vs-eventual-consistency
sessions/67-read-through-vs-write-through-cache
sessions/68-push-vs-pull-architecture
sessions/69-rest-vs-rpc
sessions/70-sync-vs-async-communication
```

```{toctree}
:maxdepth: 1
:caption: Case studies

sessions/71-design-url-shortener
sessions/72-design-autocomplete
sessions/73-design-load-balancer
sessions/74-design-cdn
sessions/75-design-parking-garage
sessions/76-design-vending-machine
sessions/77-design-key-value-store
sessions/78-design-distributed-cache
sessions/79-design-authentication-system
sessions/80-design-upi-payments
```
