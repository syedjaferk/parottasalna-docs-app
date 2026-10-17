# Chapter 9 · Queues, rate limiting and resilience

## The big idea

Not everything has to happen **while the user waits**. Put slow work on a queue, protect your system
from floods, and make failure a normal event the system survives.

**Everyday example:** a restaurant kitchen. The waiter drops the order slip on a rail and goes back
to the customers. Cooks pick slips at their own pace. If slips pile up, the manager stops taking
new orders for a while.

```{raw} html
:file: ../diagrams/queue.html
```

## Message queues and task queues

- A **queue** holds messages until a consumer takes one. Examples: SQS, RabbitMQ.
- A **log / stream** (Kafka) keeps messages in order and lets many consumers replay them.
- **Pub/sub:** one message goes to many subscribers (a new order notifies billing, email and stock).
- Delivery: **at-most-once** (may lose), **at-least-once** (may repeat, the usual choice), and
  *effectively-once* (at-least-once plus idempotent consumers).

## Idempotency

An operation is **idempotent** if doing it twice has the same effect as once. Because networks
retry, every write that moves money or stock needs an **idempotency key**: the server stores the key
with the result and returns the stored result if it sees the key again.

## Back pressure

If producers are faster than consumers, a queue grows without limit. **Back pressure** slows or
rejects producers (HTTP 429/503, bounded queues) so the system degrades gracefully instead of
falling over.

## Rate limiting

Protect the service from abuse and accidents. Common algorithms:

| Algorithm | Idea | Note |
|---|---|---|
| Fixed window | N requests per minute | Bursts at the window edge |
| Sliding window | Count the last 60 seconds | Smoother, a bit more memory |
| Token bucket | Tokens refill steadily, a request spends one | Allows short bursts. A common default |

Keep counters in a shared store such as Redis so all servers agree.

## Resilience patterns

- **Timeouts:** never wait forever for a dependency.
- **Retries with exponential backoff and jitter:** wait 1s, 2s, 4s plus random noise, so clients do
  not all retry together.
- **Circuit breaker:** after too many failures, stop calling the sick service for a while and use a
  fallback. Prevents one slow service from taking down everyone.
- **Bulkheads:** separate thread pools or instances so one failure cannot use every resource.
- **Health checks and heartbeats:** notice dead nodes quickly.
- **Graceful degradation:** serve cached or partial results instead of an error page.

## Common mistakes

- Retrying forever, which turns an outage into a bigger outage.
- Non-idempotent consumers on an at-least-once queue.
- An unbounded queue.
- No dead-letter queue for messages that keep failing.

:::{admonition} Try it in the playground
:class: important
The [UPI payments](/system-design/upi/) problem depends on idempotency keys and safe retries.
:::
