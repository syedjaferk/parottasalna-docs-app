# Chapter 58 · Event-driven architecture

## The big idea

In an **event-driven architecture (EDA)**, components communicate by **publishing events** ("an order was
placed") that other components **react** to, instead of calling each other directly and waiting for answers.

**Everyday example:** a **railway station announcement**. The station does not phone every passenger. It
announces "Platform 3: the 6:15 to Chennai is arriving". Passengers who care react (walk to platform 3). Cab
drivers react differently. The announcer does not know or care who is listening.

```{raw} html
:file: ../diagrams/event-driven.html
```

## Events, commands and queries

- **Event:** a **fact that already happened**, in the past tense: `OrderPlaced`, `PaymentFailed`. It cannot be
  rejected, only reacted to.
- **Command:** a **request to do something**: `PlaceOrder`. It can be refused. Addressed to one handler.
- **Query:** a **request for information**.

Name events as facts (`OrderPlaced`, not `PlaceOrder`) and make them carry enough data for consumers to act:

```json
{
  "type": "OrderPlaced",
  "id": "evt_8f2a",
  "occurred_at": "2024-06-10T12:01:22Z",
  "version": 1,
  "data": { "order_id": 9001, "customer_id": 17, "total": 500, "items": [{"sku": "TEA-250", "qty": 2}] }
}
```

## The parts

1. **Event producers:** emit events when something happens.
2. **Event broker / bus / log:** transports events (Kafka, RabbitMQ, SNS/SQS, EventBridge).
3. **Event consumers:** react; they may emit new events.

## Compared with request/response

| | Request/response | Event-driven |
|---|---|---|
| Caller waits for the answer | **Yes** | No |
| Producer knows the consumers | **Yes** (calls them) | **No** |
| Adding a new reaction | Change the caller | Add a subscriber |
| Coupling in time | Tight: both must be up | Loose: consumers can be down and catch up |
| Result of the whole workflow | Immediate | **Eventual** |
| Following the flow | Easy | Harder: needs tracing |

## A small event-driven system

```python
from collections import defaultdict

handlers = defaultdict(list)
def on(event_type):
    def register(fn):
        handlers[event_type].append(fn); return fn
    return register

def emit(event_type, **data):
    print(f"EVENT {event_type} {data}")
    for fn in handlers[event_type]:
        fn(data)

stock = {"TEA-250": 5}

@on("OrderPlaced")
def reserve_stock(e):
    if stock[e["sku"]] >= e["qty"]:
        stock[e["sku"]] -= e["qty"]
        emit("StockReserved", order=e["order"], sku=e["sku"])
    else:
        emit("StockRejected", order=e["order"])

@on("StockReserved")
def charge_card(e):
    emit("PaymentTaken", order=e["order"])

@on("PaymentTaken")
def ship_and_notify(e):
    print(f"   shipping order {e['order']} and emailing the customer")

@on("StockRejected")
def apologise(e):
    print(f"   apology email for order {e['order']}")

emit("OrderPlaced", order=1, sku="TEA-250", qty=2)
print()
emit("OrderPlaced", order=2, sku="TEA-250", qty=9)
print("stock left:", stock)
```

**Output:**

```text
EVENT OrderPlaced {'order': 1, 'sku': 'TEA-250', 'qty': 2}
EVENT StockReserved {'order': 1, 'sku': 'TEA-250'}
EVENT PaymentTaken {'order': 1}
   shipping order 1 and emailing the customer

EVENT OrderPlaced {'order': 2, 'sku': 'TEA-250', 'qty': 9}
EVENT StockRejected {'order': 2}
   apology email for order 2
stock left: {'TEA-250': 3}
```

No service called another: each reacted to an event and emitted the next. Order 2 followed a different path
without anyone writing an `if` that spans services.

## Patterns inside EDA

### Event notification

A small event says "something happened" (just ids); consumers call back for details if needed. Loose coupling,
extra calls.

### Event-carried state transfer

The event carries **all the data** consumers need, so they keep a **local copy** and never call the producer.
Faster and more resilient, but more data duplicated and **eventually consistent**.

### Event sourcing

Instead of storing **current state**, store the **sequence of events** that led to it. State is rebuilt by
replaying events. Benefits: a perfect **audit log**, "time travel", easy to build new views. Costs:
complexity, event schema evolution, slower rebuilds (use **snapshots**).

```python
# Event sourcing: the account balance is not stored, it is derived from events
events = [("deposited", 500), ("withdrew", 120), ("deposited", 50), ("withdrew", 200)]

def balance_after(events):
    total = 0
    for kind, amount in events:
        total += amount if kind == "deposited" else -amount
    return total

print("balance now          :", balance_after(events))
print("balance after event 2:", balance_after(events[:2]), "(time travel for free)")
```

**Output:**

```text
balance now          : 230
balance after event 2: 380 (time travel for free)
```

### CQRS (Command Query Responsibility Segregation)

Use **different models for writing and reading**: commands update the write model and emit events; events
build **read-optimised views** (a search index, a denormalised table). Reads scale independently.

### Saga

Coordinating a long business process across services with events and compensating actions (see
microservices).

## Challenges (and answers)

| Challenge | Answer |
|---|---|
| **Duplicates** (at-least-once delivery) | **Idempotent consumers**, event ids |
| **Ordering** | Partition by key (all events of one order go to one partition) |
| **Lost events when publishing** | **Outbox pattern** / CDC |
| **Eventual consistency** | Design the UI for "pending", show optimistic updates |
| **Hard to follow the flow** | **Distributed tracing**, correlation ids, an event catalogue |
| **Schema evolution** | Versioned events, schema registry, backward-compatible changes |
| **Poison messages** | Retries with limits, **dead-letter queues** |
| **Testing** | Contract tests, replaying recorded events |

## When to use it

**Good fit:** many things must happen when something occurs; systems owned by different teams; high
fan-out; spiky load; audit and analytics; workflows that can be asynchronous.

**Poor fit:** simple CRUD apps; operations needing an **immediate, strongly consistent** answer ("is this
username free right now?"); small teams who cannot yet operate a broker.

## Common mistakes

:::{warning}
- Events that are really **commands in disguise** ("PleaseSendEmail"), recreating tight coupling.
- Huge events with every field, making the schema an unmanageable public contract.
- No idempotency or ordering strategy.
- A hidden web of reactions nobody can draw (document the event flows).
- Using events where a simple synchronous call is clearer.
:::

## Try it yourself

1. Rename these as proper events: `ChargeCard`, `SendWelcomeEmail`, `ReserveStock`.
2. Why does event-carried state transfer make a consumer more resilient, and what does it cost?
3. In the code above, how would you add a loyalty-points feature without touching existing handlers?

<details class="solution"><summary>Answers</summary>

1. `PaymentRequested`/`CardCharged`, `UserRegistered`, `StockReserved` (past-tense facts, not instructions).
2. The consumer keeps its own copy so it works even if the producer is down. Cost: duplicated data that is **eventually consistent** and must be kept up to date.
3. Add a new handler: `@on("PaymentTaken") def award_points(e): ...`. Nothing else changes.

</details>

:::{admonition} Next
:class: important
Architectures with no centre at all: [peer-to-peer](59-peer-to-peer-architecture.md).
:::
