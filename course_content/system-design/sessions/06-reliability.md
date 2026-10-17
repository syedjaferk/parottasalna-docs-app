# Chapter 6 · Reliability

## The big idea

A system is **reliable** if it **does the right thing, every time, even when things go wrong**.
Availability asks "is it up?". Reliability asks "is it *correct*, and does it keep its promises?".

**Everyday example:** a courier service. If parcels always arrive (availability) but sometimes to the
wrong house, it is up but **unreliable**. A reliable courier delivers the right parcel to the right
door, and when a van breaks down, the parcel still arrives.

| | Available | Not available |
|---|---|---|
| **Reliable** | Ideal | Correct but down for maintenance |
| **Unreliable** | Up, but wrong answers, lost data, double charges | Worst case |

```{raw} html
:file: ../diagrams/reliability.html
```

## What reliability means in practice

A reliable system keeps four promises:

1. **Correctness:** the answer is right (the order total adds up).
2. **Durability:** data that was acknowledged is never lost, even after a crash.
3. **Consistency of behaviour:** it does the same thing under load as when idle.
4. **Recoverability:** after a failure it returns to a correct state by itself.

## The tools

### 1. Redundancy

Several copies of data and compute, so one failure is not the end. (See SPOF and failover chapters.)

### 2. Retries with exponential backoff and jitter

Networks fail briefly all the time. A reliable client **tries again**, but politely: wait longer after
each failure, and add randomness so thousands of clients do not retry at the same instant.

```python
import random
random.seed(1)

def flaky_call(attempt):
    """Fails twice, succeeds on the third try."""
    return attempt >= 3

def call_with_retry(max_attempts=5, base=0.1, cap=5.0):
    waited = 0.0
    for attempt in range(1, max_attempts + 1):
        if flaky_call(attempt):
            return f"success on attempt {attempt}, waited {waited:.2f}s in total"
        backoff = min(cap, base * 2 ** attempt)          # 0.2, 0.4, 0.8, ...
        waited += random.uniform(0, backoff)             # "full jitter"
    return "gave up"

print(call_with_retry())
```

**Output:**

```text
success on attempt 3, waited 0.37s in total
```

Without a limit and without backoff, retries become a **retry storm**: when a service is struggling,
every client hammering it makes it worse.

### 3. Idempotent operations

A retry must not charge the card twice. Make writes **idempotent** with a unique request id. (See the
idempotency chapter.)

### 4. Durable storage

- **Write-ahead log (WAL):** write the intention to disk **before** changing data. After a crash,
  replay the log.
- **Replication:** at least 3 copies of important data, in different zones.
- **Backups, and restore drills:** a backup you have never restored is a hope, not a backup.
- **Checksums:** detect silent corruption (see the checksums chapter).

### 5. Validation and safe change

- Validate input at the edge; reject nonsense early.
- **Automated tests and canary deployments:** release to 1% of traffic first.
- **Feature flags:** turn a bad feature off without a deploy.
- **Rollbacks** that take minutes, not hours.

## Measuring reliability

| Metric | Meaning |
|---|---|
| **Error rate** | Share of requests that fail or return wrong results |
| **MTBF** | Mean time between failures: higher is better |
| **MTTR** | Mean time to repair: lower is better |
| **Durability** | Chance data is not lost over a year (S3: "11 nines") |
| **Data-loss window (RPO)** | How much recent data you may lose in a disaster |

## What actually breaks reliability

1. **Software changes** (bugs, bad config): the largest cause.
2. **Overload:** traffic spikes, retry storms, a slow dependency.
3. **Hardware and network failures.**
4. **Human error:** the wrong command in production.
5. **Third-party dependencies:** a payment gateway or DNS provider goes down.

## Common mistakes

:::{warning}
- Retrying with no backoff, no cap and no jitter.
- Retrying non-idempotent operations (double payments).
- Treating "the server returned 200" as proof of correctness: the data may be wrong.
- Never testing backups or failure paths.
:::

## Try it yourself

1. Why add *jitter* to retry delays?
2. A queue consumer crashes after charging a customer but before acknowledging the message. What stops a double charge on redelivery?
3. What is the difference between a system that is highly available but not reliable? Give an example.

<details class="solution"><summary>Answers</summary>

1. Without it, all clients that failed together retry together and overload the server again. Random delays spread the retries out.
2. An **idempotency key**: the second attempt carries the same key, the payment service finds the stored result and returns it without charging again.
3. A service that always answers but sometimes returns stale or wrong data, or loses writes: for example a cache-only store that acknowledges writes and loses them on restart.

</details>

:::{admonition} Next
:class: important
Reliability starts with knowing what can take you down: [single points of failure](07-spof.md).
:::
