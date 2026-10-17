# Chapter 69 · REST vs RPC

## The big idea

Two ways to design how programs call each other over a network:

- **REST** thinks in **things (resources)**: "here is order 42; GET it, change it, delete it".
- **RPC** (remote procedure call) thinks in **actions (functions)**: "call `PlaceOrder(...)` on that machine as if it were a local function".

**Everyday example:** a **library**. In the REST style you ask for **things by their catalogue address**: "give me
book 42", "add a note to book 42", "remove book 42". The few actions (get, add, remove) are the same for every
book. In the RPC style you ask the librarian to **perform specific tasks**: "reserve this book for me",
"transfer it to the Pune branch", "recommend something like it". There is a custom verb for each.

```{raw} html
:file: ../diagrams/rest-vs-rpc.html
```

## The same feature, both ways

Cancel an order:

```text
REST                                       RPC (gRPC / JSON-RPC)
-----------------------------------        ------------------------------------------
PATCH  /orders/42  {"status":"cancelled"}  POST /rpc  {"method": "CancelOrder", "params": {"order_id": 42}}
(or)   POST /orders/42/cancel               OrderService.CancelOrder(CancelOrderRequest{order_id: 42})
Read:  GET /orders/42                       OrderService.GetOrder(GetOrderRequest{order_id: 42})
```

## How they differ

| | **REST** | **RPC (e.g. gRPC)** |
|---|---|---|
| Mental model | **Nouns**: resources with URLs, uniform verbs | **Verbs**: named functions |
| Interface | HTTP methods + URLs + status codes | A **schema** of functions and message types (`.proto`) |
| Coupling | **Loose**: clients follow documented resources | **Tighter**: client stubs generated from the schema |
| Format | Usually JSON (text, human readable) | Often **binary** (Protocol Buffers): smaller and faster |
| Transport | HTTP/1.1 or 2 | gRPC: **HTTP/2** (multiplexing, streaming) |
| Caching | **Excellent** (HTTP caches, CDN on GET) | Poor / custom |
| Streaming | Awkward | **Native** (server, client, bidirectional) |
| Browser support | **Native** | Needs gRPC-Web or a proxy |
| Typing and codegen | Optional (OpenAPI) | **Built in**: type-safe clients in many languages |
| Performance | Good | **Better** (smaller payloads, binary parsing, HTTP/2) |
| Debuggability | **Easy**: `curl`, browser, readable payloads | Needs tooling (grpcurl, reflection) |
| Evolution | Add fields; version URLs | Add optional fields with new field numbers; strong compatibility rules |
| Best for | **Public APIs**, browsers, CRUD, cacheable reads | **Internal service-to-service**, low latency, streaming, polyglot teams |

## What the payload difference means

```python
import json, struct

order = {"order_id": 42, "customer_id": 17, "quantity": 3, "price_paise": 49900}

as_json = json.dumps(order, separators=(",", ":")).encode()

# A hand-rolled binary layout like Protocol Buffers uses: fixed field order, no field names on the wire
as_binary = struct.pack(">IIHI", order["order_id"], order["customer_id"], order["quantity"], order["price_paise"])

print("JSON   :", len(as_json), "bytes ->", as_json.decode())
print("binary :", len(as_binary), "bytes ->", as_binary.hex())
print(f"binary is {len(as_json) / len(as_binary):.1f}x smaller; at 20,000 calls per second that saves {(len(as_json) - len(as_binary)) * 20_000 / 1e6:.1f} MB/s")
```

**Output:**

```text
JSON   : 65 bytes -> {"order_id":42,"customer_id":17,"quantity":3,"price_paise":49900}
binary : 14 bytes -> 0000002a0000001100030000c2ec
binary is 4.6x smaller; at 20,000 calls per second that saves 1.0 MB/s
```

JSON repeats every field name in every message and writes numbers as text. A schema-based binary format sends
only values (the schema is known to both sides), which also parses faster.

