# Chapter 3 · APIs, data model and choosing a database

## The big idea

Once you know **what** the system does and **how big** it is, define how the outside world talks to
it (the API) and what it remembers (the data model). Then pick a store based on **how the data is read**,
not on what you used last time.

```{raw} html
:file: ../diagrams/apis.html
```

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

## A worked example: a chat app

Requirements: send a message to a person or a group, read the latest messages of a conversation.

**1. List the entities and the queries first.**

| Query | How often |
|---|---|
| Latest 50 messages of conversation X | Constantly (every screen open) |
| Append a message to conversation X | Constantly |
| List my conversations, newest first | Often |
| Search messages | Rare |

**2. Design the API from those queries.**

```text
POST /v1/conversations/{id}/messages     {"text": "hello"}                   -> 201 {"id": 981, "sent_at": "..."}
GET  /v1/conversations/{id}/messages?limit=50&before=981                       -> 200 {"messages": [...], "next_before": 931}
GET  /v1/conversations?limit=20&cursor=...                                      -> 200 {"conversations": [...]}
```

Notice the **cursor pagination** (`before=981`), which stays correct while new messages arrive. Offset pagination
(`offset=100000`) gets slower and skips or repeats rows as data changes.

**3. Shape the data around the query.**

```sql
-- Relational version: fine up to a very large size
CREATE TABLE messages (
  conversation_id BIGINT NOT NULL,
  id              BIGINT NOT NULL,          -- time-ordered id (Snowflake style)
  sender_id       BIGINT NOT NULL,
  text            TEXT,
  sent_at         TIMESTAMP NOT NULL,
  PRIMARY KEY (conversation_id, id)         -- one conversation's messages are stored together, newest last
);
-- "latest 50 of conversation X" becomes one index range scan:
--   SELECT * FROM messages WHERE conversation_id = ? AND id < ? ORDER BY id DESC LIMIT 50;
```

At billions of messages per day the same shape moves to a wide-column store (partition key `conversation_id`,
clustering key `id`), which is why choosing the key from the query matters more than the brand of database.

## From data model to database: a decision you can defend

```python
def suggest_store(needs_transactions, needs_joins, access, scale):
    if needs_transactions or needs_joins:
        return "relational database (add replicas, then shard only if the numbers demand it)"
    if access == "by key" and scale == "huge":
        return "key-value or wide-column store, partitioned by the lookup key"
    if access == "documents":
        return "document store"
    if access == "search":
        return "a search engine next to the main database"
    return "relational database: the safe default"

cases = [
    ("bank transfers", dict(needs_transactions=True, needs_joins=True, access="rows", scale="large")),
    ("URL shortener", dict(needs_transactions=False, needs_joins=False, access="by key", scale="huge")),
    ("product catalogue", dict(needs_transactions=False, needs_joins=False, access="documents", scale="large")),
    ("a small blog", dict(needs_transactions=False, needs_joins=False, access="rows", scale="small")),
]
for name, params in cases:
    print(f"{name:<18} -> {suggest_store(**params)}")
```

**Output:**

```text
bank transfers     -> relational database (add replicas, then shard only if the numbers demand it)
URL shortener      -> key-value or wide-column store, partitioned by the lookup key
product catalogue  -> document store
a small blog       -> relational database: the safe default
```

The later chapters on [SQL vs NoSQL](30-sql-vs-nosql.md), [indexes](31-database-indexes.md) and
[API design](24-api-design.md) go deep on each of these choices.

## Common mistakes

- Choosing the database before listing the queries.
- Putting a long URL in a URL path.
- Forgetting expiry, validation or rate limits.

## Try it yourself

1. Design the endpoints and the key for "a user's last 20 notifications".
2. Why is `?offset=100000` a poor pagination method?
3. For each of these, which store: shopping cart, bank ledger, product search?

<details class="solution"><summary>Answers</summary>

1. `GET /v1/users/{id}/notifications?limit=20&before=<cursor>`; key `(user_id, notification_id)` with ids ordered by time, so the latest 20 are one contiguous read.
2. The database must walk past 100,000 rows to reach the page, so it gets slower the deeper you go, and rows can be skipped or repeated when data changes. Use a cursor (`before=<id>`).
3. Cart: key-value store (Redis or DynamoDB). Ledger: relational (ACID). Search: a search engine (Elasticsearch).

</details>

:::{admonition} Try it in the playground
:class: important
In the [TinyURL problem](/system-design/tinyurl/) you design the endpoints, decide between 301 and 302
and pick the store.
:::

:::{admonition} Next
:class: important
With the routine in hand, we now go deep on each building block, one concept per chapter, starting with [scalability](04-scalability.md).
:::
