# Chapter 44 · Message queues

## The big idea

A **message queue** is a **buffer between a producer and a consumer**: the producer drops a message on
the queue and moves on; a consumer picks it up and processes it **later, at its own speed**. The two sides
no longer have to be running, or fast, at the same time.

**Everyday example:** a restaurant kitchen's **order rail**. Waiters clip order slips on the rail and go
back to customers. Cooks take slips one at a time. On a busy night the rail fills up, but nobody is
turned away at the door and no cook is overwhelmed. If one cook leaves, others keep taking slips.

```{raw} html
:file: ../diagrams/queue.html
```

## Synchronous vs queue-based

Without a queue, signing up a user might do everything **inside the request**:

```text
POST /signup  ->  save user (10 ms) -> send welcome email (800 ms) -> create thumbnail (400 ms) -> reply
                  user waits about 1.2 seconds; if the email service is down, the signup FAILS
```

With a queue:

```text
POST /signup  ->  save user (10 ms) -> put "send email" and "make thumbnail" on a queue -> reply (15 ms)
                  workers do the slow parts afterwards; a down email service just delays the email
```

## Core vocabulary

- **Producer:** sends messages. **Consumer / worker:** receives and processes them.
- **Broker:** the queue server (RabbitMQ, SQS, ActiveMQ, Kafka).
- **Acknowledgement (ack):** the consumer says "done"; only then is the message removed.
- **Visibility timeout / lock:** while a consumer works, the message is hidden from others; if no ack arrives
  in time, it becomes visible again and is **redelivered**.
- **Dead-letter queue (DLQ):** a side queue for messages that keep failing, for inspection.
- **Competing consumers:** many workers share one queue; each message goes to **one** of them.

## Why use a queue

1. **Decoupling:** producer and consumer do not know each other and can be deployed separately.
2. **Smoothing bursts (load levelling):** the queue absorbs a spike; workers drain it steadily.
3. **Async work:** emails, image processing, reports, notifications, payments follow-ups.
4. **Reliability:** if a consumer crashes, the message is not lost; another picks it up.
5. **Scaling:** add workers to drain the queue faster.
6. **Rate control:** protect a slow downstream (a third-party API with a rate limit).

## A queue with acknowledgements, retries and a dead-letter queue

```python
import collections

queue = collections.deque([
    {"id": 1, "job": "email asha"},
    {"id": 2, "job": "email BAD"},      # this one always fails
    {"id": 3, "job": "email ravi"},
])
dead_letters, done, attempts = [], [], collections.Counter()
MAX_ATTEMPTS = 3

def process(msg):
    if "BAD" in msg["job"]:
        raise ValueError("smtp rejected")
    return "sent"

while queue:
    msg = queue.popleft()               # receive: the message is now "in flight"
    attempts[msg["id"]] += 1
    try:
        process(msg)
        done.append(msg["id"])          # ack: remove for good
    except ValueError:
        if attempts[msg["id"]] >= MAX_ATTEMPTS:
            dead_letters.append(msg["id"])     # give up, park for humans
        else:
            queue.append(msg)                  # no ack: it comes back for another attempt

print("processed OK  :", done)
print("dead-lettered :", dead_letters)
print("attempt counts:", dict(attempts))
```

**Output:**

```text
processed OK  : [1, 3]
dead-lettered : [2]
attempt counts: {1: 1, 2: 3, 3: 1}
```

The failing message was tried three times and then **parked** instead of blocking the others or retrying forever.

## Delivery guarantees

| Guarantee | Meaning | Risk |
|---|---|---|
| **At-most-once** | Never redelivered; may be **lost** | Lost work |
| **At-least-once** (most common) | Delivered until acked; may arrive **more than once** | Duplicates |
| **Exactly-once** | Processed once | Very hard end to end; in practice = at-least-once + **idempotent consumers** |

So: **make consumers idempotent** (see the idempotency chapter). Store processed message ids, or design the work
so repeating it is harmless.

## Ordering

- A **single queue with one consumer** preserves order, but does not scale.
- With many consumers, order is lost. If you need order **per entity** (all events of one order in sequence),
  use **partitions or message groups** keyed by that entity (Kafka partitions, SQS FIFO message group id).

## Queue vs log vs pub/sub

| | Queue (RabbitMQ, SQS) | Log / stream (Kafka) | Pub/sub |
|---|---|---|---|
| Message after consumption | Removed | **Kept** for a retention period | Delivered to all subscribers |
| Consumers | Compete for messages | Each group reads independently, can **replay** | Each subscriber gets a copy |
| Best for | Task distribution (jobs) | Event streams, analytics, audit | Fan-out notifications |

(Pub/sub and logs are covered next.)

## Back pressure

If producers outrun consumers the queue grows without limit, increasing delay and memory. Respond by:

- **Alerting on queue depth and age of the oldest message**,
- **Autoscaling workers** on queue length,
- **Bounded queues** that reject (HTTP 429/503) when full,
- **Rate limiting** the producer.

## Choosing a technology

| | Pick when |
|---|---|
| **Amazon SQS** | Simple, fully managed, scales automatically; at-least-once (FIFO option) |
| **RabbitMQ** | Rich routing, per-message acks, flexible patterns |
| **Kafka** | Very high throughput, ordered partitions, replay, event streaming |
| **Redis lists/streams** | Lightweight tasks when Redis is already there (Celery, RQ) |

## Common mistakes

:::{warning}
- Non-idempotent consumers on an at-least-once queue (duplicate emails, double charges).
- No dead-letter queue: one poison message blocks or loops forever.
- Unbounded queues with no alert on depth or age.
- Acking **before** the work is done (a crash then loses the message).
- Long processing with a short visibility timeout (the message is handled twice in parallel).
:::

## Try it yourself

1. A sign-up should send a welcome email but the email provider is flaky. How does a queue help?
2. Workers process 100 jobs/s; producers send 250 jobs/s for 10 minutes. How long is the backlog afterwards, and how many workers drain it in the same 10 minutes?
3. What should a consumer do when it receives the same message twice?

<details class="solution"><summary>Answers</summary>

1. Sign-up replies fast; the email job waits in the queue and is **retried** until it succeeds, without failing the user.
2. Backlog grows 150 jobs/s x 600 s = **90,000 jobs**, taking 900 s at 100 jobs/s. To keep up you need **250/100 = 3 workers** (the same 100/s each).
3. Detect the duplicate (store processed message ids or use naturally idempotent operations) and **skip** it, but still ack.

</details>

:::{admonition} Next
:class: important
One message, many interested parties: [publish/subscribe](45-pub-sub.md).
:::
