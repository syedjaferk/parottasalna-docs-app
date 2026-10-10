# Session 16 · Amazon API Gateway: REST APIs, HTTP APIs, Lambda & Security

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/Jw9OzYrLySQ"
  title="Session 16: Amazon API Gateway" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 16** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=Jw9OzYrLySQ)

## The big idea

An **API gateway** is the single front door for your APIs. Clients call one address; the gateway
**routes** each request to the right backend, checks **who** is calling, **limits** how often,
and records **metrics**, so every microservice doesn't have to re-implement all that.
**Amazon API Gateway** is AWS's fully managed version, and it pairs naturally with **Lambda** for
serverless backends.

**Everyday example:** a hotel's front desk. Guests don't wander into the kitchen or laundry; they ask
the desk, which checks their room key (auth), passes the request to the right department (routing),
and politely refuses someone calling every ten seconds (throttling).

## 1. First, the idea locally: KrakenD (class demo)

Before AWS, the class ran an open-source gateway, **KrakenD**, in Docker Compose.

**Routing:** one front door, two services:

```text
{ "endpoint": "/api/users/{user_id}",       "backend": [{ "host": ["http://user-service:8000"],    "url_pattern": "/users/{user_id}" }] },
{ "endpoint": "/api/products/{product_id}", "backend": [{ "host": ["http://product-service:8000"], "url_pattern": "/products/{product_id}" }] }
```

```bash
cd 01.api_routing && docker compose up -d --build
curl localhost:8082/api/users/42
curl localhost:8082/api/products/1
```

**Output:**

```text
{"email":"john@example.com","id":42,"name":"John Doe"}
{"id":1,"name":"MacBook Pro","price":2000}
```

**Aggregation:** one call, three services, one combined answer. Each backend's response goes
under its own `group`:

```bash
cd 02.aggregation && docker compose up -d --build
curl localhost:8082/customer/7
```

**Output:**

```text
{"orders":{"orders":[{"amount":500,"id":101},{"amount":900,"id":102}]},"user":{"email":"john@example.com","id":7,"name":"John Doe"},"wallet":{"balance":2500}}
```

A mobile app makes **one** request instead of three. And clients can't call the services directly:
`curl localhost:8082/orders/user/7` returns **404**, because only routes defined in the gateway exist.

## 2. Amazon API Gateway

```{raw} html
:file: ../diagrams/s16-apigw.html
```

### Three API types

| | **REST API** | **HTTP API** | **WebSocket API** |
|---|---|---|---|
| For | full-featured APIs | simple, fast, cheap APIs (most new Lambda / HTTP backends) | two-way real-time (chat, live updates) |
| Price / latency | higher | **cheaper (about 70 % less) and lower latency** | per message + connection minutes |
| Auth | IAM, Cognito, Lambda authorizers, **API keys + usage plans** | IAM, **JWT authorizers** (Cognito, Auth0…), Lambda authorizers | IAM, Lambda authorizers |
| Extras | request validation, caching, **WAF**, transformations, private APIs, edge-optimized | automatic deployments, simple CORS | routes by message content |

### Key words

| Term | Meaning |
|---|---|
| **Resource / route** | a path and method: `GET /courses/{id}` |
| **Integration** | what the route calls: **Lambda**, any **HTTP** URL, other AWS services directly (e.g. SQS), or a mock |
| **Lambda proxy integration** | passes the whole request to Lambda and returns its response as-is (the common choice) |
| **Stage** | a deployed version with its own URL: `dev`, `prod` (`…/prod/courses/1`) |
| **Deployment** | a snapshot of the API published to a stage (REST APIs need an explicit deploy) |

## 3. Hands-on: HTTP API + Lambda

1. **Lambda** → *Create function* → Python 3.12, name `getCourse`:

   ```python
   import json

   def lambda_handler(event, context):
       course_id = event["pathParameters"]["id"]
       return {
           "statusCode": 200,
           "headers": {"Content-Type": "application/json"},
           "body": json.dumps({"id": course_id, "title": "AWS Solutions Architect"}),
       }
   ```

2. **API Gateway** → *Create API* → **HTTP API** → integration: Lambda `getCourse` → route
   `GET /courses/{id}` → stage `$default` (auto-deploy).
3. Call it:

