# Chapter 70 · Synchronous vs asynchronous communication

## The big idea

- **Synchronous:** the caller **sends a request and waits** for the answer before doing anything else.
- **Asynchronous:** the caller **sends a message and carries on**; the answer (if any) comes **later**, through a
  different path.

**Everyday example:** a **phone call versus a text message**. A phone call is synchronous: both people must be
available at the same moment, and you cannot do other things while on the line. A text message is asynchronous:
you send it and go about your day; the other person replies when they can, even hours later, and the message
waits safely in the meantime.

```{raw} html
:file: ../diagrams/sync-vs-async.html
```

## Side by side

| | **Synchronous** | **Asynchronous** |
|---|---|---|
| Caller | **Blocks** until the response | Continues immediately |
| Both sides up at the same time? | **Yes** (temporal coupling) | **No**: a queue or log sits between them |
| Result | Immediate | **Eventual** (poll, callback, event, notification) |
| Failure of the callee | **Directly affects the caller** | Absorbed: message waits, retried later |
| Latency seen by the user | Sum of all calls in the chain | Fast response, slow work happens in the background |
| Error handling | Simple (the error comes back) | Complex (retries, dead-letter queues, compensation) |
| Debugging | Easy to trace one request | Needs correlation ids and distributed tracing |
| Load handling | A spike hits the callee directly | **Queue absorbs** the spike |
| Typical tech | HTTP/REST, gRPC, SQL | Message queues, Kafka, pub/sub, webhooks, async/await events |

## The cost of synchronous chains

Each synchronous hop **adds its latency** and **multiplies the failure chances**.

```python
def sync_chain(latencies_ms, availabilities):
    total_latency = sum(latencies_ms)
    availability = 1.0
    for a in availabilities:
        availability *= a
    return total_latency, availability

services = {
    "gateway": (10, 0.9999),
    "order":   (40, 0.999),
    "payment": (300, 0.999),
    "email":   (800, 0.995),      # slow and flaky third party
    "inventory": (30, 0.999),
}

# 1. everything synchronous
lat, avail = sync_chain([v[0] for v in services.values()], [v[1] for v in services.values()])
print(f"all synchronous : user waits {lat:>5} ms, request succeeds {avail:.2%} of the time")

# 2. email moved to a queue: only gateway, order, payment, inventory are on the user's path
critical = {k: v for k, v in services.items() if k != "email"}
lat, avail = sync_chain([v[0] for v in critical.values()], [v[1] for v in critical.values()])
print(f"email via queue : user waits {lat:>5} ms, request succeeds {avail:.2%} of the time")
print("the email is still sent, a little later, and retried if the provider fails")
```

**Output:**

```text
all synchronous : user waits  1180 ms, request succeeds 99.19% of the time
email via queue : user waits   380 ms, request succeeds 99.69% of the time
the email is still sent, a little later, and retried if the provider fails
```

Moving one slow, flaky, non-essential step to a queue cut the wait by more than half and removed a failure cause
from the user's request.

## Ways to be asynchronous

1. **Fire and forget:** publish a message; nobody waits (log an analytics event).
2. **Request, then poll:** return `202 Accepted` with a **job id**; the client polls `GET /jobs/{id}` (or receives
   a callback).
3. **Callbacks / webhooks:** the server calls the client back when done.
4. **Events:** publish "OrderPlaced" and let consumers react (event-driven).
5. **Async/await in code:** concurrency within a process (see concurrency vs parallelism). A call may be
   non-blocking in code yet still a synchronous request/response over the network.

```python
import asyncio

async def export_report(job_id, jobs):
    jobs[job_id] = "running"
    await asyncio.sleep(0.2)                       # pretend the heavy work takes a while
    jobs[job_id] = "done"

async def main():
    jobs = {}
    # the API call returns immediately with a job id ("202 Accepted")...
    task = asyncio.create_task(export_report("job-7", jobs))
    print("API replied instantly: 202 Accepted, job id = job-7")
    await asyncio.sleep(0.05)
    print("client polls:", jobs["job-7"])
    await task
    print("client polls:", jobs["job-7"])

asyncio.run(main())
```

**Output:**

```text
API replied instantly: 202 Accepted, job id = job-7
client polls: running
client polls: done
```

The caller was never blocked by the 0.2-second job. The same shape is used for video encoding, report exports and
bulk imports.

## Choosing

| Use **synchronous** when | Use **asynchronous** when |
|---|---|
| The caller **needs the result to continue** (login check, price lookup, "is the username free?") | The work is **slow** (video, report, ML) |
| The operation is fast and the callee is reliable | The result is **not needed right now** (email, notification, analytics) |
| You need a simple, easy-to-debug flow | The callee may be **down or slow**, or traffic is **spiky** |
| Strong consistency is required | You want to **decouple** teams and services |
| | **Fan-out** to many consumers |

A good rule: keep the **critical user path synchronous and short**, and push everything else (emails, search
indexing, analytics, cache warming, recommendations) to **asynchronous** channels.

## What asynchronous demands from you

- **Idempotent consumers** (messages can arrive more than once).
- **Retries with backoff** and **dead-letter queues**.
- **Ordering** strategy (partition by key).
- **Eventual consistency** in the UI: show "processing...", use optimistic updates, notify on completion.
- **Observability:** correlation ids, queue depth and age alarms, distributed tracing.
- **Back pressure:** bounded queues and autoscaled consumers.
- **Timeouts for the polling side** and a way to **cancel**.

## A hybrid in practice: checkout

```text
POST /checkout                                    (synchronous, must succeed or fail clearly)
  1. validate cart, reserve stock                 sync
  2. charge the card                              sync, with timeout + idempotency key
  3. save order                                   sync
  -> respond 201 "order placed"                   user sees success in ~400 ms
  then asynchronously, via events:
  - send confirmation email       - update search index      - notify warehouse
  - update recommendations        - emit analytics           - loyalty points
```

## Common mistakes

:::{warning}
- Long chains of synchronous calls (latency adds, availability multiplies).
- Using a queue for something the user needs **now** and then faking it with polling.
- Async without idempotency, so retries create duplicates.
- No monitoring of queue depth and age, so backlogs go unnoticed.
- Calling a sync API "async" because the **code** uses `await`: the user is still waiting.
:::

## Try it yourself

1. Which should be sync, which async: check password, send welcome email, charge card, generate a yearly report, update the search index?
2. Four services in a synchronous chain, each 99.9% available and 100 ms. What are the user-visible availability and latency?
3. An export takes 3 minutes. How should the API behave?

<details class="solution"><summary>Answers</summary>

1. Sync: check password, charge card. Async: welcome email, yearly report, search index update.
2. Availability 0.999^4 = **99.6%**; latency about **400 ms** (the sum). Move non-essential calls off the path.
3. Return **`202 Accepted` with a job id** immediately; process in the background; let the client **poll** the job status or receive a **webhook/notification**.

</details>

:::{admonition} Next
:class: important
You now have the whole toolbox. Use it on real designs in the case studies, beginning with [the URL shortener](71-design-url-shortener.md), and build each one step by step in the [System Design playground](/system-design/).
:::
