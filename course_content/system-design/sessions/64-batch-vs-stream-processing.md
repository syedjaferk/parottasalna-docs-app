# Chapter 64 · Batch vs stream processing

## The big idea

- **Batch processing** collects data **over a period** and processes it **all at once** on a schedule (nightly
  sales report).
- **Stream processing** processes each record **as it arrives**, continuously, within seconds or
  milliseconds (fraud check on each card swipe).

**Everyday example:** **laundry versus a conveyor-belt dry-cleaner**. At home you collect clothes through the
week and run **one big load on Sunday** (batch): efficient, but you wear dirty shirts until then. A
conveyor-belt cleaner washes **each garment the moment it arrives** (stream): always fresh, but the machinery
runs all the time.

```{raw} html
:file: ../diagrams/batch-vs-stream.html
```

## Side by side

| | **Batch** | **Stream** |
|---|---|---|
| Data | **Bounded**: a finite set (yesterday's logs) | **Unbounded**: never ends |
| When it runs | Scheduled (hourly, nightly) | **Continuously** |
| Latency | Minutes to hours | **Milliseconds to seconds** |
| Throughput | **Very high**, efficient bulk work | High, but per-record overhead |
| Complexity | Simpler: rerun on failure | Harder: ordering, late data, state, exactly-once |
| Failure recovery | **Rerun the job** | Checkpoints, replay from the log |
| Use of resources | Bursty: big cluster, then idle | Steady |
| Examples | Payroll, billing, ETL, ML training, reports | Fraud detection, live dashboards, alerts, recommendations |
| Tools | Hadoop MapReduce, Spark, SQL warehouses, Airflow | Kafka Streams, Flink, Spark Structured Streaming, Kinesis |

## The same job both ways

Count orders per city.

```python
from collections import Counter

orders = [("Chennai", 120), ("Pune", 80), ("Chennai", 45), ("Delhi", 200), ("Pune", 60), ("Chennai", 30)]

# BATCH: read everything, compute once at the end
def batch_totals(all_orders):
    totals = Counter()
    for city, amount in all_orders:
        totals[city] += amount
    return dict(totals)

print("batch result (available after the whole day):", batch_totals(orders))

# STREAM: keep running state, update on every event, and the answer is always current
totals = Counter()
def on_order(city, amount):
    totals[city] += amount
    return dict(totals)

for city, amount in orders:
    live = on_order(city, amount)
    print(f"stream after order from {city:<8} -> {live}")
```

**Output:**

```text
batch result (available after the whole day): {'Chennai': 195, 'Pune': 140, 'Delhi': 200}
stream after order from Chennai  -> {'Chennai': 120}
stream after order from Pune     -> {'Chennai': 120, 'Pune': 80}
stream after order from Chennai  -> {'Chennai': 165, 'Pune': 80}
stream after order from Delhi    -> {'Chennai': 165, 'Pune': 80, 'Delhi': 200}
stream after order from Pune     -> {'Chennai': 165, 'Pune': 140, 'Delhi': 200}
stream after order from Chennai  -> {'Chennai': 195, 'Pune': 140, 'Delhi': 200}
```

Both reach the same final numbers. The stream version has an answer **after every event**; the batch version
only at the end.

## Windows: how streams make sense of endless data

A stream has no "end", so aggregations use **windows**:

- **Tumbling window:** fixed, non-overlapping (every 1 minute).
- **Sliding (hopping) window:** overlapping (last 5 minutes, updated every minute).
- **Session window:** groups events separated by gaps of inactivity (a user's visit).

```python
events = [(1, "a"), (2, "b"), (31, "c"), (58, "d"), (61, "e"), (95, "f"), (130, "g")]   # (timestamp seconds, id)

def tumbling(events, size):
    windows = {}
    for ts, _ in events:
        windows.setdefault(ts // size * size, []).append(ts)
    return {f"{start}-{start + size}s": len(v) for start, v in sorted(windows.items())}

print("events per 60 s tumbling window:", tumbling(events, 60))
```

**Output:**

```text
events per 60 s tumbling window: {'0-60s': 4, '60-120s': 2, '120-180s': 1}
```

## Hard problems in streaming

- **Event time vs processing time:** an event that happened at 12:00:58 may arrive at 12:01:10. Use the
  **event timestamp**, with **watermarks** (a promise that "nothing older than time T will arrive") and an
  **allowed lateness**.
- **Out-of-order and late data:** handle updates to windows already emitted.
- **State:** counting needs memory that survives failures: **checkpoints** to durable storage.
- **Exactly-once results:** achieved with idempotent sinks, transactions or checkpoint plus replay.
- **Back pressure:** a slow consumer must be able to slow producers.
- **Reprocessing:** replay the log from an offset to fix a bug.

## Lambda and Kappa architectures

**Lambda:** run **both**: a **batch layer** (accurate, recomputed over all data) and a **speed layer** (fast,
approximate), merged at query time. Powerful but you maintain **two code paths**.

**Kappa:** use **only streaming** over a replayable log (Kafka). "Batch" is just a stream replayed from the
start. One code path. Modern engines (Flink, Spark Structured Streaming) treat batch as a special case of
streaming.

## Choosing

| Question | Lean to |
|---|---|
| How fresh must results be? Seconds or less | **Stream** |
| Hours or a day is fine | **Batch** (simpler, cheaper) |
| Is the full dataset needed for the answer (train a model, join entire tables)? | **Batch** |
| Reactions to events (alerts, fraud, personalisation)? | **Stream** |
| Small team, limited ops capability? | **Batch** |
| Need both fresh and corrected figures? | Stream for freshness, batch to reconcile |

Often the right design is **streaming for what must be fast, batch for what must be right and cheap**.

## Common mistakes

:::{warning}
- Building a streaming system for a report nobody reads before morning.
- Using processing time instead of **event time** and then producing wrong windows.
- No plan for late data or replays.
- Streaming jobs without checkpoints (a restart loses all state).
- Maintaining two diverging code paths (Lambda) without need.
:::

## Try it yourself

1. Which fits: monthly payroll, card-fraud detection, nightly search index rebuild, live traffic map?
2. An event timestamped 12:00:58 arrives at 12:01:10. Which window should count it, and what concept lets you handle this?
3. Why is a failed batch job usually easier to recover than a failed streaming job?

<details class="solution"><summary>Answers</summary>

1. Payroll: batch. Fraud detection: **stream**. Index rebuild: batch. Live traffic map: **stream**.
2. The 12:00 window (its **event time**). **Watermarks** and allowed lateness let the engine wait for or update windows.
3. A batch job has a finite input and can simply be **rerun**; a streaming job has continuous state and an unbounded input, so it needs checkpoints and replay.

</details>

:::{admonition} Next
:class: important
Where do you keep a user's state? [Stateful vs stateless design](65-stateful-vs-stateless-architecture.md).
:::
