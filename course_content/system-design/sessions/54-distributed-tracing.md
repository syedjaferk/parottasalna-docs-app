# Chapter 54 · Distributed tracing

## The big idea

**Distributed tracing** follows **one request through every service** it touches, recording how long each step
took, so you can see **where the time went and where it failed**.

**Everyday example:** a **courier tracking number**. A parcel passes through five depots. The tracking page
shows each stop with a timestamp, so when it arrives late you can see "stuck 18 hours at the Pune hub".
Without tracking you only know it is late somewhere.

```{raw} html
:file: ../diagrams/distributed-tracing.html
```

## The problem

A user clicks "Checkout" and it takes 6 seconds. The request went through: gateway, auth, cart, pricing,
inventory, payments, and a database for each. Logs on each machine show only that machine's view, in different
files, with different clocks. Which service was slow? Which call failed? **Logs and metrics alone cannot
answer "what happened to *this* request".**

## The three pillars of observability

| Pillar | Answers | Example |
|---|---|---|
| **Metrics** | "What is happening overall?" | Error rate 5%, p99 latency 2 s |
| **Logs** | "What did this component say?" | `payment declined: card expired` |
| **Traces** | "What path did *one request* take and where did the time go?" | Checkout took 6 s, 4.8 s inside the pricing DB call |

Use them together: metrics tell you something is wrong, traces tell you **where**, logs tell you **why**.

## The vocabulary

- **Trace:** the whole journey of one request, identified by a **trace id**.
- **Span:** one **unit of work** within the trace (an HTTP call, a DB query), with start time, duration,
  name, tags and a **parent span id**. Spans form a tree.
- **Context propagation:** passing the trace id (and current span id) from service to service so spans can be
  stitched together. It travels in **request headers**.
- **Sampling:** recording only a fraction of traces (1%, or all errors and slow ones) to control cost.

The standard header is **W3C `traceparent`**:

```text
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
             ver  trace-id (32 hex)                span-id (16 hex)  flags (sampled)
```

## Spans in code

```python
import itertools

counter = itertools.count(1)
spans = []

class Span:
    def __init__(self, name, trace_id, parent=None, start=0.0):
        self.id, self.name, self.trace_id, self.parent, self.start = next(counter), name, trace_id, parent, start
        self.end = None
        spans.append(self)

def simulate_checkout():
    trace_id = "trace-42"                                  # created at the entry point, passed on in headers
    t = 0.0
    root = Span("gateway: POST /checkout", trace_id, None, t)

    cart = Span("cart-service: load cart", trace_id, root.id, t + 0.01); cart.end = t + 0.05
    price = Span("pricing-service: price items", trace_id, root.id, t + 0.05)
    db = Span("pricing-db: SELECT prices", trace_id, price.id, t + 0.06); db.end = t + 1.10     # the slow part
    price.end = t + 1.15
    pay = Span("payment-service: charge card", trace_id, root.id, t + 1.15)
    gw = Span("bank-api: authorise", trace_id, pay.id, t + 1.20); gw.end = t + 1.50
    pay.end = t + 1.55
    root.end = t + 1.60

simulate_checkout()
by_id = {s.id: s for s in spans}

def depth(span):
    d = 0
    while span.parent:
        span = by_id[span.parent]; d += 1
    return d

total = spans[0].end - spans[0].start
for s in spans:
    dur = s.end - s.start
    bar = "#" * max(1, int(dur / total * 30))
    print(f"{'  ' * depth(s)}{s.name:<34} {dur * 1000:6.0f} ms  {bar}")

slowest = max(spans[1:], key=lambda s: (s.end - s.start) - sum((c.end - c.start) for c in spans if c.parent == s.id))
print("\nbiggest own time (excluding children):", slowest.name)
```

**Output:**

```text
gateway: POST /checkout              1600 ms  ##############################
  cart-service: load cart                40 ms  #
  pricing-service: price items         1100 ms  ####################
    pricing-db: SELECT prices            1040 ms  ###################
  payment-service: charge card          400 ms  #######
    bank-api: authorise                   300 ms  #####

biggest own time (excluding children): pricing-db: SELECT prices
```

The waterfall makes the culprit obvious: one pricing database query (about 1.04 s) is two thirds of the
request. Logs on five machines would have taken an hour to piece together.

## How tracing works end to end

1. The **first service** (gateway) creates a **trace id** and a root span.
2. Every outgoing call carries `traceparent` (HTTP header, gRPC metadata, message headers on queues).
3. Each service creates **child spans** with the received parent id, and sends finished spans to a **collector**
   (usually asynchronously, in batches, so tracing never slows requests).
4. The backend **stores and indexes** spans by trace id; the UI draws the **waterfall** and service map.

**Instrumentation** is mostly automatic: an agent or library wraps HTTP clients, web frameworks, database
drivers and message consumers. You add manual spans for important business steps.

## Tools

| Tool | Notes |
|---|---|
| **OpenTelemetry (OTel)** | The **open standard** for traces, metrics and logs: SDKs, collector, no vendor lock-in |
| **Jaeger, Zipkin, Tempo** | Open-source tracing backends |
| **Datadog, New Relic, Honeycomb, AWS X-Ray, Cloud Trace** | Managed |
| **Service meshes (Istio/Envoy)** | Generate spans at the proxy |

Dapper (Google, 2010) was the paper that started all of this.

## Sampling

Tracing everything at 50,000 requests per second is expensive. Strategies:

- **Head-based:** decide at the start (sample 1%). Cheap, but may miss the rare slow or failed request.
- **Tail-based:** buffer a whole trace and keep it **only if it was slow or had an error**. Smarter, needs more
  infrastructure.
- **Always sample errors and slow requests**, sample the rest.

## Making traces useful

- Put the **trace id in every log line** so you can jump from a trace to its logs (and back).
- Return the trace id to the user in error pages (`request id: 4bf92f35...`) so support can find it.
- Tag spans with useful attributes: `user.id` (hashed), `http.status_code`, `db.statement` (without
  secrets), `cache.hit`.
- Propagate context across **async boundaries** too (queues, background jobs), or traces break into pieces.

## Common mistakes

:::{warning}
- Not propagating the context through one service (the trace splits in two).
- Missing queues and thread pools: context is lost when work moves to another thread or message.
- Sampling away exactly the slow and failing requests you need.
- Putting passwords, tokens or personal data in span attributes.
- Collecting traces but never putting the trace id in logs.
:::

## Try it yourself

1. In the waterfall above, which service should you investigate first, and why?
2. What is the difference between a trace and a span?
3. Why must tracing data be sent asynchronously and sampled?

<details class="solution"><summary>Answers</summary>

1. The **pricing service / its database**: its own query dominates the request time.
2. A **trace** is the whole request journey; a **span** is one timed operation in it. Spans form a tree under one trace id.
3. Synchronous sending would add latency to every request and an outage of the tracing system would hurt the product. Full capture of every request is expensive in storage and bandwidth.

</details>

:::{admonition} Next
:class: important
Time to look at how entire systems are *shaped*. Start with the oldest pattern: [client-server architecture](55-client-server-architecture.md).
:::
