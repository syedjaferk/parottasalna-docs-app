# Chapter 3 · APIs, data model and choosing a database

## The big idea

Once you know **what** the system does and **how big** it is, define how the outside world talks to
it (the API) and what it remembers (the data model). Then pick a store based on **how the data is read**,
not on what you used last time.

## Designing the API

For each feature write the verb, the path, the input and the output.

```text
POST /api/v1/urls            body: { long_url, alias?, expires_at? }   ->  201 { short_url }
GET  /{code}                                                          ->  302 Location: long_url
```

Good habits:

- Use **GET** for reads that change nothing, **POST** to create. Never create data with GET.
- Use **versioning** (`/v1/`) and clear status codes (`201` created, `404` unknown, `410` expired).
- Say how you would **protect** it: API key, rate limit, input validation.
- **301 or 302?** A 301 is cached by browsers, so later clicks never reach you (fast, but no analytics and
  no expiry). A 302 sends every click through your server. Pick on purpose.

## The data model

List the entities and the fields. For the shortener it is one entity:

| Field | Type | Note |
|---|---|---|
| short_code | string, primary key | 6-7 base62 characters |
| long_url | string | validated |
| created_at, expires_at | timestamps | expiry optional |
| owner_id | id | optional |

## Choosing a store from the access pattern

| If you mostly need... | Consider |
|---|---|
| Joins, transactions, flexible queries | Relational database |
| Look up one value by key, huge scale | **Key-value store** |
| Heavy writes, time-ordered data | Wide-column store |
| Flexible, nested documents | Document store |
| Full-text search | Search index |

The shortener only ever asks *"give me the row for this code"*. There are no joins and billions of
rows, so a key-value or wide-column store fits. A sharded relational database also works if you explain it.

## Common mistakes

- Choosing the database before listing the queries.
- Putting a long URL in a URL path.
- Forgetting expiry, validation or rate limits.

:::{admonition} Try it in the playground
:class: important
In the [TinyURL problem](/system-design/tinyurl/) you design the endpoints, decide between 301 and 302
and pick the store.
:::
