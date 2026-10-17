# Chapter 27 · Idempotency

## The big idea

An operation is **idempotent** if doing it **many times has the same effect as doing it once**.

**Everyday example:** pressing the **lift call button** five times does not call five lifts: it is
idempotent. Pressing a **"+1" counter button** five times adds five: it is **not** idempotent.
Setting a thermostat to 22 C is idempotent. "Increase the temperature by 1 degree" is not.

```{raw} html
:file: ../diagrams/idempotency.html
```

## Why it matters: networks lie

You send "charge Rs 500" and the connection drops. **Did it happen?** You cannot know: the request may
have been lost before reaching the server, or the **reply** may have been lost after the charge.
The only safe thing is to **retry**. If the operation is not idempotent, retrying may **charge twice**.

```text
client --charge 500--> server       (server charges, reply is lost)
client   ...timeout...
client --charge 500--> server       (retry!)   -> customer charged Rs 1,000
```

This also applies to queue consumers (at-least-once delivery), webhooks, mobile apps on flaky
networks, and users double-tapping a button.

## Which operations are naturally idempotent?

| Operation | Idempotent? | Why |
|---|---|---|
| `GET` read | Yes | Changes nothing |
| `PUT /users/7 {name: "Asha"}` | Yes | Setting a value to a value |
| `DELETE /orders/9` | Yes (the end state is the same) | Already gone is fine |
| `POST /orders` | **No** | Creates a new order each time |
| `balance = balance + 100` | **No** | Applied twice gives +200 |
| `balance = 600` | Yes | Absolute, not relative |

Tip: prefer **absolute** updates ("set to") over **relative** ones ("add") where you can.

## The standard solution: idempotency keys

The client generates a **unique key** per logical operation (a UUID) and sends it with the request.
The server stores `key -> result`. If the same key arrives again, it **returns the stored result**
without doing the work again.

```python
import uuid

accounts = {"asha": 1000}
seen = {}                      # idempotency key -> stored response

def charge(key, user, amount):
    if key in seen:
        return seen[key] + "  (replayed, no new charge)"
    accounts[user] -= amount
    seen[key] = f"charged {amount}, balance {accounts[user]}"
    return seen[key]

key = str(uuid.UUID(int=12345))             # the client creates this once per payment attempt
print(charge(key, "asha", 500))
print(charge(key, "asha", 500))             # retry after a timeout
print(charge(key, "asha", 500))             # another retry
print("final balance:", accounts["asha"])

print(charge(str(uuid.UUID(int=999)), "asha", 100))   # a genuinely new payment gets a new key
```

**Output:**

```text
charged 500, balance 500
charged 500, balance 500  (replayed, no new charge)
charged 500, balance 500  (replayed, no new charge)
final balance: 500
charged 100, balance 400
```

## Doing it properly in a real service

1. Client sends `Idempotency-Key: <uuid>` on every `POST` that creates or pays.
2. Server **atomically** inserts the key into a table with a **unique constraint**:
   `INSERT INTO idempotency(key, request_hash, status) ... ON CONFLICT DO NOTHING`.
3. If the insert succeeds, process and **store the response** against the key.
4. If the key exists and is **finished**, return the stored response.
5. If it exists and is **in progress**, return `409` or wait (another request is processing it).
6. If the key exists with a **different request body**, return `422` (the client reused a key wrongly).
7. **Expire** keys after 24 hours to 7 days.

Do the key check **and** the business write in **one transaction**, or a crash between them
leaves you with a charge and no recorded key.

## Other idempotency techniques

- **Natural unique business keys:** `UNIQUE(order_id, payment_attempt)` in the database makes a
  duplicate insert fail.
- **Conditional updates:** `UPDATE ... WHERE status = 'pending'` only the first call changes it.
- **Version numbers (optimistic locking):** `UPDATE ... WHERE version = 7`.
- **De-duplicate messages** by message id in a consumer (see webhooks and queues).
- **State machines:** "pay" is only valid from `pending`; a second "pay" is a no-op.

## Where it is used

| Place | How |
|---|---|
| Payment APIs (Stripe, UPI) | Idempotency key per payment |
| Message queue consumers | Message id table, so redelivery is harmless |
| Webhooks | Event id |
| Job schedulers | Job id + "already done" check |
| Retry libraries | Only auto-retry idempotent calls |

## Common mistakes

:::{warning}
- Retrying `POST` blindly with no key.
- Generating a **new key on every retry** (defeats the purpose). The key identifies the *operation*, not the attempt.
- Checking the key and doing the work in separate steps (a race lets two requests through).
- Storing keys forever, or not at all.
:::

## Try it yourself

1. Which are idempotent: `SET stock = 10`, `stock = stock - 1`, `DELETE /cart/items/3`, `POST /emails/send`?
2. Two retries of the same payment arrive at the same instant on two servers. What makes sure only one charges?
3. Why must the client, not the server, create the idempotency key?

<details class="solution"><summary>Answers</summary>

1. `SET stock = 10` yes; `stock = stock - 1` no; `DELETE` yes; `POST /emails/send` no (sends again).
2. A **unique constraint** on the key in one database transaction: the second insert fails and that request returns the first one's result.
3. If the server generated it, a lost response means the client never learns the key, so it cannot reference the same operation on retry.

</details>

:::{admonition} Next
:class: important
Protecting your API from clients that call too often: [rate limiting](28-rate-limiting.md).
:::
