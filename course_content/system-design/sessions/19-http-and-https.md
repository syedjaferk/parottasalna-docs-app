# Chapter 19 · HTTP and HTTPS

## The big idea

**HTTP** is the language browsers and apps use to ask servers for things. **HTTPS** is HTTP inside an
encrypted, verified tunnel (TLS), so nobody on the path can read or change it.

**Everyday example:** ordering at a restaurant. You say what you want (**request**), the waiter comes
back with food or an apology (**response**). HTTPS is doing it in a private room with a waiter whose ID
you checked, instead of shouting across a public market.

## Anatomy of a request and a response

```text
GET /api/products/42?lang=en HTTP/1.1          <- method, path, version
Host: shop.example.com                          <- headers
Accept: application/json
Authorization: Bearer eyJhbGciOi...
                                                <- blank line, then optional body

HTTP/1.1 200 OK                                 <- status line
Content-Type: application/json
Cache-Control: max-age=60
ETag: "v17"

{"id": 42, "name": "Masala tea", "price": 25}   <- body
```

```python
raw = (
    "POST /api/orders HTTP/1.1\r\n"
    "Host: shop.example.com\r\n"
    "Content-Type: application/json\r\n"
    "Content-Length: 27\r\n"
    "\r\n"
    '{"item": 42, "quantity": 3}'
)

head, body = raw.split("\r\n\r\n", 1)
request_line, *header_lines = head.split("\r\n")
method, path, version = request_line.split(" ")
headers = dict(line.split(": ", 1) for line in header_lines)

print("method :", method)
print("path   :", path)
print("host   :", headers["Host"])
print("body   :", body)
```

**Output:**

```text
method : POST
path   : /api/orders
host   : shop.example.com
body   : {"item": 42, "quantity": 3}
```

HTTP is plain text with a clear structure. Everything else (REST, GraphQL, gRPC over HTTP/2) is built
on top.

## Methods and what they promise

| Method | Meaning | Safe? | Idempotent? | Typical use |
|---|---|---|---|---|
| **GET** | Read | Yes | Yes | Fetch a resource |
| **POST** | Create / do something | No | **No** | Create an order |
| **PUT** | Replace | No | Yes | Replace a profile |
| **PATCH** | Partial update | No | Not guaranteed | Change one field |
| **DELETE** | Remove | No | Yes | Delete a resource |

*Safe* = does not change data (so caches and crawlers may call it freely). *Idempotent* = calling it
twice has the same effect as once (so a client may safely retry).

## Status codes by family

| Family | Meaning | Remember |
|---|---|---|
| **2xx** success | `200` OK, `201` Created, `204` No Content | |
| **3xx** redirect | `301` permanent, `302` temporary, `304` Not Modified (cache still valid) | |
| **4xx** your fault | `400` bad input, `401` not logged in, `403` not allowed, `404` not found, `409` conflict, `429` too many requests | Do not retry unchanged |
| **5xx** our fault | `500` bug, `502` bad gateway, `503` overloaded, `504` upstream timeout | Retry with backoff |

## Statelessness, cookies and caching

HTTP is **stateless**: each request stands alone, and the server remembers nothing. To "stay logged
in" the client sends something every time: a **cookie** or an **Authorization** token.

Caching headers:

- `Cache-Control: max-age=3600` : reuse this for an hour without asking.
- `ETag: "v17"` + `If-None-Match: "v17"` : "has it changed?" A `304` reply with no body means
  "keep using your copy". Saves bandwidth.
- `Cache-Control: no-store` : never cache (sensitive data).

## HTTP versions

| Version | Key idea | Why it matters |
|---|---|---|
| **HTTP/1.1** | One request at a time per connection; keep-alive reuses connections | Browsers open ~6 connections to compensate |
| **HTTP/2** | **Multiplexing**: many requests share one connection, header compression | Faster pages; but one lost TCP packet stalls all streams |
| **HTTP/3** | Runs on **QUIC (UDP)**: streams are independent, faster connection setup | Better on mobile and lossy networks |

## HTTPS: what TLS adds

HTTPS gives you three guarantees:

1. **Confidentiality:** nobody on the path can read the data (encryption).
2. **Integrity:** nobody can alter it undetected (message authentication).
3. **Authentication:** you are really talking to `shop.example.com` (certificate).

### The handshake, simplified (TLS 1.3)

```{raw} html
:file: ../diagrams/tls-handshake.html
```

1. **ClientHello:** the browser says which TLS versions and ciphers it supports and sends its half of
   a key exchange.
2. **ServerHello + certificate:** the server picks a cipher, sends its half of the key exchange and its
   **certificate**: a document saying "this public key belongs to shop.example.com", **signed by a
   certificate authority (CA)** the browser already trusts.
3. The browser **verifies the signature chain, the domain name and the expiry**.
4. Both sides compute the same **session key** from the two halves (Diffie-Hellman) **without ever
   sending the key**.
5. From now on all HTTP traffic is encrypted with that fast symmetric key.

Cost: TLS 1.3 adds **one extra round trip** (TLS 1.2 added two). Connection reuse, session resumption
and CDNs terminating TLS near the user keep this cheap.

**Public-key cryptography** (certificate, key exchange) is slow and is used only to agree on a key.
**Symmetric encryption** (AES) is fast and encrypts the actual data.

### Where to terminate TLS

Usually at the **load balancer or CDN edge**. Your internal services then talk plain HTTP inside a
private network (or re-encrypt with mTLS if the network is not trusted). This centralises certificate
renewal and saves CPU on app servers.

## HTTPS is not magic

- It protects data **in transit**, not on the server or in the database.
- A valid certificate proves **the domain**, not that the site is honest. Phishing sites have valid certs.
- **HSTS** (`Strict-Transport-Security`) tells browsers to refuse plain HTTP for your domain.

## Common mistakes

:::{warning}
- Using `GET` for actions that change data (crawlers and prefetchers will trigger them).
- Returning `200 OK` with an error message in the body. Use real status codes.
- Retrying `POST` blindly: it may create duplicates (see the idempotency chapter).
- Letting a certificate expire. Automate renewal (Let's Encrypt, ACM).
:::

## Try it yourself

1. Which status code for: successful creation, missing login, forbidden action, rate limited, upstream timeout?
2. Why can a client safely retry `PUT` but not `POST`?
3. Why does TLS use public-key crypto for the handshake but symmetric crypto for the data?

<details class="solution"><summary>Answers</summary>

1. `201`, `401`, `403`, `429`, `504`.
2. `PUT` replaces the resource with the same content, so doing it twice leaves the same result. `POST` usually creates something new each time.
3. Public-key operations are far too slow for bulk data but solve the problem of agreeing on a secret over an open network. Once both sides share a key, fast AES encrypts the traffic.

</details>

:::{admonition} Next
:class: important
Now you can spread requests over many servers: [load balancing](20-load-balancing.md).
:::
