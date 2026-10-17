# Chapter 24 · API design

## The big idea

A well-designed API is easy to use correctly, hard to misuse, and survives years of change. In an
interview it is step 3 of the framework: **define the operations, inputs, outputs and errors** before
drawing boxes.

**Everyday example:** the controls of a car. Every car has pedals and a steering wheel in the same
places, with the same meaning. A new driver is productive in minutes. A badly designed API is a car with
the brake on the left in one model and on the right in another.

```{raw} html
:file: ../diagrams/api-design.html
```

## The design checklist

Use this in the "API and data model" step of an interview.

**1. Resources and URLs**

- Plural nouns: `/orders`, `/orders/{id}/items`.
- Keep nesting shallow (two levels).

**2. Methods and codes**

- Correct verbs; `201` with a `Location` header on creation; `204` for success with no body.
- `400` validation, `401` unauthenticated, `403` forbidden, `404` missing, `409` conflict,
  `422` semantic error, `429` rate limited.

**3. Consistent error format**

```json
{
  "error": {
    "code": "out_of_stock",
    "message": "Only 2 units of item 42 are left",
    "request_id": "req_8f2a"
  }
}
```

**4. Pagination, filtering, sorting**

`GET /orders?status=paid&sort=-created_at&limit=20&cursor=eyJpZCI6MTAwfQ`

**5. Versioning**

`/v1/orders` (simple) or a header. Never break existing clients silently; support old versions for a
published period.

**6. Idempotency for writes**

Accept an `Idempotency-Key` header on `POST` so retries are safe (next-but-one chapter).

**7. Security**

HTTPS only, short-lived tokens, least-privilege scopes, validate every input, never put secrets in URLs.

**8. Documentation and evolution**

OpenAPI spec as the source of truth; additive changes only (new optional fields), deprecate loudly.

## Request and response examples

```text
POST /v1/orders
Idempotency-Key: 7c1f-...
Authorization: Bearer <token>
Content-Type: application/json

{"customer_id": 17, "items": [{"sku": "TEA-250", "qty": 2}]}

HTTP/1.1 201 Created
Location: /v1/orders/9001
{"id": 9001, "status": "pending", "total": 500}
```

## A worked design: a food-delivery order API

Requirements: customers place orders, see them, cancel while pending.

```text
POST   /v1/orders                 place an order            -> 201 + Location
GET    /v1/orders/{id}            read one order            -> 200 / 404
GET    /v1/orders?status=active   list my orders (paged)    -> 200
POST   /v1/orders/{id}/cancel     cancel (an action)        -> 200 / 409 if already cooking
```

Design decisions worth saying out loud:

- Cancelling is an **action**, not CRUD, so `POST /orders/{id}/cancel` reads better than `DELETE`.
- `409 Conflict` when the order can no longer be cancelled.
- Prices are computed **on the server**; the client sends item ids and quantities only.
- `Idempotency-Key` on `POST /orders` so a double tap on a flaky network does not order twice.

## Validate in code

```python
def validate_order(body):
    errors = []
    if not isinstance(body.get("items"), list) or not body["items"]:
        errors.append("items must be a non-empty list")
    else:
        for i, item in enumerate(body["items"]):
            if item.get("qty", 0) < 1 or item.get("qty", 0) > 50:
                errors.append(f"items[{i}].qty must be between 1 and 50")
            if "sku" not in item:
                errors.append(f"items[{i}].sku is required")
    return errors

print(validate_order({"items": [{"sku": "TEA-250", "qty": 2}]}))
print(validate_order({"items": [{"sku": "TEA-250", "qty": 99}, {"qty": 1}]}))
print(validate_order({}))
```

**Output:**

```text
[]
['items[0].qty must be between 1 and 50', 'items[1].sku is required']
['items must be a non-empty list']
```

Return **all** validation errors at once in a `400`/`422` body so clients can fix everything in one go.

## Evolving an API without breaking clients

| Change | Safe? |
|---|---|
| Add an optional request field | Yes |
| Add a field to a response | Yes (clients must ignore unknown fields) |
| Rename or remove a field | **No**: new version |
| Change a field's type or meaning | **No** |
| Make an optional field required | **No** |

Run **deprecation** properly: announce, add a `Deprecation` or `Sunset` header, measure who still
calls the old version, then retire.

## Common mistakes

:::{warning}
- Verbs in URLs (`/getOrders`, `/createUser`).
- Returning `200 OK` with `{"error": ...}` in the body.
- Unbounded list endpoints with no pagination.
- Trusting the client to send prices, totals or user ids.
- Changing response shapes in place instead of versioning.
:::

## Try it yourself

1. Design endpoints for a library: list books, borrow a book, return a book, list a member's loans.
2. A client sends `{"price": 1}` for an item that costs 500. How should your API behave and why?
3. List three backwards-compatible and three breaking changes to a response.

<details class="solution"><summary>Answers</summary>

1. `GET /books`, `POST /loans` (body: book_id, member_id), `POST /loans/{id}/return`, `GET /members/{id}/loans`.
2. Ignore client-supplied prices entirely; look up the price on the server. Never trust amounts from the client.
3. Compatible: add an optional field, add a new endpoint, add a new enum value clients tolerate. Breaking: remove a field, rename a field, change a type.

</details>

:::{admonition} Next
:class: important
Some data must be pushed to the client as it happens: [WebSockets](25-websockets.md).
:::