```bash
curl https://abc123.execute-api.ap-south-1.amazonaws.com/courses/42
```

**Output:**

```text
{"id": "42", "title": "AWS Solutions Architect"}
```

API Gateway automatically adds a resource-based permission to the Lambda function so it may
invoke it.

## 4. Security, limits and the rest

- **Authentication / authorization:** IAM (SigV4, for AWS callers), **Cognito user pools / JWT**
  (for app users), **Lambda authorizers** (custom logic: check a header, call your auth service).
- **API keys + usage plans** (REST): give each partner a key with a **quota** (e.g. 10,000 requests
  a month) and **throttle** (e.g. 50 requests/second). API keys identify callers; they are **not** a
  security mechanism on their own.
- **Throttling:** by default about **10,000 requests per second** per account per Region, with a
  burst of 5,000; over the limit, clients get **429 Too Many Requests**. Set lower limits per stage or route.
- **CORS:** let browser apps on another domain call the API (allowed origins, methods, headers).
- **Custom domains:** `api.parottasalna.com` with an **ACM** certificate, then a Route 53 Alias record
  ([Session 14](14-route-53.md)). Edge-optimized APIs need the certificate in **us-east-1**.
- **WAF** on REST APIs ([Session 12](12-aws-waf.md)).
- **Timeouts:** the integration timeout is **29 seconds** by default. Long jobs should be asynchronous
  (e.g. queue to SQS and return `202 Accepted`).
- **Monitoring:** CloudWatch metrics `Count`, `Latency`, `IntegrationLatency`, `4XXError`,
  `5XXError`; access logs and X-Ray tracing.

## Common mistakes

- **Treating an API key as authentication.** Use IAM, JWT/Cognito or a Lambda authorizer.
- **Changing a REST API and forgetting to *Deploy* it to the stage.**
- **Browser errors that are really CORS:** the API works with curl but not from the web app.
- **Long-running Lambda behind API Gateway:** the request fails at the integration timeout even if the function keeps running.
- **Choosing REST API by habit** when an HTTP API is enough, and paying more.

## Try it yourself

1. A startup needs a simple, cheap API in front of Lambda with JWT auth from Cognito. REST or HTTP API?

   <details class="solution">
   <summary>Answer</summary>

   **HTTP API**: cheaper, lower latency, built-in JWT authorizers.

   </details>

2. A partner must be limited to 1,000 requests per day with their own key. Which feature?

   <details class="solution">
   <summary>Answer</summary>

   A **REST API** with an **API key** and a **usage plan** (quota 1,000/day plus a throttle).

   </details>

3. Add a third backend to the KrakenD aggregation example: `GET /rewards/{user_id}`.

   <details class="solution">
   <summary>Answer</summary>

   Add a `rewards-service` to `docker-compose.yml`, and another object to the endpoint's `backend`
   list in `krakend.json` with `"group": "rewards"`, its host and `"url_pattern": "/rewards/{user_id}"`.

   </details>

## Class files

<details class="source">
<summary>01.api_routing/krakend/krakend.json</summary>

```{literalinclude} ../code/16-api-gateway-local/01.api_routing/krakend/krakend.json
:language: json
```

</details>

<details class="source">
<summary>02.aggregation/krakend/krakend.json</summary>

```{literalinclude} ../code/16-api-gateway-local/02.aggregation/krakend/krakend.json
:language: json
```

</details>

<details class="source">
<summary>02.aggregation/docker-compose.yml</summary>

```{literalinclude} ../code/16-api-gateway-local/02.aggregation/docker-compose.yml
:language: yaml
```

</details>

- Downloads: {download}`routing compose file <../code/16-api-gateway-local/01.api_routing/docker-compose.yml>` ·
  {download}`user-service app.py <../code/16-api-gateway-local/01.api_routing/user-service/app.py>` ·
  {download}`order-service app.py <../code/16-api-gateway-local/02.aggregation/order-service/app.py>` ·
  {download}`wallet-service app.py <../code/16-api-gateway-local/02.aggregation/wallet-service/app.py>`
- Whiteboards: {download}`API Gateway on AWS <../code/whiteboards/16-api-gateway-architecture.excalidraw>` ·
  {download}`API gateway locally <../code/whiteboards/16-api-gateway-local.excalidraw>`
  (open at [excalidraw.com](https://excalidraw.com))
