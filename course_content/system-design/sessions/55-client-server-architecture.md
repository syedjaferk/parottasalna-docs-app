# Chapter 55 · Client-server architecture

## The big idea

In **client-server architecture** one side, the **client**, **asks** for something and the other side, the
**server**, **provides** it. Clients start the conversation; servers wait, serve many clients at once, and
hold the shared data and rules.

**Everyday example:** a **restaurant**. Customers (clients) come with requests: "one masala dosa". The
kitchen (server) prepares it and hands it over. One kitchen serves many customers. Customers do not cook, and
the kitchen does not walk to anyone's house uninvited.

```{raw} html
:file: ../diagrams/client-server.html
```

## The roles

| | Client | Server |
|---|---|---|
| Starts the conversation | **Yes** | No: it listens |
| Runs on | User devices (browser, phone, other services) | Machines you control |
| Number | Millions | Few or many, but far fewer than clients |
| Trust | **Untrusted**: anyone can send anything | Trusted: enforces rules and security |
| Holds | Presentation, local state | Shared data, business logic |

A server for one request can be a client of another (an API server calling a database or a payment service).

## How a request travels

```text
Browser --(1) DNS--> IP --(2) TCP+TLS--> Web server --(3) HTTP request--> App --(4) query--> Database
                                          <--(8) response--- <--(7)--------- <--(6) result---
```

1. DNS finds the address, a TCP connection and TLS session are set up, and the HTTP request is sent.
2. The server runs logic, perhaps queries a database or other services, and returns a response.

## Tiered architectures

| Tiers | Layout | Where it fits |
|---|---|---|
| **1-tier** | Everything on one machine (a desktop app with a local file) | Single-user tools |
| **2-tier** | Client talks **directly to a database** | Small internal apps; unsafe on the internet (clients hold DB credentials) |
| **3-tier** | **Presentation** (client) -> **application/logic** (server) -> **data** (database) | The standard web design |
| **N-tier** | Adds caches, queues, API gateways, search services | Larger systems |

Three tiers separate concerns: you can scale the app tier without touching the database, change the UI without
changing the rules, and keep database credentials **off** the client.

## Thin vs thick clients

- **Thin client:** the server does the work and sends mostly ready-to-show output (server-rendered pages).
  Easy to update; every action needs a round trip.
- **Thick (rich) client:** the client does more (single-page apps, mobile apps, games), calling APIs for data.
  Better responsiveness and offline use; logic is duplicated, and old app versions linger.

Security rule for both: **never trust the client**. Validate and authorise everything on the server, because
anyone can craft their own requests.

## Making the server side scale

A single server is a **bottleneck and a single point of failure**. The standard path:

1. Run **many identical, stateless** application servers.
2. Put a **load balancer** in front.
3. Keep state in **shared stores** (database, cache).
4. Scale the data tier with **replicas and shards**.

```python
# A client-server exchange, using real HTTP parsing on both sides
def server(raw_request):
    request_line = raw_request.split("\r\n")[0]
    method, path, _ = request_line.split(" ")
    if method == "GET" and path == "/hello":
        body = '{"message": "hello from the server"}'
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\n\r\n{body}"
    return "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"

def client(path):
    request = f"GET {path} HTTP/1.1\r\nHost: example.com\r\n\r\n"        # the client speaks first
    response = server(request)                                             # the server only reacts
    status_line = response.split("\r\n")[0]
    body = response.split("\r\n\r\n", 1)[1]
    return status_line, body

print(client("/hello"))
print(client("/missing"))
```

**Output:**

```text
('HTTP/1.1 200 OK', '{"message": "hello from the server"}')
('HTTP/1.1 404 Not Found', '')
```

## Strengths and weaknesses

| Strengths | Weaknesses |
|---|---|
| **Centralised data and rules**: easy to secure, back up and update | The server is a **bottleneck and SPOF** unless scaled and duplicated |
| Clients can be simple and many | **Network dependent**: no server, no service |
| One place to enforce security and consistency | Cost and effort grow with the number of clients |
| Well understood, huge tooling | Latency for every interaction |

## Client-server vs peer-to-peer

| | Client-server | Peer-to-peer |
|---|---|---|
| Roles | Fixed (asks / serves) | Every node is both |
| Control | Centralised | Decentralised |
| Scaling | You buy more servers | More users bring more capacity |
| Failure | Server is a SPOF | No single point |
| Example | Web, email, banking | BitTorrent, blockchains |

(See the peer-to-peer chapter.)

## Common mistakes

:::{warning}
- Trusting the client (hidden fields, client-side price calculation, client-side permission checks).
- Letting clients talk **directly** to the database.
- A single application server with state in memory.
- Chatty clients making many sequential requests instead of batching.
:::

## Try it yourself

1. In an online shop, which checks must run on the server even if the browser already did them?
2. Why is a two-tier design with the client connecting directly to the database risky on the public internet?
3. Which tier would you scale first for a read-heavy site, and how?

<details class="solution"><summary>Answers</summary>

1. **All of them**: price, stock, authentication, authorisation and input validation. Client checks are only for user convenience.
2. Database credentials and network access would live on every client device, and anyone could run arbitrary queries.
3. Often the **data tier first**: add caching and read replicas; app servers are stateless and easy to add behind a load balancer.

</details>

:::{admonition} Next
:class: important
When a single server-side application grows too large, teams split it: [microservices](56-microservices.md).
:::
