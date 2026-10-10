# Session 16 · Amazon API Gateway: REST APIs, HTTP APIs, Lambda & Security

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/Jw9OzYrLySQ"
  title="Session 16: Amazon API Gateway" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 **Session 16** of the [AWS Solutions Architect playlist](https://www.youtube.com/playlist?list=PLYmjGMwZ9N88) (Tamil) · [watch on YouTube](https://www.youtube.com/watch?v=Jw9OzYrLySQ)

## What you'll learn

- The **API gateway pattern**: routing, aggregation, auth, throttling and monitoring at one front door
- Trying it locally with **KrakenD** (class demo)
- **Amazon API Gateway**: REST vs HTTP vs WebSocket APIs
- Resources/routes, **integrations** (Lambda proxy, HTTP, AWS services), **stages** and deployments
- **Authentication and authorisation**: IAM, Cognito/JWT, Lambda authorizers
- **Throttling**, **API keys and usage plans**, **caching**, **CORS**, **custom domains**, **monitoring**

## 1. The API gateway pattern

**🧑 In plain words.** A hotel **front desk**. Guests don't wander into the kitchen or laundry;
they ask the desk, which checks their **room key** (auth), passes the request to the right
department (**routing**), sometimes gathers answers from several departments into **one reply**
(aggregation), and politely refuses someone ringing every ten seconds (**throttling**).

**❓ The problem it solves.** With many microservices, every client would need to know every service's
address, and every service would re-implement auth, rate limiting, TLS, CORS and logging, slightly
differently each time. Mobile apps would make many calls per screen.

**⚙️ How it works.** One entry point receives every request and applies **cross-cutting concerns**
centrally: TLS, authentication, authorisation, rate limiting, request validation, transformation,
routing to backends, response aggregation, caching, logging and metrics. Backends stay simple and
private.

**💡 Example.** A mobile "My account" screen calls `GET /customer/7` once; the gateway fans out to the
user, orders and wallet services and returns one combined JSON (the class aggregation demo below).

## 2. Try the pattern locally: KrakenD (class demo)

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

## 3. Amazon API Gateway: the three API types

```{raw} html
:file: ../diagrams/s16-apigw.html
```

**🧑 In plain words.** Three kinds of front desk: a **full-service concierge** (REST API), a **fast
self-service kiosk** (HTTP API), and a **hotline that stays open** for live two-way chat (WebSocket API).

**❓ The problem it solves.** Running your own gateway (KrakenD, NGINX, Kong) means servers to scale,
patch and keep highly available. API Gateway is **fully managed and serverless**: no servers, scales
automatically, pay per request.

**⚙️ How it works.**

| | **REST API** | **HTTP API** | **WebSocket API** |
|---|---|---|---|
| For | full-featured APIs | simple, fast, cheap APIs (most new Lambda / HTTP backends) | two-way real-time: chat, live dashboards, games |
| Price / latency | higher | **cheaper (about 70 % less) and lower latency** | per message + connection minutes |
| Auth | IAM, Cognito user pools, Lambda authorizers, **API keys + usage plans** | IAM, **JWT authorizers** (Cognito, Auth0, Google…), Lambda authorizers | IAM, Lambda authorizers |
| Extras | request validation, **caching**, **AWS WAF**, mapping templates, **private APIs**, edge-optimized endpoints, canary releases | automatic deployments, simple CORS, private integrations via VPC link | routes by message content (`$connect`, `$disconnect`, `$default`) |
| Endpoint types | edge-optimized, regional, private | regional | regional |

**💡 Example.** A startup's mobile backend on Lambda uses an **HTTP API** with a Cognito JWT authorizer;
its partner API, which needs API keys, quotas and WAF, uses a **REST API**; its live order-tracking uses a **WebSocket API**.

## 4. Routes, integrations, stages and deployments

**🧑 In plain words.** **Routes** are the desk's menu ("GET my bill"); the **integration** is which
department actually does the work; a **stage** is a copy of the whole desk (test desk vs live desk).

**❓ The problem it solves.** Mapping URLs to backends, and releasing changes safely.

**⚙️ How it works.**

| Term | Meaning |
|---|---|
| **Resource / route** | a path and method: `GET /courses/{id}` (`{id}` is a path parameter; `{proxy+}` catches everything) |
| **Integration** | what the route calls: **Lambda**, any **HTTP** URL, **AWS services directly** (e.g. put a message on SQS, write to DynamoDB) or a **mock** |
| **Lambda proxy integration** | passes the whole request (headers, path, query, body) to Lambda as an event and returns Lambda's `statusCode/headers/body` as the response (the common choice) |
| **VPC link** | reach private backends (ALB/NLB, Cloud Map) inside a VPC |
| **Stage** | a deployed version with its own URL and settings: `dev`, `prod` (`https://abc123.execute-api.ap-south-1.amazonaws.com/prod/courses/1`) |
| **Deployment** | a snapshot of the API published to a stage. REST APIs need an explicit **Deploy**; HTTP APIs can **auto-deploy** |
| **Stage variables** | per-stage settings, e.g. which Lambda alias to call |

**💡 Example.** `dev` stage → Lambda alias `dev`; `prod` stage → alias `prod`. Test in dev, then deploy
the same API definition to prod.

## 5. Authentication and authorisation

**🧑 In plain words.** Different ways to check the room key: a **staff badge** (IAM), a **hotel
loyalty card** issued by a trusted partner (JWT from Cognito/Google), or **asking the security office**
each time (Lambda authorizer).

**❓ The problem it solves.** Only allowed callers should reach the backend, without every service
writing its own login checks.

**⚙️ How it works.**

| Method | Who uses it | How |
|---|---|---|
| **IAM (SigV4)** | AWS principals: other services, internal tools | requests signed with AWS credentials; IAM policies allow `execute-api:Invoke` |
| **Cognito user pools / JWT authorizer** | app users | the client sends `Authorization: Bearer <JWT>`; the gateway verifies signature, issuer, audience, expiry and scopes |
| **Lambda authorizer** | custom logic | a Lambda checks a token/header (or calls your auth service) and returns an allow/deny policy; results can be cached |
| **Resource policy** (REST) | network-level rules | allow only certain IPs, VPCs or VPC endpoints (private APIs) |
| **API keys** | identifying partners for **usage plans** | **not** a security mechanism on their own |

**💡 Example.** An HTTP API JWT authorizer with issuer
`https://cognito-idp.ap-south-1.amazonaws.com/<pool-id>` rejects requests without a valid token with
**401**, so the Lambda never runs for anonymous callers.

## 6. Throttling, usage plans and caching

**🧑 In plain words.** The desk can only serve so many guests per second; VIP partners get a
**contract** with a monthly quota; and frequently asked answers are kept **on a sticky note**.

**❓ The problem it solves.** Protecting backends (and your bill) from floods, enforcing partner
limits, and making repeated reads faster and cheaper.

**⚙️ How it works.**

- **Throttling** uses a token bucket: by default about **10,000 requests per second** per account per
  Region with a **burst of 5,000**; set lower limits per stage, per route/method or per client.
  Over the limit → **429 Too Many Requests**.
- **Usage plans** (REST): attach **API keys** with a **quota** (per day/week/month) and **throttle**
  (rate + burst) per partner.
- **Caching** (REST): a per-stage cache (0.5 GB+, TTL default 300 s, max 3600 s) for GET responses.
- **Timeouts:** the integration timeout is **29 seconds** by default; long work should be asynchronous
  (queue to SQS, return `202 Accepted`, notify or poll later).
- **Payload limit:** 10 MB request size.

**💡 Example.** Partner "Gold" gets 1 million requests/month at 100 rps; partner "Free" gets 10,000/month
at 5 rps, enforced by two usage plans.

## 7. CORS, custom domains and monitoring

**🧑 In plain words.** **CORS** is telling browsers "pages from *this* other website may talk to me".
A **custom domain** puts your own name on the front desk. **Monitoring** is the desk's logbook.

**❓ The problem it solves.** Browser apps on another domain are blocked by default; customers expect
`api.yourcompany.com`; operations need visibility.

**⚙️ How it works.**

- **CORS:** configure allowed origins, methods and headers; the gateway answers browser **preflight**
  `OPTIONS` requests. (With Lambda proxy on REST APIs, your function must also return the CORS headers.)
- **Custom domains:** an **ACM** certificate (for **edge-optimized** REST APIs it must be in
  **us-east-1**; for regional, in the API's Region), a domain name mapping (base path → API/stage),
  and a Route 53 **Alias** record ([Session 14](14-route-53.md)).
- **Monitoring:** CloudWatch metrics `Count`, `Latency`, `IntegrationLatency`, `4XXError`, `5XXError`
  (and `CacheHitCount`); **access logs** in a format you choose; **execution logs** (REST); **X-Ray**
  tracing; **WAF** on REST APIs ([Session 12](12-aws-waf.md)).

**💡 Example.** `Latency` is 900 ms but `IntegrationLatency` is 880 ms: the time is spent in the
Lambda/backend, not in API Gateway.

## 8. Hands-on: HTTP API + Lambda

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

## Common mistakes

- **Treating an API key as authentication.** Use IAM, JWT/Cognito or a Lambda authorizer.
- **Changing a REST API and forgetting to *Deploy* it to the stage.**
- **Browser errors that are really CORS:** the API works with curl but not from the web app.
- **Long-running Lambda behind API Gateway:** the request fails at the integration timeout even if the function keeps running.
- **Choosing REST API by habit** when an HTTP API is enough, and paying more.

## Hands-on exercises

Local KrakenD exercises are **free**. API Gateway and Lambda have generous free tiers; ⚠️ delete
APIs, functions and custom domains at the end.

**Exercise 1 · Local routing.** Run the class `01.api_routing` stack and call both routes.

<details class="solution"><summary>Check</summary>

`curl localhost:8082/api/users/42` → John Doe; `curl localhost:8082/api/products/1` → MacBook Pro.
The services themselves aren't published on any host port: only the gateway is.

</details>

**Exercise 2 · Local aggregation.** Run `02.aggregation` and call `/customer/7`. Then stop the wallet
service and call it again. What does KrakenD return?

<details class="solution"><summary>What to notice</summary>

```bash
docker compose stop wallet-service
curl -s -D - localhost:8082/customer/7
```

```text
HTTP/1.1 200 OK
X-Krakend-Completed: false
{"orders":{"orders":[{"amount":500,"id":101},{"amount":900,"id":102}]},"user":{"email":"john@example.com","id":7,"name":"John Doe"}}
```

KrakenD still answers with the parts that worked (user and orders), drops `wallet`, and flags the
response as incomplete with `X-Krakend-Completed: false`: the screen can still show most of the data.

</details>

**Exercise 3 · Add a route.** In `01.api_routing`, add `GET /api/health` that maps to a new `/health`
endpoint on user-service. Rebuild and test.

<details class="solution"><summary>krakend.json addition</summary>

```json
{ "endpoint": "/api/health", "method": "GET",
  "backend": [{ "host": ["http://user-service:8000"], "url_pattern": "/health" }] }
```

Add `@app.get("/health")` returning `{"status": "UP"}` to user-service, then
`docker compose up -d --build`.

</details>

**Exercise 4 · Your first Lambda.** Create the `getCourse` Python Lambda from section 8 and test it in
the console with a test event containing `{"pathParameters": {"id": "42"}}`.

<details class="solution"><summary>Check</summary>

The test returns `statusCode 200` and body `{"id": "42", "title": "AWS Solutions Architect"}`.

</details>

**Exercise 5 · HTTP API + Lambda.** Create an HTTP API with route `GET /courses/{id}` to the Lambda and
call it with curl.

<details class="solution"><summary>CLI quick create</summary>

```bash
aws apigatewayv2 create-api --name courses-api --protocol-type HTTP \
    --target arn:aws:lambda:ap-south-1:<acct>:function:getCourse
# quick create makes a $default route; then add the permission:
aws lambda add-permission --function-name getCourse --statement-id apigw \
    --action lambda:InvokeFunction --principal apigateway.amazonaws.com
curl https://<api-id>.execute-api.ap-south-1.amazonaws.com/courses/42
```

(With quick create the Lambda receives every path; the console route-based setup gives you `{id}`.)

</details>

**Exercise 6 · See the event.** Change the Lambda to `print(json.dumps(event))`, call the API with a
query string and a header, and read the event in CloudWatch Logs.

<details class="solution"><summary>What to look for</summary>

`rawPath`, `pathParameters`, `queryStringParameters`, `headers` (lowercased),
`requestContext.http.sourceIp`: everything the proxy integration passes to Lambda.

</details>

**Exercise 7 · Throttle it.** Set the `$default` stage's throttling to rate 2, burst 2, and fire 20 quick requests.

<details class="solution"><summary>Test</summary>

```bash
for i in $(seq 20); do curl -s -o /dev/null -w "%{http_code} " https://<api>/courses/1; done; echo
```

Most come back **429**. Restore normal limits afterwards.

</details>

**Exercise 8 · JWT auth (optional).** Create a Cognito user pool and app client, add a **JWT
authorizer** to the route, and call it with and without an ID token.

<details class="solution"><summary>Expected</summary>

Without a token: **401 Unauthorized** and the Lambda never runs. With `Authorization: Bearer <id_token>`
from a signed-in Cognito user: 200.

</details>

**Exercise 9 · API keys and usage plans (REST).** Build a REST API version of the endpoint, require an
API key, attach a usage plan (quota 100/day, rate 5), and test with and without `x-api-key`.

<details class="solution"><summary>Expected</summary>

Without the key: **403 Forbidden**. With the key: 200, until the quota or rate limit → 429. Remember:
deploy the REST API to a stage after every change.

</details>

**Exercise 10 · CORS.** Serve a small HTML page from `localhost` that calls your API with `fetch()`.
See the browser error, then configure CORS (allowed origin `http://localhost:8000`, method GET).

<details class="solution"><summary>What to notice</summary>

Before: the browser console shows *blocked by CORS policy* even though curl works. After configuring
CORS on the HTTP API, the response includes `access-control-allow-origin` and the page shows the data.

</details>

**Exercise 11 · Metrics.** After the exercises, open CloudWatch metrics for the API and compare
`Latency` with `IntegrationLatency`, and find the 4XX count from Exercises 7–9.

<details class="solution"><summary>Where</summary>

CloudWatch → Metrics → **ApiGateway** → by API (HTTP APIs use `ApiId` + `Stage`). The difference
between Latency and IntegrationLatency is API Gateway's own overhead.

</details>

**Exercise 12 · Custom domain (optional).** With your Route 53 domain, create an ACM certificate for
`api.yourdomain.com` (regional), a custom domain mapping to your HTTP API, and an Alias record.

<details class="solution"><summary>Check</summary>

`curl https://api.yourdomain.com/courses/42` works with a valid certificate. The Alias points to the
custom domain's **API Gateway domain name** (`d-xxxx.execute-api.ap-south-1.amazonaws.com`).

</details>

**Exercise 13 · Clean up.** Delete the APIs (HTTP and REST), usage plans, API keys, the custom domain,
the Cognito pool, the Lambda and its log group; `docker compose down` the local stacks.

<details class="solution"><summary>Check</summary>

API Gateway console: no APIs. Lambda: function deleted. `docker ps` shows no KrakenD containers.

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
