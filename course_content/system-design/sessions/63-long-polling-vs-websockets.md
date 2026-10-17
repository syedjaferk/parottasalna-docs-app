# Chapter 63 · Long polling vs WebSockets

## The big idea

Both let a server tell a client about **new data without the client constantly asking**. They differ in
**how**:

- **Long polling:** the client asks, and the server **holds the request open** until it has news (or a timeout),
  then answers; the client **immediately asks again**.
- **WebSockets:** one **persistent, two-way** connection; either side can send at any time.

**Everyday example:** waiting for a parcel. **Long polling** is phoning the courier, being told "stay on the
line, I'll say as soon as it arrives" and, once they tell you, ringing again to wait for the next parcel.
**WebSockets** is the courier giving you a **walkie-talkie** that stays switched on.

```{raw} html
:file: ../diagrams/long-polling-vs-websockets.html
```

## The family of techniques

| Technique | How | Direction | Cost |
|---|---|---|---|
| **Short polling** | Ask every N seconds | Client to server | Many wasted requests; delay up to N |
| **Long polling** | Ask; server waits until data or timeout; ask again | Server push (simulated) | One held request per client; re-request overhead |
| **Server-Sent Events (SSE)** | One long HTTP response the server keeps writing to | Server to client only | Light; auto-reconnect built in |
| **WebSocket** | Persistent full-duplex connection | **Both ways** | Stateful connection per client |

## Long polling step by step

```text
t=0    client: GET /messages?after=41      (server has nothing yet: it HOLDS the request)
t=12   a new message (id 42) arrives       (server answers the held request immediately)
t=12   client: receives 42, immediately sends GET /messages?after=42     (next held request)
t=42   still nothing after 30 s: server answers "no news" (timeout); client asks again
```

## Counting the work

```python
def short_polling(users, interval_s, events_per_user_per_hour):
    requests = users * 3600 / interval_s
    useful = users * events_per_user_per_hour
    return requests, useful

def long_polling(users, events_per_user_per_hour, timeout_s=30):
    # one request completes per event, plus timeouts when idle
    event_responses = users * events_per_user_per_hour
    timeout_responses = users * max(0, 3600 / timeout_s - events_per_user_per_hour)
    return event_responses + timeout_responses, event_responses

def websocket(users, events_per_user_per_hour, ping_s=30):
    return users * (events_per_user_per_hour + 3600 / ping_s), users * events_per_user_per_hour    # messages + pings

users, events = 100_000, 6        # 100k online users, each receives 6 updates an hour
for name, (n, useful) in {
    "short polling (2 s)": short_polling(users, 2, events),
    "long polling (30 s)": long_polling(users, events),
    "websocket (30 s ping)": websocket(users, events),
}.items():
    print(f"{name:<22} {n / 3600:>9,.0f} messages/s   useful: {useful / n:>6.1%}")
```

**Output:**

```text
short polling (2 s)       50,000 messages/s   useful:   0.3%
long polling (30 s)        3,333 messages/s   useful:   5.0%
websocket (30 s ping)      3,500 messages/s   useful:   4.8%
```

Short polling sends **50,000 requests a second**, and only 0.3% of them carry news. Long polling and WebSockets send
about **3,500 messages a second**, 15 times fewer. WebSockets also send them as tiny frames instead of full HTTP
requests, and have **no re-request gap** in which events can be missed.

## Comparison

| | Long polling | WebSocket |
|---|---|---|
| Protocol | Plain HTTP | HTTP upgrade, then its own framing |
| Direction | Server push; client uses normal requests to send | **True two-way** |
| Latency | One round trip to re-poll after each message; messages can be missed in the gap (you need ids) | **Lowest**: push immediately |
| Overhead | Full HTTP headers on every poll | **2-14 bytes** per frame |
| Works through proxies, firewalls, old browsers | **Almost everywhere** | Some proxies block or time out idle sockets |
| Server resources | A held request ties up a connection (or thread, in thread-per-request servers) | A connection **plus** per-connection state |
| Load balancing | Stateless: any server can answer the next poll | **Sticky**: connection lives on one server |
| Scaling | Easier, uses the normal HTTP stack and caches | Needs connection-aware infrastructure and pub/sub between servers |
| Complexity | Low | Medium to high (reconnect, heartbeats, auth, backpressure) |
| Best for | Occasional updates, fallback, simple stacks | **Frequent, bidirectional** messages: chat, games, collaboration, live trading |

## Practical considerations

### Long polling

- **Never lose events in the gap** between one response and the next request: send an **event id**
  (`after=41`) so the server can replay what was missed.
- Choose timeouts below proxies' idle limits (typically 30 to 60 seconds) and handle the thundering herd when
  all clients re-poll at once.
- Servers must be able to **hold many idle requests cheaply** (async servers, not one thread per request).

### WebSockets

- Handle **reconnection with backoff and jitter**; replay from a last-seen id.
- **Heartbeats (ping/pong)** to detect dead connections.
- Authenticate during the upgrade; limit message size and rate.
- A **pub/sub backbone** (Redis, Kafka) to deliver a message to the server holding the recipient's socket.
- Plan for **deploy storms**: restarting a server drops all its connections, which all reconnect at once.

### SSE as a middle path

For **one-way** streams (news tickers, notifications, progress bars, live scores) SSE is simpler than
WebSockets: plain HTTP, automatic reconnection and `Last-Event-ID` replay built in, works with HTTP/2.

## Choosing

| Need | Pick |
|---|---|
| Chat, multiplayer game, collaborative editor | **WebSocket** |
| Live notifications, tickers, dashboards (one-way) | **SSE** (or WebSocket) |
| Infrequent updates, simple infrastructure, restrictive networks | **Long polling** |
| Updates every few minutes | **Short polling** (simplest, cacheable) |
| Fallback for the above | Libraries like Socket.IO try WebSocket and fall back to long polling |

## Common mistakes

:::{warning}
- Short-polling every second at scale: a huge load with almost no useful responses.
- Long polling without event ids: messages arriving between polls are lost.
- WebSockets for data that changes once a minute.
- Forgetting that WebSocket servers are **stateful**: balancing, deploys and failures need extra design.
:::

## Try it yourself

1. A stock ticker pushes prices to 50,000 browsers several times a second. Which technique?
2. A mobile app checks for a new order status every minute on average-quality networks. Which is simplest?
3. Why does long polling still need an event id in the request?

<details class="solution"><summary>Answers</summary>

1. **WebSockets** (or SSE since it is one-way): frequent updates and low latency.
2. **Short or long polling**: updates are infrequent, so a persistent connection is not worth its complexity.
3. Between a response and the next request there is a gap in which new events can occur. The id lets the server send everything after the last event the client saw.

</details>

:::{admonition} Next
:class: important
Processing data in bulk or as it arrives: [batch vs stream processing](64-batch-vs-stream-processing.md).
:::
