# Chapter 22 · REST vs GraphQL

## The big idea

Both are ways to build a web API. They differ in **who decides the shape of the response**:

- **REST:** the **server** decides. Each URL returns a fixed shape.
- **GraphQL:** the **client** decides. It describes exactly which fields it wants.

**Everyday example:** a fixed-price **thali** versus an **a-la-carte** menu. A thali (REST) gives you the
same set of dishes whether you are hungry or not. A-la-carte (GraphQL) lets you ask for just the two
curries you want, and everything arrives on one tray.

```{raw} html
:file: ../diagrams/rest-vs-graphql.html
```

## REST: resources and verbs

Model the world as **resources** with URLs and use HTTP methods on them:

```text
GET    /books            list books
POST   /books            create a book
GET    /books/42         read book 42
PUT    /books/42         replace book 42
PATCH  /books/42         change some fields
DELETE /books/42         delete book 42
GET    /books/42/reviews reviews of book 42       (a nested resource)
```

Strengths: simple, uses HTTP properly (caching, status codes), easy to debug with `curl`, understood by
everyone, **CDN-friendly** for GET requests.

## GraphQL: ask for exactly what you need

One endpoint, usually `POST /graphql`. The client sends a **query** shaped like the data it wants:

```graphql
query {
  book(id: 42) {
    title
    author { name }
    reviews(limit: 2) { rating text }
  }
}
```

Response (exactly those fields, nothing more):

```json
{"data": {"book": {"title": "Dune", "author": {"name": "Frank Herbert"},
                   "reviews": [{"rating": 5, "text": "Classic"}, {"rating": 4, "text": "Dense"}]}}}
```

A GraphQL server has a **schema** (types and fields) and **resolvers** (functions that fetch each field).
Besides **queries** (read) it supports **mutations** (write) and **subscriptions** (live updates).

## The problem GraphQL solves: over- and under-fetching

- **Over-fetching:** the endpoint returns 40 fields; the screen needs 3. Wastes bandwidth.
- **Under-fetching:** one endpoint is not enough, so the client makes **several round trips**
  (`/books/42`, then `/authors/7`, then `/books/42/reviews`). On a slow mobile network each trip hurts.

```python
# The same book screen, REST vs GraphQL, counting round trips and bytes
BOOK = {"id": 42, "title": "Dune", "author_id": 7, "isbn": "978...", "pages": 412, "language": "en",
        "publisher": "Chilton", "year": 1965, "price": 499, "stock": 18}
AUTHOR = {"id": 7, "name": "Frank Herbert", "born": 1920, "bio": "x" * 400}
REVIEWS = [{"rating": 5, "text": "Classic"}, {"rating": 4, "text": "Dense"}, {"rating": 3, "text": "Slow"}]

import json
def size(obj):
    return len(json.dumps(obj))

# REST: three calls, each returns the full resource
rest_bytes = size(BOOK) + size(AUTHOR) + size(REVIEWS)
print(f"REST   : 3 round trips, {rest_bytes} bytes")

# GraphQL: one call, only the requested fields
needed = {"book": {"title": BOOK["title"], "author": {"name": AUTHOR["name"]},
                   "reviews": REVIEWS[:2]}}
print(f"GraphQL: 1 round trip , {size(needed)} bytes")
```

**Output:**

```text
REST   : 3 round trips, 714 bytes
GraphQL: 1 round trip , 143 bytes
```

On a 150 ms mobile connection, two saved round trips are 300 ms the user does not wait.

## Side by side

| | REST | GraphQL |
|---|---|---|
| Endpoints | Many (`/books`, `/authors`) | One (`/graphql`) |
| Response shape | Fixed by the server | Chosen by the client |
| Round trips for related data | Often several | Usually one |
| HTTP caching, CDN | **Easy** (GET + URL) | **Hard** (POST, every query differs) |
| Error handling | HTTP status codes | Always `200`; errors inside the body |
| Versioning | `/v1`, `/v2` | Evolve the schema; deprecate fields |
| File upload, streaming | Natural | Awkward |
| Learning curve | Low | Medium |
| Main risk | Over/under-fetching | **Expensive queries** (deeply nested), N+1 resolver calls |

## The N+1 problem and query cost

If a query asks for 50 books **and each book's author**, a naive resolver runs **1 query for books +
50 queries for authors**. Fix with **batching** (DataLoader: collect all author ids, fetch once).
Also protect the server: limit **query depth, complexity** and use **persisted queries**.

## When to choose which

| Situation | Choose |
|---|---|
| Public API for third parties | **REST**: simple, cacheable, universal |
| Simple CRUD service | **REST** |
| Many client types (web, iOS, Android) with different data needs | **GraphQL** in front of your services |
| Product team changes the UI weekly | **GraphQL** (no new endpoint per screen) |
| Heavily cached read traffic (CDN) | **REST** |
| Internal, high-volume service calls | **gRPC** (see REST vs RPC) |

A common real-world setup: **REST or gRPC between services; GraphQL as a gateway for the front-ends**.

## Common mistakes

:::{warning}
- Choosing GraphQL "because it is modern" for a simple CRUD API: you gain a caching and security problem.
- Exposing GraphQL with no depth or complexity limits (one query can take down the server).
- Returning `200 OK` for every REST error. REST has status codes; use them.
- Forgetting the N+1 problem in resolvers.
:::

## Try it yourself

1. A home screen needs the user name, 3 latest orders and the unread notification count. Compare the REST and GraphQL approaches.
2. Why is it harder to put a CDN in front of GraphQL than in front of REST?
3. What is the N+1 problem and how do you fix it?

<details class="solution"><summary>Answers</summary>

1. REST: three calls (`/me`, `/orders?limit=3`, `/notifications/unread-count`) or one custom endpoint. GraphQL: one query naming those fields.
2. A CDN caches by URL. GraphQL sends different queries to the same URL via POST, so there is nothing stable to cache (unless you use persisted queries over GET).
3. A list query triggers one extra query per item. Fix with batching (e.g. DataLoader) or a join so related data is fetched in one or two queries.

</details>

:::{admonition} Next
:class: important
One door for all those APIs: the [API gateway](23-api-gateway.md).
:::
