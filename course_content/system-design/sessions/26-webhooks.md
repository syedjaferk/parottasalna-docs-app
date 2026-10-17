# Chapter 26 · Webhooks

## The big idea

A **webhook** is an HTTP request that a service sends **to you** when something happens, instead of
you repeatedly asking "has it happened yet?". It is "don't call us, we'll call you" for APIs.

**Everyday example:** you order food. You can phone the restaurant every 5 minutes (**polling**), or
leave your number and let them **call you** when it is ready (**webhook**).

```{raw} html
:file: ../diagrams/webhooks.html
```

## Polling vs webhook

| | Polling | Webhook |
|---|---|---|
| Who starts | You, on a timer | The provider, on an event |
| Delay | Up to the polling interval | Near real time |
| Wasted calls | Many ("nothing new") | None |
| Needs a public endpoint | No | **Yes**: you must expose a URL |
| Reliability | You control retries | Provider retries; you must handle duplicates |

Real examples: **Stripe** tells you a payment succeeded, **GitHub** tells your CI a commit was pushed,
**Razorpay/UPI gateways** report a settlement, **Slack** sends slash commands, **Twilio** reports an SMS
delivered.

## The flow

1. You **register** a URL with the provider (`https://shop.example.com/hooks/payments`) and receive a
   **secret** for signing.
2. An event occurs (payment succeeded).
3. The provider sends `POST /hooks/payments` with a JSON body and a **signature header**.
4. Your endpoint **verifies the signature**, **stores the event**, and replies `200` quickly.
5. You process the event **asynchronously**.
6. If you did not reply `2xx` in time, the provider **retries** (exponential backoff, for hours or days).

## The four rules of a good webhook receiver

### 1. Verify the signature (anyone can POST to a public URL)

The provider computes an **HMAC** of the body with the shared secret and sends it in a header. You
recompute and compare, using a **constant-time** comparison.

```python
import hmac, hashlib, json

SECRET = b"whsec_demo_secret"

def sign(body: bytes) -> str:
    return hmac.new(SECRET, body, hashlib.sha256).hexdigest()

def verify(body: bytes, signature: str) -> bool:
    return hmac.compare_digest(sign(body), signature)

body = json.dumps({"event": "payment.succeeded", "id": "evt_1001", "amount": 499}).encode()
good = sign(body)
print("genuine webhook accepted :", verify(body, good))

tampered = body.replace(b"499", b"1")
print("tampered body accepted   :", verify(tampered, good))
print("forged signature accepted:", verify(body, "0" * 64))
```

**Output:**

```text
genuine webhook accepted : True
tampered body accepted   : False
forged signature accepted: False
```

Without a secret an attacker cannot produce a valid signature, so they cannot forge "payment succeeded".
Also check a **timestamp** in the signed payload to stop **replay** of an old valid request.

### 2. Reply fast, process later

The provider times out after a few seconds. Do not run the heavy work inside the request: **save the
event to a queue or table and return `200`**. A worker handles it.

### 3. Be idempotent (you will get duplicates)

Retries mean the **same event can arrive twice**. Store each event `id`; if you have seen it, return
`200` and do nothing.

```python
processed = set()
balance = {"asha": 0}

def handle_event(event):
    if event["id"] in processed:
        return "duplicate ignored"
    processed.add(event["id"])
    balance[event["user"]] += event["amount"]
    return "applied"

evt = {"id": "evt_1001", "user": "asha", "amount": 499}
print(handle_event(evt))
print(handle_event(evt))                  # the provider retried
print("balance:", balance)
```

**Output:**

```text
applied
duplicate ignored
balance: {'asha': 499}
```

### 4. Do not depend on order

Events can arrive **out of order** (`order.updated` before `order.created`). Use the event's timestamp or
a version number, or **fetch the current state from the provider's API** when an event arrives.

## Sending webhooks (when you are the provider)

Designing your own webhook system is a good interview topic:

- Customers register URLs and event types; you **sign** every request.
- Put events on a **queue**; **worker pool** sends them so a slow customer does not block others.
- **Retry with exponential backoff** (1 min, 5 min, 30 min, 2 h ... up to ~24 h), then mark the endpoint
  failing and **disable** it after repeated failures, emailing the owner.
- Add a **dead-letter queue** and a dashboard to **replay** failed deliveries.
- Set a **timeout** (5 to 10 s), limit **payload size**, and use **per-customer concurrency limits**.
- Protect against **SSRF**: never let a customer register `http://169.254.169.254/` or internal addresses.

## Common mistakes

:::{warning}
- Trusting a webhook without verifying its signature.
- Doing slow processing before replying, so the provider times out and retries (duplicates!).
- Assuming exactly-once delivery. It is **at-least-once**.
- Exposing the endpoint with no rate limit or size limit.
:::

## Try it yourself

1. Your endpoint takes 20 seconds to process a payment event and the provider times out at 5 seconds. What do you change?
2. The same `payment.succeeded` webhook arrives three times. How do you avoid crediting three times?
3. Why is an HMAC signature better than just an IP allow-list?

<details class="solution"><summary>Answers</summary>

1. Accept the event, write it to a queue, return `200` immediately, and process in a worker.
2. Keep a table of processed **event ids** (unique constraint) and skip duplicates.
3. IPs can change, be shared, or be spoofed behind proxies. A signature proves the **content** was produced by someone who knows the secret and was not modified.

</details>

:::{admonition} Next
:class: important
Retries and duplicates are everywhere in distributed systems. The fix is [idempotency](27-idempotency.md).
:::
