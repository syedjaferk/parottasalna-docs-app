# Chapter 52 · Circuit breaker

## The big idea

A **circuit breaker** watches calls to a dependency. When too many fail, it **"trips"** and **stops calling
that dependency for a while**, failing fast (or using a fallback) instead of waiting on timeouts. It gives the
sick service time to recover and stops your service from being dragged down with it.

**Everyday example:** the **fuse box in your home**. If a faulty appliance draws too much current, the
breaker flips off *before* the wiring burns. You do not keep forcing power into a short circuit. After you fix
the appliance, you flip the breaker back on.

```{raw} html
:file: ../diagrams/circuit-breaker.html
```

## The problem: cascading failure

Service A calls service B. B becomes slow (not dead, just slow: 30-second responses).

```text
A's threads wait on B  ->  A runs out of threads  ->  A becomes slow  ->  callers of A back up  ->  ... everything fails
```

A failure in one small service **spreads** to the whole system because everyone politely waits. Retries make
it worse: each failed call is retried, tripling the load on the struggling service exactly when it is weakest.

## The three states

1. **Closed (normal):** calls pass through. The breaker counts failures. If failures exceed a threshold
   (for example 50% of the last 20 calls, or 5 in a row), it **opens**.
2. **Open (tripped):** calls **fail immediately** (or return a fallback) without touching the dependency.
   After a **cool-down** (say 30 seconds) it moves to half-open.
3. **Half-open (testing):** a **few trial calls** are allowed. If they succeed, the breaker **closes**. If any
   fail, it **opens again** and the cool-down restarts.

## A working circuit breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=3, cooldown=10):
        self.threshold, self.cooldown = failure_threshold, cooldown
        self.failures, self.state, self.opened_at = 0, "CLOSED", 0

    def call(self, func, now, fallback=None):
        if self.state == "OPEN":
            if now - self.opened_at >= self.cooldown:
                self.state = "HALF_OPEN"                 # allow one trial call
            else:
                return fallback() if fallback else "FAST-FAIL (breaker open)"
        try:
            result = func()
        except Exception:
            self.failures += 1
            if self.state == "HALF_OPEN" or self.failures >= self.threshold:
                self.state, self.opened_at = "OPEN", now
            return fallback() if fallback else "ERROR"
        self.failures, self.state = 0, "CLOSED"           # success closes it
        return result

healthy = {"up": False}
def payments():
    if not healthy["up"]:
        raise TimeoutError("payment service timed out")
    return "payment ok"

breaker = CircuitBreaker(failure_threshold=3, cooldown=10)
fallback = lambda: "FALLBACK: queued for later"

for t in range(0, 24, 2):
    if t == 8:
        healthy["up"] = True                             # the dependency recovers while the breaker is open
    reply = breaker.call(payments, now=t, fallback=fallback)
    print(f"t={t:>2}s  breaker is {breaker.state:<9} after the call  -> {reply}")
```

**Output:**

```text
t= 0s  breaker is CLOSED    after the call  -> FALLBACK: queued for later
t= 2s  breaker is CLOSED    after the call  -> FALLBACK: queued for later
t= 4s  breaker is OPEN      after the call  -> FALLBACK: queued for later
t= 6s  breaker is OPEN      after the call  -> FALLBACK: queued for later
t= 8s  breaker is OPEN      after the call  -> FALLBACK: queued for later
t=10s  breaker is OPEN      after the call  -> FALLBACK: queued for later
t=12s  breaker is OPEN      after the call  -> FALLBACK: queued for later
t=14s  breaker is CLOSED    after the call  -> payment ok
t=16s  breaker is CLOSED    after the call  -> payment ok
t=18s  breaker is CLOSED    after the call  -> payment ok
t=20s  breaker is CLOSED    after the call  -> payment ok
t=22s  breaker is CLOSED    after the call  -> payment ok
```

After three failures (t=0, 2, 4) the breaker **opened** and callers got an instant fallback with no waiting on timeouts, even
though the dependency recovered at t=8. Only when the 10-second cool-down ended (t=14) did it send **one trial call**; that
succeeded, so the breaker **closed** and normal traffic resumed.

## What to return when the circuit is open

A fast failure is only useful if the caller handles it well. Options:

- **Fallback value:** cached data, a default, an empty list.
- **Degraded feature:** hide the recommendations panel.
- **Queue for later:** accept the order and process the payment when it recovers.
- **Alternative provider:** switch to a second payment gateway.
- **Clear error:** `503` with `Retry-After`.

## Companion patterns

A circuit breaker is one tool among several; they work best together:

| Pattern | What it does |
|---|---|
| **Timeouts** | Never wait forever. The foundation of everything else. |
| **Retries with backoff and jitter** | Retry transient errors; **stop** when the breaker opens |
| **Bulkhead** | Separate thread pools or connection limits per dependency, so one slow dependency cannot use every thread |
| **Rate limiting / load shedding** | Protect the **server** side |
| **Fallbacks / graceful degradation** | Keep the core experience alive |
| **Health checks** | Take failing instances out of rotation |

```text
call -> [bulkhead: limit concurrent calls to 20] -> [circuit breaker] -> [timeout 500 ms] -> [retry max 2, with backoff] -> dependency
```

## Tuning

| Setting | Too low | Too high |
|---|---|---|
| Failure threshold | Trips on a blip | Reacts too late |
| Cool-down | Hammers a recovering service | Stays closed to a healthy one for too long |
| Trial calls (half-open) | Cannot judge | Floods a fragile service |
| Timeout | False failures | Threads stuck |

Count **slow calls** as failures too (a 30-second answer is as bad as an error). Use a **sliding window** of
recent calls and a **minimum number of calls** before judging (do not trip on 1 of 1).

## Libraries and platforms

- **Resilience4j** (Java), **Hystrix** (retired, but the origin of the idea), **Polly** (.NET),
  **pybreaker** (Python), **gobreaker** (Go).
- **Service meshes** (Istio, Envoy, Linkerd) apply circuit breaking, retries and timeouts **outside** your
  code, in the sidecar proxy.

## Common mistakes

:::{warning}
- Retrying aggressively with no breaker: a **retry storm** that turns a brownout into an outage.
- No timeout: the breaker never sees a failure because calls never return.
- One breaker for all dependencies, so an unrelated failure trips everything.
- Opening with no fallback or user-facing plan: fast failure is still failure.
- Forgetting **metrics and alerts** on breaker state changes.
:::

## Try it yourself

1. A breaker opens after 5 failures and has a 30-second cool-down. What happens on the first call after 30 seconds, and why only one?
2. Why is "fail fast" better than "wait for the timeout" when a dependency is down?
3. How does a bulkhead differ from a circuit breaker?

<details class="solution"><summary>Answers</summary>

1. The breaker goes **half-open** and allows a **trial call**. If it succeeds it closes; if it fails it re-opens. Only one (or a few) so a fragile service is not flooded while recovering.
2. Waiting ties up threads and connections for the whole timeout, which spreads the failure upstream. Failing fast frees resources immediately and gives the dependency room to recover.
3. A **bulkhead limits resources per dependency** (e.g. 20 concurrent calls) so a slow one cannot starve others. A **circuit breaker stops calling** a failing dependency for a period. They solve different halves and are used together.

</details>

:::{admonition} Next
:class: important
Even with all this, entire sites and regions can fail. Planning for it: [disaster recovery](53-disaster-recovery.md).
:::
