# Chapter 25 · WebSockets

## The big idea

Normal HTTP is a **question and answer**: the client asks, the server replies, the conversation ends.
**WebSockets** keep one connection **open both ways**, so the server can **push** data the moment
something happens and the client can send at any time.

**Everyday example:** HTTP is **sending letters**: every question needs a new envelope, and the other
side cannot write unless you wrote first. A WebSocket is a **phone call**: once connected, either side
can speak whenever they like.

```{raw} html
:file: ../diagrams/websockets.html
```

## Why plain HTTP struggles with live data

How do you show a new chat message to the other person instantly?

- **Polling:** the client asks "anything new?" every 2 seconds. Wasteful: 99% of answers are "no", and
  messages arrive up to 2 seconds late. With 1 million users that is **500,000 requests per second** of
  mostly nothing.
- **Long polling:** the client asks and the server **holds the request open** until there is news
  (see the long polling vs WebSockets chapter).
- **Server-Sent Events (SSE):** one long-lived HTTP response the server keeps writing to. One-way only.
- **WebSocket:** a two-way channel.

## How a WebSocket starts: an HTTP upgrade

A WebSocket begins as an ordinary HTTP request that asks to **upgrade** the connection:

```text
GET /chat HTTP/1.1
Host: chat.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

Status `101` means "from now on this TCP connection speaks WebSocket". The server proves it understood by
hashing the client's key with a fixed GUID:

```python
import base64, hashlib

key = "dGhlIHNhbXBsZSBub25jZQ=="                      # from the client's Sec-WebSocket-Key
GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"          # fixed by the WebSocket standard (RFC 6455)

accept = base64.b64encode(hashlib.sha1((key + GUID).encode()).digest()).decode()
print("Sec-WebSocket-Accept:", accept)
```

**Output:**

```text
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

After the `101`, both sides exchange small **frames** (text or binary) with only 2 to 14 bytes of
overhead, instead of hundreds of bytes of HTTP headers per message.

## A chat room, simulated

The server keeps a list of open connections and **broadcasts** each message to the others:

```python
import asyncio

class Room:
    def __init__(self):
        self.members = {}                     # name -> that member's inbox (their open connection)

    async def join(self, name):
        self.members[name] = asyncio.Queue()

    async def send(self, sender, text):
        for name, inbox in self.members.items():
            if name != sender:
                await inbox.put(f"{sender}: {text}")      # push to every other open connection

async def main():
    room = Room()
    for n in ("asha", "ravi", "meena"):
        await room.join(n)
    await room.send("asha", "hello everyone")
    await room.send("ravi", "hi asha")
    for name in ("asha", "ravi", "meena"):
        inbox = room.members[name]
        got = []
        while not inbox.empty():
            got.append(await inbox.get())
        print(f"{name:<6} received {got}")

asyncio.run(main())
```

**Output:**

```text
asha   received ['ravi: hi asha']
ravi   received ['asha: hello everyone']
meena  received ['asha: hello everyone', 'ravi: hi asha']
```

No client asked for anything. The server **pushed**. That is the entire idea.

## Designing for WebSockets at scale

A WebSocket connection is **stateful**: it lives on **one specific server**. That changes the design.

1. **Memory per connection:** each open connection costs memory (about 10 to 50 KB). One server can hold
   roughly **50,000 to 1 million** connections with tuning. 10 million concurrent users need about
   **10 to 200 servers** just for connections.
2. **Load balancing:** connections are long, so "round robin per request" does not balance them. Use
   **least connections** and expect uneven spread after a deploy.
3. **Cross-server messages:** Asha is connected to server 1, Ravi to server 4. A message from Asha must
   reach server 4. Use **pub/sub** (Redis, Kafka) between servers: server 1 publishes to the room channel,
   every server with a member of that room delivers it.
4. **Reconnection:** connections drop (mobile networks, deploys). Clients **reconnect with backoff and
   jitter** and say "I last saw message 981": the server **replays** what was missed.
5. **Heartbeats:** send ping/pong every 20 to 30 seconds to detect dead connections and keep NAT and proxies
   from closing idle ones.
6. **Authentication:** authenticate during the HTTP upgrade (token in the first message or a cookie);
   re-check periodically.
7. **Fallback:** some corporate proxies block WebSockets, so libraries (Socket.IO) fall back to long polling.

```{raw} html
:file: ../diagrams/websocket-scaling.html
```

## When to use them

| Use WebSockets for | Prefer something else for |
|---|---|
| Chat, live comments | One-off request/response (use REST) |
| Multiplayer games, collaborative editing | Rare updates: use polling or SSE |
| Live dashboards, trading prices | Server-to-server events: webhooks or queues |
| Live location (ride tracking) | Tiny scale where polling is simpler |

## Common mistakes

:::{warning}
- Using WebSockets for data that changes once a minute (polling is simpler and cacheable).
- Storing the only copy of important state in a connection's server memory.
- No reconnect and replay logic: a flaky network loses messages.
- Forgetting that a deploy drops every connection on that server at once (a **reconnect storm**).
:::

## Try it yourself

1. A chat app has 2 million concurrent users and a server holds 100,000 connections. How many servers for connections alone (with 30% headroom)?
2. Asha is on server 1 and Ravi on server 4. How does Ravi get Asha's message?
3. Why does polling every 2 seconds for 1 million users cost so much?

<details class="solution"><summary>Answers</summary>

1. 2,000,000 / 100,000 = 20 servers; with 30% headroom, **26 servers**.
2. Server 1 publishes the message to a **pub/sub channel**; server 4, which subscribes for Ravi's room or user, receives it and pushes it down Ravi's socket.
3. 1,000,000 / 2 = **500,000 requests per second**, almost all returning "nothing new", each carrying full HTTP headers.

</details>

:::{admonition} Next
:class: important
WebSockets push to a *client*. When one *server* must tell another server something happened, we use
[webhooks](26-webhooks.md).
:::
