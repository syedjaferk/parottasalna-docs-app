# Chapter 57 · Serverless architecture

## The big idea

In **serverless**, you write **functions or small pieces of code**, upload them, and the cloud provider runs
them **on demand**: it provisions machines, scales to the number of requests, and **bills only for the time
your code actually runs**. There are still servers, but **you do not manage them**.

**Everyday example:** a **taxi versus owning a car**. Owning a car means you pay for it, insure it, park it and
maintain it even when it sits idle. A taxi (serverless) appears when you call, takes you there, and you pay only
for the ride. If a hundred friends need rides at once, a hundred taxis come.

```{raw} html
:file: ../diagrams/serverless.html
```

## Two flavours

1. **FaaS (Functions as a Service):** short event-triggered functions. AWS Lambda, Google Cloud Functions,
   Azure Functions, Cloudflare Workers.
2. **BaaS (Backend as a Service):** fully managed building blocks you glue together: auth (Cognito, Auth0),
   databases (DynamoDB, Firestore), storage (S3), queues (SQS), API gateways.

A serverless app usually combines both: **API Gateway + Lambda + DynamoDB + S3 + SQS**.

## How it runs

1. An **event** arrives: an HTTP request, a file uploaded to storage, a message on a queue, a timer.
2. The platform finds (or creates) an **execution environment** (a micro-container), loads your code and runs it.
3. After the function returns, the environment stays **warm** for a few minutes for reuse, then is destroyed.
4. If 1,000 events arrive together, the platform runs up to **1,000 copies in parallel**.

```python
# The shape of a function: stateless, triggered by an event, returns a result
def handler(event, context=None):
    name = event.get("name", "world")
    return {"statusCode": 200, "body": f"Hello, {name}!"}

print(handler({"name": "Asha"}))
print(handler({}))
```

**Output:**

```text
{'statusCode': 200, 'body': 'Hello, Asha!'}
{'statusCode': 200, 'body': 'Hello, world!'}
```

There is no server, no port, no loop: the platform calls `handler` once per event.

## Cold starts

When no warm environment exists, the platform must **create one first**: download code, start the runtime,
run your initialisation. That adds **100 ms to several seconds** to that first request (the **cold start**),
worst for large packages, heavy runtimes (JVM) and functions inside a VPC.

Mitigations: **keep functions small**, lazy-load heavy libraries, choose a fast runtime (Node, Python, Go),
**provisioned concurrency** (keep N warm, costs money), avoid unnecessary startup work, and reuse connections
across invocations by creating them **outside** the handler.

## Cost model: pay per use

```python
def lambda_monthly_cost(requests, avg_ms, memory_gb=0.5,
                        per_million_requests=0.20, per_gb_second=0.0000166667):
    gb_seconds = requests * (avg_ms / 1000) * memory_gb
    return requests / 1e6 * per_million_requests + gb_seconds * per_gb_second

def server_monthly_cost(servers, per_server=35.0):
    return servers * per_server

for requests in (100_000, 5_000_000, 100_000_000, 1_000_000_000):
    serverless = lambda_monthly_cost(requests, avg_ms=100)
    servers_needed = max(2, round(requests / (30 * 86_400) / 250 * 3) + 1)      # 250 rps per server, 3x peak, +1 spare
    classic = server_monthly_cost(servers_needed)
    cheaper = "serverless" if serverless < classic else "servers"
    print(f"{requests:>13,} req/month: serverless ${serverless:>9,.2f}   servers ${classic:>7,.0f}  -> {cheaper}")
```

**Output:**

```text
      100,000 req/month: serverless $     0.10   servers $     70  -> serverless
    5,000,000 req/month: serverless $     5.17   servers $     70  -> serverless
  100,000,000 req/month: serverless $   103.33   servers $     70  -> servers
1,000,000,000 req/month: serverless $ 1,033.34   servers $    210  -> servers
```

For spiky or low traffic serverless is dramatically cheaper (idle costs nothing). For steady, very high
volume, always-on servers can win. (Prices here are illustrative.)

## Strengths and weaknesses

| Strengths | Weaknesses |
|---|---|
| **No servers to manage**, patch or scale | **Cold starts** add latency to some requests |
| **Automatic scaling**, from zero to thousands | **Time limits** (e.g. 15 minutes max), memory limits |
| **Pay per use**, zero cost when idle | **Stateless**: no local state between calls |
| Fast to build and ship | **Vendor lock-in** (triggers, services, permissions) |
| Built-in availability across zones | **Hard to debug and test locally**; distributed by nature |
| Great for event-driven glue | Can get **expensive** at sustained high load |
| | **Limits on concurrency**; a burst can overwhelm a downstream database |

## Design guidance

- **Stateless:** keep state in a database, cache or object storage.
- **Idempotent handlers:** events may be delivered more than once (queues, retries).
- **Short and focused:** one function, one job.
- **Protect downstreams:** thousands of parallel Lambdas can exhaust a relational database's connections. Use
  a connection pool proxy (RDS Proxy), or a serverless-friendly database (DynamoDB), or put a **queue** in
  front with limited concurrency.
- **Use async patterns:** put slow work on a queue; return fast to the caller.
- **Timeouts and dead-letter queues** on every trigger.
- **Least-privilege roles** per function.

## Good fits and poor fits

| Great for | Poor for |
|---|---|
| Event-driven pipelines (image upload creates a thumbnail) | Long-running or heavy compute (video encoding for hours) |
| APIs with unpredictable or spiky traffic | Ultra-low, predictable latency (cold starts) |
| Scheduled jobs (nightly clean-up) | Stateful, connection-heavy workloads (WebSocket servers, games) |
| Webhooks, chatbots, glue code | Steady, very high throughput (cost) |
| Startups wanting to ship fast | Workloads needing special hardware or full control of the OS |

## A typical serverless design

```text
Browser -> CDN (S3 static site)
Browser -> API Gateway -> Lambda (create order) -> DynamoDB
                                   \-> SQS queue -> Lambda (send email) -> SES
S3 upload event -> Lambda (resize image) -> S3
CloudWatch schedule (nightly) -> Lambda (clean-up)
```

## Common mistakes

:::{warning}
- Assuming cold starts do not matter for user-facing APIs.
- Opening a new database connection on every invocation (connections run out).
- Storing state in the function's memory or local disk.
- Non-idempotent handlers behind at-least-once triggers.
- Ignoring cost at scale; there is a crossover point where servers or containers are cheaper.
- Building a chain of functions calling functions synchronously (latency adds up, failures multiply).
:::

## Try it yourself

1. A function runs 20 million times a month for 200 ms at 1 GB memory. How many GB-seconds is that?
2. Why can thousands of parallel Lambdas hurt a PostgreSQL database?
3. Give a good and a poor use case for serverless.

<details class="solution"><summary>Answers</summary>

1. 20,000,000 x 0.2 s x 1 GB = **4,000,000 GB-seconds**.
2. Each invocation may open its own connection, and PostgreSQL supports only a few hundred; use a connection pooler or limit concurrency with a queue.
3. Good: resizing uploaded images on demand. Poor: a long-lived WebSocket game server or heavy multi-hour compute.

</details>

:::{admonition} Next
:class: important
Services reacting to things that happened: [event-driven architecture](58-event-driven-architecture.md).
:::
