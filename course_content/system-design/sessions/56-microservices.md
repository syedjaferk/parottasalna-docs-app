# Chapter 56 · Microservices architecture

## The big idea

**Microservices** break one big application into **many small services**, each owning **one business
capability**, with **its own data**, **deployed and scaled independently**, talking to each other over the
network.

**Everyday example:** a **food court versus a single giant restaurant**. In the giant restaurant one kitchen
makes everything; if the pizza oven breaks, the whole restaurant slows down, and renovating means closing
everything. In a food court, each stall (pizza, dosa, juice) runs independently with its own staff and cash
register. One stall closing does not close the court. The price: customers now need a map, and getting a
combo meal means visiting three stalls.

```{raw} html
:file: ../diagrams/microservices.html
```

## Monolith vs microservices

| | **Monolith** | **Microservices** |
|---|---|---|
| Codebase | One | Many small ones |
| Deploy | Everything together | Each service alone |
| Scaling | Scale the whole app | Scale only the hot service |
| Data | One shared database | **Database per service** |
| Calls between parts | In-process function calls (fast, reliable) | **Network calls** (slower, can fail) |
| Technology | One stack | Each team may choose |
| Team structure | Everyone in one code base | Small teams own services |
| Failure | One bug can crash everything | Failures can be **isolated** |
| Operations | Simple | **Complex**: many things to deploy, monitor, secure |
| Transactions | Easy (one DB) | Hard: **distributed transactions** |

:::{admonition} Start with a monolith
:class: important
Microservices solve **organisational and scaling** problems of big teams and big systems. For a small team
and a young product, a **well-structured monolith** is faster to build and far simpler to run. Most successful
microservice systems began as monoliths and were split **when the pain appeared**.
:::

## Principles of a good service

1. **Single business capability** (orders, payments, catalogue), not a technical layer.
2. **Owns its data**: nobody else reads its tables. Other services use its **API or events**.
3. **Independently deployable**: a change should not require deploying others.
4. **Loosely coupled, highly cohesive**: change one thing in one place.
5. **Designed for failure**: timeouts, retries, circuit breakers, fallbacks.
6. **Observable**: logs, metrics, traces, health endpoints.

How to find boundaries: use **domain-driven design (DDD)** **bounded contexts**, or ask "which parts change
together, and which parts could be owned by a different team?" Wrong boundaries create a **distributed
monolith** (many services that must all change and deploy together: the worst of both worlds).

## Communication

- **Synchronous:** REST or gRPC. Simple, but **temporal coupling**: if B is down, A fails. Add timeouts and
  circuit breakers.
- **Asynchronous:** events and queues (see pub/sub and queues). Services are decoupled in time and can retry;
  results are **eventually consistent**.
- Prefer **async** for things that need not be answered immediately; **sync** for queries that the user is
  waiting on.

## The hard problem: data and transactions

Each service has its own database, so a business operation spanning services cannot use one ACID transaction.

### The saga pattern

A **saga** is a **sequence of local transactions**, each in one service, with a **compensating action** to undo
each step if a later step fails.

```text
Place order saga:
 1. Order service   : create order (PENDING)          compensation: cancel order
 2. Payment service : charge card                       compensation: refund
 3. Inventory       : reserve items                     compensation: release items
 4. Shipping        : schedule delivery                 compensation: cancel shipment
If step 3 fails ->  refund (undo 2)  ->  cancel order (undo 1)
```

Two styles: **choreography** (services react to each other's events, no central brain, harder to follow) and
**orchestration** (a coordinator tells each service what to do and tracks the state, easier to understand).

```python
def run_saga(steps, fail_at=None):
    """steps: list of (name, action, compensation). Runs actions; on failure runs compensations in reverse."""
    done = []
    for i, (name, action, compensation) in enumerate(steps):
        if i == fail_at:
            print(f"  step '{name}' FAILED -> compensating {len(done)} earlier step(s)")
            for done_name, comp in reversed(done):
                print(f"    undo: {done_name} -> {comp}")
            return "ROLLED BACK"
        print(f"  step '{name}': {action}")
        done.append((name, compensation))
    return "COMPLETED"

saga = [
    ("create order",   "order #9001 PENDING", "cancel order #9001"),
    ("charge card",    "charged 500",         "refund 500"),
    ("reserve stock",  "reserved 2 units",    "release 2 units"),
    ("schedule ship",  "pickup booked",       "cancel pickup"),
]
print("Happy path:");           print(" ->", run_saga(saga))
print("Stock reservation fails:"); print(" ->", run_saga(saga, fail_at=2))
```

**Output:**

```text
Happy path:
  step 'create order': order #9001 PENDING
  step 'charge card': charged 500
  step 'reserve stock': reserved 2 units
  step 'schedule ship': pickup booked
 -> COMPLETED
Stock reservation fails:
  step 'create order': order #9001 PENDING
  step 'charge card': charged 500
  step 'reserve stock' FAILED -> compensating 2 earlier step(s)
    undo: charge card -> refund 500
    undo: create order -> cancel order #9001
 -> ROLLED BACK
```

### Other data patterns

- **Database per service**, never a shared database.
- **API composition:** a gateway or BFF queries several services and merges the result.
- **CQRS:** separate write and read models; build read views from events.
- **Outbox + CDC** to publish events reliably.
- **Idempotent** operations everywhere (retries are normal).

## Supporting infrastructure you will need

| Concern | Solution |
|---|---|
| Entry point | **API gateway** |
| Finding services | **Service discovery** |
| Failures | **Circuit breakers, timeouts, retries, bulkheads** |
| Configuration | Central config and secrets management |
| Observability | **Distributed tracing**, centralised logs, metrics, dashboards |
| Deployment | **Containers and Kubernetes**, CI/CD per service |
| Security | mTLS between services, zero trust, per-service identity |
| Versioning | Backwards-compatible APIs, contract tests |

## Benefits and costs, honestly

**Benefits:** independent scaling and deployment, fault isolation, team autonomy, technology freedom,
easier to understand small codebases.

**Costs:** network latency and failure modes, distributed data consistency, much higher operational and
testing complexity, duplicated effort, debugging across services, the need for a mature DevOps culture.

A **rule of thumb**: if you cannot yet operate a monolith well (CI/CD, monitoring, on-call), you are not ready
for microservices.

## Common mistakes

:::{warning}
- Going microservices on day one for a small team.
- Services too small (nano-services) or split on technical layers instead of business capabilities.
- A **shared database** between services (hidden coupling).
- Chains of synchronous calls A -> B -> C -> D (availability multiplies down, latency adds up).
- No tracing or central logging.
- Ignoring data consistency, and expecting cross-service ACID.
:::

## Try it yourself

1. Four services in a synchronous chain each have 99.9% availability. What is the end-to-end availability, and how do you improve it?
2. An order must be placed, paid and stocked. Which pattern replaces a database transaction across services?
3. How can you recognise a "distributed monolith"?

<details class="solution"><summary>Answers</summary>

1. 0.999^4 = **99.6%**. Improve by removing synchronous dependencies (use events/queues), adding caching and fallbacks, and using circuit breakers.
2. The **saga pattern**: a sequence of local transactions with compensating actions (refund, release stock).
3. Services that must be deployed together, share a database, or where one change forces changes in many services.

</details>

:::{admonition} Next
:class: important
Going even smaller: no servers to manage at all, [serverless architecture](57-serverless-architecture.md).
:::
