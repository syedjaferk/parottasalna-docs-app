# Chapter 21 · What is an API?

## The big idea

An **API** (application programming interface) is a **contract between two programs**: "if you send
me *this*, I will send you back *that*". It lets software cooperate without knowing each other's insides.

**Everyday example:** a restaurant menu. You never walk into the kitchen. You pick from the menu (the
API), a waiter carries the order, and the kitchen can swap its chef or stove without you noticing, as
long as the menu keeps working.

```{raw} html
:file: ../diagrams/apis.html
```

## Where APIs show up

| Kind | Example | Who calls it |
|---|---|---|
| **Web / public API** | Google Maps API, Stripe API | Other companies' apps |
| **Private / internal API** | Order service calling the payment service | Your own services |
| **Library API** | `requests.get(...)` in Python | Your own code |
| **Operating-system API** | "open this file" | Programs |
| **Hardware API** | Camera access on a phone | Apps |

In system design, "design the API" almost always means the **web API** between a client and your
servers, or between two of your services.

## The anatomy of a web API call

Every call has four parts:

1. **Where:** a URL (`https://api.shop.example.com/v1/orders/42`)
2. **What to do:** an operation (HTTP method `GET`, `POST`...)
3. **What I send:** headers (who am I) and an optional body (data)
4. **What I get back:** a status code and a body

```python
# A tiny "API" implemented as plain functions, to see the contract clearly
orders = {42: {"id": 42, "item": "Masala tea", "qty": 2, "status": "paid"}}

def api_get_order(order_id):
    """GET /v1/orders/{id}"""
    order = orders.get(order_id)
    if order is None:
        return 404, {"error": "order not found"}
    return 200, order

def api_create_order(body):
    """POST /v1/orders"""
    if "item" not in body or body.get("qty", 0) < 1:
        return 400, {"error": "item and a positive qty are required"}
    new_id = max(orders) + 1
    orders[new_id] = {"id": new_id, "status": "pending", **body}
    return 201, orders[new_id]

print(api_get_order(42))
print(api_get_order(7))
print(api_create_order({"item": "Filter coffee", "qty": 1}))
print(api_create_order({"item": "Tea"}))
```

**Output:**

```text
(200, {'id': 42, 'item': 'Masala tea', 'qty': 2, 'status': 'paid'})
(404, {'error': 'order not found'})
(201, {'id': 43, 'status': 'pending', 'item': 'Filter coffee', 'qty': 1})
(400, {'error': 'item and a positive qty are required'})
```

Notice what a client can rely on: **the shape of requests, the shape of responses, and the status
codes**. The server's database, language and servers could change completely and the client would
never know.

## What makes an API good

- **Predictable:** same style everywhere (names, errors, pagination).
- **Minimal:** easy to use correctly, hard to use wrongly.
- **Stable:** old clients keep working; change by **adding**, not by breaking.
- **Documented:** an OpenAPI/Swagger description is the source of truth.
- **Secure:** authentication, authorisation, input validation, rate limits.
- **Efficient:** pagination, filtering, small responses, caching headers.

## Styles you will compare

- **REST:** resources and HTTP verbs over JSON.
- **GraphQL:** one endpoint, the client picks the fields.
- **RPC / gRPC:** call a remote function.
- **Event-based:** WebSockets, webhooks, message queues for pushes.

The next chapters take each in turn.

## Public vs internal API decisions

| Question | Public API | Internal API |
|---|---|---|
| Who are the clients? | Unknown, many | Teams you know |
| Can you change it freely? | **No** (versioning, long deprecation) | Easier (coordinate) |
| Authentication | API keys, OAuth | Service identity (mTLS) |
| Protocol | REST (easy for everyone) | gRPC (fast) |
| Rate limits | Essential | Often looser |

## Common mistakes

:::{warning}
- Designing the API around your **database tables** instead of what the client needs to do.
- Changing a response field's meaning without versioning.
- Treating the API as an afterthought, then living with it for ten years.
- Returning different error shapes from different endpoints.
:::

## Try it yourself

1. In the code above, what status code would you return if a client tries to create an order with a negative quantity?
2. Why is it a bad idea to expose database column names directly as API fields?
3. A mobile app is released and cannot be force-updated. What does that imply for how you change your API?

<details class="solution"><summary>Answers</summary>

1. `400 Bad Request` (or `422 Unprocessable Entity`), with a clear message.
2. A schema change in the database would break every client. The API should be a **stable contract** that you can map to whatever storage you like.
3. Old app versions will call the API for months or years. Version the API, only make **additive** changes, and support old versions until usage drops.

</details>

:::{admonition} Next
:class: important
The most common style, in depth, against its modern rival: [REST vs GraphQL](22-rest-vs-graphql.md).
:::
