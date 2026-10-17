# Chapter 45 · Publish/subscribe (pub/sub)

## The big idea

In **pub/sub**, a **publisher** sends a message to a **topic** without knowing who is listening, and
**every subscriber** to that topic receives **its own copy**.

**Everyday example:** a **YouTube channel**. The creator uploads a video once (publish). Everyone who
subscribed gets a notification (subscribe). The creator does not keep a list of viewers, and viewers can
join or leave any time. Compare a **queue**, where each message goes to exactly **one** worker.

```{raw} html
:file: ../diagrams/pub-sub.html
```

## Queue vs pub/sub

| | Queue (point-to-point) | Pub/sub (fan-out) |
|---|---|---|
| Each message goes to | **One** consumer | **Every** subscriber |
| Use for | Sharing work among workers | Broadcasting an event to many systems |
| Example | "Resize this image" | "Order #42 was placed" |

A common combination: publish to a topic, and give **each subscriber its own queue** so each service
processes events at its own pace and can retry independently (SNS to SQS fan-out, RabbitMQ exchanges, Kafka
consumer groups).

## Why it matters

When an order is placed, **many things** must happen: billing, inventory, email, analytics, fraud check,
recommendations. If the order service called each one directly:

- It must know all of them (**tight coupling**).
- Adding a new consumer means **changing the order service**.
- One slow service **slows the checkout**; one down service **breaks it**.

With pub/sub the order service publishes `order.placed` once. New consumers simply subscribe. Nothing else changes.

## A tiny pub/sub broker

```python
from collections import defaultdict

class Broker:
    def __init__(self):
        self.subscribers = defaultdict(list)           # topic -> list of handler functions
    def subscribe(self, topic, handler):
        self.subscribers[topic].append(handler)
    def publish(self, topic, message):
        for handler in self.subscribers[topic]:
            handler(message)

broker = Broker()
log = []
broker.subscribe("order.placed", lambda m: log.append(f"billing  : charge {m['total']}"))
broker.subscribe("order.placed", lambda m: log.append(f"inventory: reserve {m['sku']}"))
broker.subscribe("order.placed", lambda m: log.append(f"email    : confirm to {m['user']}"))
broker.subscribe("order.cancelled", lambda m: log.append("billing  : refund"))

broker.publish("order.placed", {"user": "asha", "sku": "TEA-250", "total": 240})
print("\n".join(log))
```

**Output:**

```text
billing  : charge 240
inventory: reserve TEA-250
email    : confirm to asha
```

The publisher made **one** call and three independent systems reacted. Adding a fourth subscriber needs
no change to the publisher.

## Topics, filtering and ordering

- **Topics / channels:** named streams (`orders`, `payments`).
- **Filtering:** subscribers can match by **pattern** (`orders.*`) or by **attributes** (only EU orders).
- **Ordering:** guaranteed only **within a partition or key** in most systems.
- **Retention:** classic brokers drop messages once delivered; **logs (Kafka)** keep them so new or
  recovering subscribers can **replay** history.

## Delivery semantics and durability

- **Durable subscriptions** keep messages for a subscriber that is **offline**; non-durable ones lose them.
- **At-least-once** delivery is typical, so subscribers must be **idempotent**.
- A slow subscriber should not hold back the others, hence **one queue per subscriber**.
- **Dead-letter topics** catch poison messages.

## Real-world uses

| Use | Example |
|---|---|
| Event notification | `user.signed_up` triggers email, CRM, analytics |
| Microservices integration | Services react to each other's events instead of calling APIs |
| Real-time features | Chat rooms across WebSocket servers (Redis pub/sub) |
| Cache invalidation | Publish `product.updated`; every app server evicts its local copy |
| Streaming analytics | Clickstream to Kafka, many consumers |
| Mobile and web push | Push notification fan-out |

## Technologies

| | Notes |
|---|---|
| **Redis pub/sub** | Very fast, **no persistence**: offline subscribers miss messages |
| **Kafka** | Durable, partitioned log; consumer groups; replay; enormous throughput |
| **AWS SNS (+ SQS)** | Managed fan-out; SNS topic to many SQS queues, Lambdas, HTTP endpoints |
| **Google Pub/Sub, Azure Service Bus** | Managed, durable |
| **RabbitMQ exchanges** | Routing by topic, headers and bindings |

## Trade-offs

- **Decoupling and flexibility** vs **harder tracing**: "who reacts to this event?" is no longer visible in code.
  Use event catalogues and distributed tracing.
- **Eventual consistency:** subscribers act a bit later.
- **Schema evolution:** events are a public contract; change them compatibly (versioned schemas).
- **Duplicates and ordering** must be designed for.

## Common mistakes

:::{warning}
- Using pub/sub with no persistence (Redis) for events you cannot afford to lose.
- Putting heavy data in events instead of ids; subscribers then fetch what they need.
- Subscribers that are not idempotent.
- Changing an event's shape without versioning, breaking unknown subscribers.
:::

## Try it yourself

1. When an order is placed, which services might subscribe, and what does the order service need to know about them?
2. What is the difference between a topic with three subscribers and a queue with three workers?
3. A new analytics team wants every past order event. Which technology makes this easy, and why?

<details class="solution"><summary>Answers</summary>

1. Billing, inventory, email, analytics, fraud. The order service needs to know **nothing**: it only publishes the event.
2. Topic: all three get **every** message. Queue: each message goes to **one** worker.
3. A **log-based broker such as Kafka**: events are retained, so the new consumer can **replay from the beginning**.

</details>

:::{admonition} Next
:class: important
Databases can publish their own changes: [change data capture](46-change-data-capture.md).
:::