## What the interface looks like

**REST (OpenAPI description, shortened):**

```yaml
paths:
  /orders/{id}:
    get:    {summary: Read an order, responses: {200: {description: The order}, 404: {description: Not found}}}
    delete: {summary: Cancel an order, responses: {204: {description: Cancelled}}}
```

**gRPC (Protocol Buffers):**

```text
service OrderService {
  rpc GetOrder    (GetOrderRequest)    returns (Order);
  rpc CancelOrder (CancelOrderRequest) returns (CancelOrderResponse);
  rpc WatchOrders (WatchRequest)       returns (stream OrderEvent);   // server streaming
}
message GetOrderRequest { int64 order_id = 1; }
```

The generated client lets you write `client.CancelOrder(order_id=42)`: it feels like a **local function call**.

## The danger of pretending a remote call is local

RPC's convenience hides the **fallacies of distributed computing**: the network is **not** reliable, latency is
**not** zero, bandwidth is **not** infinite. A remote call can **time out**, **fail halfway** or be
**delivered twice**. Always add **timeouts, retries (with idempotency), deadlines and error handling**. This is the
core argument people make for REST's explicit, resource-based, cache-friendly style at the edges of a system.

## Where each wins

**Choose REST when:**

- The API is **public** or used by many unknown clients, including **browsers**.
- Reads are cacheable and you want **CDN** support.
- The domain maps naturally to resources and CRUD.
- You value simplicity and debuggability.

**Choose RPC (gRPC) when:**

- **Internal service-to-service** traffic with high volume and tight latency budgets.
- You need **streaming** (live feeds, bidirectional chat) or **long-lived** calls.
- Many languages need **type-safe generated clients** and a strict contract.
- Actions do not fit CRUD (`ResizeImage`, `StartDeployment`, `RecalculateInvoice`).

### Typical modern architecture

```text
Browsers / mobile  --REST or GraphQL-->  API gateway  --gRPC-->  internal services  --gRPC-->  more services
```

REST (or GraphQL) at the **edge**, gRPC **inside**. The gateway translates.

## Other RPC flavours

- **gRPC:** Protocol Buffers over HTTP/2. Today's default.
- **JSON-RPC, XML-RPC:** simple RPC over HTTP with text payloads.
- **Thrift, Avro:** other schema-based binary RPC systems (Facebook, Hadoop).
- **GraphQL** is a third approach: client-shaped queries over a single endpoint (see REST vs GraphQL).
- **Older:** CORBA, Java RMI, SOAP: heavier, mostly legacy.

## Common mistakes

:::{warning}
- Treating RPC calls like local calls: no timeouts, no retries, no idempotency.
- Exposing gRPC directly to browsers without a gateway (gRPC-Web).
- "REST" APIs that are really RPC over POST (`POST /doEverything`) and lose the benefits of both.
- Breaking a `.proto` contract (reusing or renumbering fields).
- Using REST internally for a latency-critical, high-volume path where binary RPC would save a lot.
:::

## Try it yourself

1. Which fits better: a public weather API, or a payment service called 30,000 times a second by internal services?
2. Why does gRPC need a schema while a JSON REST API often does not?
3. Cancelling an order is not exactly CRUD. How can REST and RPC each express it?

<details class="solution"><summary>Answers</summary>

1. Weather: **REST** (public, cacheable, universal). Payment service: **gRPC** (fast, typed, internal).
2. gRPC sends only values in a compact binary form, so both sides need the schema (field numbers and types) to interpret the bytes; JSON carries field names in the text itself.
3. REST: `POST /orders/42/cancel` (an action sub-resource) or `PATCH` the status. RPC: `CancelOrder(order_id=42)`.

</details>

:::{admonition} Next
:class: important
The last trade-off: do you wait for the answer? [Synchronous vs asynchronous
communication](70-sync-vs-async-communication.md).
:::
