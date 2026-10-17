# Chapter 5 · Availability

## The big idea

**Availability** answers one question: *when a user shows up, is the system working?* It is usually
quoted as a percentage of time, such as 99.9%.

**Everyday example:** a petrol station. If it is open and has fuel whenever you drive in, it is
**available**, even if the fuel is expensive or the queue is long. If it shuts for two hours every
afternoon, its availability drops. Availability says nothing about whether the fuel is *good* (that is
reliability, the next chapter).

```{raw} html
:file: ../diagrams/availability.html
```

## Measuring availability

Availability is the fraction of time a system works:

```text
availability = uptime / (uptime + downtime)
             = MTBF / (MTBF + MTTR)
```

- **MTBF** (mean time between failures): how long it runs before breaking.
- **MTTR** (mean time to repair): how long to fix it.

Notice the second formula: you can improve availability by **failing less (MTBF)** *or* by
**recovering faster (MTTR)**. Modern teams usually win by recovering faster: automatic failover,
quick rollbacks, good alerts.

## The nines

```python
HOURS_PER_YEAR = 365 * 24

for availability in (99.0, 99.9, 99.95, 99.99, 99.999):
    downtime_h = HOURS_PER_YEAR * (1 - availability / 100)
    if downtime_h >= 1:
        text = f"{downtime_h:.1f} hours"
    else:
        text = f"{downtime_h * 60:.1f} minutes"
    print(f"{availability:>7}%  ->  {text} of downtime per year")
```

**Output:**

```text
   99.0%  ->  87.6 hours of downtime per year
   99.9%  ->  8.8 hours of downtime per year
  99.95%  ->  4.4 hours of downtime per year
  99.99%  ->  52.6 minutes of downtime per year
 99.999%  ->  5.3 minutes of downtime per year
```

Each extra nine is roughly **10 times harder and more expensive**. Pick the number from the business,
not from pride:

| Product | Reasonable target | Why |
|---|---|---|
| Internal admin tool | 99% | A few hours of downtime hurts nobody |
| Online shop | 99.9% | Downtime loses sales directly |
| Payments, UPI | 99.99% | People are standing at a counter |
| Air traffic control | 99.999%+ | Lives |

## SLI, SLO and SLA

- **SLI** (indicator): the measurement. Example: "share of requests that return in under 300 ms
  without an error".
- **SLO** (objective): the internal target. "99.9% of requests are good over 30 days".
- **SLA** (agreement): the promise to customers, with a penalty. Usually *looser* than the SLO.
- **Error budget:** `100% - SLO`. At 99.9% over 30 days you may fail **43 minutes**. If you spend
  the budget, stop shipping features and fix reliability.

## Components in series and in parallel

This is the most useful calculation in the chapter.

**In series** (every part must work): multiply the availabilities. A request that needs the load
balancer, the app **and** the database:

**In parallel** (any one is enough): the failure chance multiplies. Two redundant servers fail together
only if **both** fail.

```python
def series(*parts):
    result = 1.0
    for p in parts:
        result *= p
    return result

def parallel(*parts):
    all_fail = 1.0
    for p in parts:
        all_fail *= (1 - p)
    return 1 - all_fail

lb, app, db = 0.999, 0.999, 0.999
print(f"series, no redundancy : {series(lb, app, db) * 100:.4f}%")

app2 = parallel(app, app)           # two app servers
db2 = parallel(db, db)              # primary + replica
lb2 = parallel(lb, lb)              # two load balancers
print(f"each layer doubled     : {series(lb2, app2, db2) * 100:.4f}%")
```

**Output:**

```text
series, no redundancy : 99.7003%
each layer doubled     : 99.9997%
```

Three parts, each 99.9%, give only **99.7%** in series (about 26 hours down a year). Doubling every
layer lifts the whole thing to about **99.9997%**. This is the mathematical reason for redundancy.
(The real number is lower: the failover itself can fail, and failures are often *correlated*, for
example two servers in the same rack losing power together.)

## How teams actually raise availability

1. **Remove single points of failure**: more than one of every critical part.
2. **Spread copies across failure domains**: different racks, zones and regions.
3. **Detect fast**: health checks and alerts that fire in seconds.
4. **Recover fast (cut MTTR)**: automatic failover, one-click rollback, runbooks.
5. **Deploy safely**: canary releases and feature flags, because most outages come from changes.
6. **Degrade gracefully**: serve a reduced experience instead of an error page.

## Common mistakes

:::{warning}
- Promising "100% uptime". It does not exist. State the number and the error budget.
- Adding a replica and assuming the nines multiply. Check **correlated failures** and failover time.
- Measuring availability at the server instead of **from the user's point of view**.
- Ignoring **planned** downtime: it counts against users too.
:::

## Try it yourself

1. A service must have 99.95% availability over a 30-day month. How many minutes of downtime are allowed?
2. Two servers, each 99% available, behind a perfect load balancer. What is the combined availability?
3. A request passes through 5 microservices, each 99.9% available (in series). What is the end-to-end availability?

<details class="solution"><summary>Answers</summary>

1. 30 x 24 x 60 = 43,200 minutes x 0.0005 = **21.6 minutes**.
2. 1 - (0.01 x 0.01) = **99.99%**.
3. 0.999^5 = **99.5%**, about 44 hours of failure a year. Long call chains hurt: keep the critical path short.

</details>

:::{admonition} Next
:class: important
Up is not enough: it must also be *right*. Next: [reliability](06-reliability.md).
:::
