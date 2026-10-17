# Chapter 23 · API gateway

## The big idea

With many services behind your product, clients should not need to know about all of them. An **API
gateway** is the **single front door**: it receives every external request, checks who you are, applies
limits, and forwards the call to the right service.

**Everyday example:** the reception desk of a big office tower. Visitors do not wander the floors. The
desk checks ID, logs the visit, controls crowding and points you to the right office.

```{raw} html
:file: ../diagrams/api-gateway.html
```

## What a gateway does

| Job | Detail |
|---|---|
| **Routing** | `/orders/*` to the order service, `/users/*` to the user service |
| **Authentication** | Verify the token once, pass the user id to services |
| **Authorization** | Coarse checks (is this client allowed to call this API at all?) |
| **Rate limiting and quotas** | Protect services; enforce per-customer plans |
| **TLS termination** | HTTPS handled in one place |
| **Request / response shaping** | Transform formats, aggregate several calls into one |
| **Caching** | Serve repeated GETs directly |
| **Observability** | Central logs, metrics, trace ids |
| **Resilience** | Timeouts, retries, circuit breaking toward services |

## A minimal gateway in code

```python
# routing, authentication and rate limiting in one place
ROUTES = {"/orders": "order-service", "/users": "user-service"}
TOKENS = {"tok_asha": "asha", "tok_ravi": "ravi"}
calls = {}

def gateway(path, token):
    user = TOKENS.get(token)
    if user is None:
        return 401, "unauthenticated"
    calls[user] = calls.get(user, 0) + 1
    if calls[user] > 3:                               # 3 calls per window for the demo
        return 429, "slow down"
    for prefix, service in ROUTES.items():
        if path.startswith(prefix):
            return 200, f"forwarded to {service} for {user}"
    return 404, "no such route"

print(gateway("/orders/9", "tok_asha"))
print(gateway("/users/1", "wrong"))
print(gateway("/payments", "tok_ravi"))
for _ in range(3):
    last = gateway("/orders/9", "tok_asha")
print(last)
```

**Output:**

```text
(200, 'forwarded to order-service for asha')
(401, 'unauthenticated')
(404, 'no such route')
(429, 'slow down')
```

Real gateways do exactly this, plus TLS, caching and metrics, in highly optimised code.

## Request flow through a gateway

1. Client sends `GET /orders/9` with a token.
2. Gateway **terminates TLS** and **validates the token**.
3. It checks **rate limits** and quotas for this customer.
4. It **routes** `/orders/*` to the order service (via service discovery).
5. The service replies; the gateway may **cache** it, **transform** it and **log** it with a trace id.

## Gateway vs load balancer vs reverse proxy

| | Load balancer | Reverse proxy | API gateway |
|---|---|---|---|
| Spreads load over identical servers | Yes | Yes | Yes |
| TLS, caching, compression | Sometimes | Yes | Yes |
| Understands APIs (auth, quotas, per-client plans) | No | Limited | **Yes** |
| Routes to **different** services | Limited | Yes | **Yes** |
| Aggregates several calls into one | No | No | **Yes** |

## Backend for Frontend (BFF)

Mobile and web need different data shapes. Run **one gateway per client type**, each shaped for its
client, instead of one gateway that serves everyone badly.

## Risks and how to handle them

- **SPOF:** run several instances across zones.
- **Bottleneck:** keep it thin; no business logic. Scale horizontally.
- **Latency:** one extra hop, so keep gateway work fast and local (verify tokens without a database call).
- **Becoming a monolith:** the moment business rules move in, every team must change it. Keep it to
  cross-cutting concerns.

Examples of products: **AWS API Gateway, Kong, Apigee, Envoy, Nginx, Traefik**.

## Common mistakes

:::{warning}
- Putting business logic in the gateway.
- A single gateway instance.
- Letting internal services trust each other with no authentication "because they are behind the gateway".
- Inconsistent error shapes between services, so clients need special cases.
:::

## Try it yourself

1. List five things an API gateway does before a request reaches a service.
2. A mobile app and a web app need different JSON shapes from the same services. Which pattern fits?
3. Why should the gateway verify tokens locally instead of calling the auth service on every request?

<details class="solution"><summary>Answers</summary>

1. Terminate TLS, authenticate the token, authorise coarsely, rate limit, route, log and attach a trace id.
2. **Backend for Frontend (BFF)**: one gateway layer per client type.
3. A call per request makes the auth service a bottleneck and a SPOF and adds latency. Signed tokens (JWT) can be verified locally with a public key.

</details>

:::{admonition} Next
:class: important
What makes a good API contract in the first place: [API design](24-api-design.md).
:::
