# Chapter 65 · Stateful vs stateless architecture

## The big idea

- A **stateless** server **remembers nothing** about a client between requests. Every request carries everything
  needed to handle it.
- A **stateful** server **remembers** earlier interactions (a login session, a half-filled cart, an open game).

**Everyday example:** two kinds of shop assistants. The **stateless** assistant treats every customer as new:
"here is your order slip with everything on it, I will fetch the items". Any assistant at any counter can serve
you. The **stateful** assistant remembers you: "you were looking at the blue shirt earlier". It feels
personal, but if that assistant goes home sick, **the memory leaves with them**, and you must always return to
**their** counter.

```{raw} html
:file: ../diagrams/stateful-vs-stateless.html
```

## Side by side

| | **Stateless** | **Stateful** |
|---|---|---|
| Server remembers the client? | **No** | Yes |
| Which server can handle a request? | **Any** | Only the one holding the state |
| Scaling out | **Easy**: add servers | Hard: state must move or requests must be pinned |
| Load balancing | Simple (round robin) | **Sticky sessions** needed |
| Server failure | Lose nothing (retry elsewhere) | **Lose the state** of its users |
| Deployments / restarts | Easy, rolling | Must drain or migrate state |
| Request size | Larger (carries context) | Smaller (server knows context) |
| Latency | Slightly higher if state is fetched from a store | Fast local access |
| Examples | REST APIs, serverless functions, HTTP itself | WebSocket servers, game servers, TCP connections, databases |

## Where the state goes in a stateless design

The state does not disappear; it **moves out of the web server** into a **shared place**:

| Where | Used for | Notes |
|---|---|---|
| **Database** | Durable data (orders, profiles) | The source of truth |
| **Shared cache (Redis)** | Sessions, carts, temporary data | Fast, small, expiry |
| **The client** | A **signed token (JWT)**, cookies, local storage | No server memory; keep it small; sign it so it cannot be forged |
| **Object storage** | Files, uploads | Cheap and durable |

```python
# STATEFUL: the cart lives in this server's memory
class StatefulServer:
    def __init__(self, name):
        self.name, self.carts = name, {}
    def add(self, user, item):
        self.carts.setdefault(user, []).append(item)
        return f"{self.name}: {user}'s cart = {self.carts[user]}"

a, b = StatefulServer("serverA"), StatefulServer("serverB")
print(a.add("asha", "tea"))
print(b.add("asha", "biscuits"))          # the load balancer sent her next request to server B: her tea is gone
print()

# STATELESS: servers keep nothing; the cart is in a shared store (Redis in real life)
shared_store = {}
class StatelessServer:
    def __init__(self, name):
        self.name = name
    def add(self, user, item):
        shared_store.setdefault(user, []).append(item)
        return f"{self.name}: {user}'s cart = {shared_store[user]}"

c, d = StatelessServer("serverC"), StatelessServer("serverD")
print(c.add("ravi", "tea"))
print(d.add("ravi", "biscuits"))          # any server works: the cart follows the user
```

**Output:**

```text
serverA: asha's cart = ['tea']
serverB: asha's cart = ['biscuits']

serverC: ravi's cart = ['tea']
serverD: ravi's cart = ['tea', 'biscuits']
```

## Sessions: the classic example

| Approach | How | Trade-off |
|---|---|---|
| **Sticky sessions** | The load balancer pins a user to one server that holds the session | Easy; uneven load, state lost on failure, hard to scale down |
| **Session store** | Session id in a cookie; data in Redis | Stateless servers; one extra lookup per request; Redis must be highly available |
| **Token in the client (JWT)** | Signed token carries the identity and claims | No lookup; **cannot be revoked easily** before expiry; size limits |

## When state is unavoidable

Some systems are **inherently stateful**: databases, caches, WebSocket servers, game rooms, video calls.
Handle it by:

- **Isolating** state into a few dedicated components (so the rest stay stateless).
- **Replicating** state (primary-replica) so a failure does not lose it.
- **Sharding** with a known owner per key (consistent hashing), and **sticky routing** to that owner.
- **Making state recoverable**: persist it, so a replacement can reload it (a game room's last snapshot).
- **Draining** connections gracefully on deploys.

## Stateless protocols and "stateful" experiences

HTTP is **stateless** by design, yet websites remember you: cookies, tokens and server-side stores create the
**illusion of state**. TCP, by contrast, is **stateful** (sequence numbers, windows), which is why long-lived
connections tie a client to one server.

## Design rule

> **Keep your application tier stateless, and concentrate state in a small number of purpose-built stores that
> are replicated and partitioned.**

This is why horizontal scaling, rolling deployments, autoscaling, serverless and self-healing all work so
easily on stateless services.

## Common mistakes

:::{warning}
- Storing sessions or carts in server memory behind a load balancer.
- Using sticky sessions as a permanent fix instead of moving the state out.
- Putting too much into a JWT (size, stale data, privacy) or making it impossible to revoke.
- A shared session store with no replication (it becomes the SPOF).
:::

## Try it yourself

1. Why does a stateless web tier make deployments and autoscaling easier?
2. Compare storing a session in Redis versus in a JWT, in one sentence each.
3. A multiplayer game server holds room state in memory. What would you add so a crash does not lose games?

<details class="solution"><summary>Answers</summary>

1. Any server can serve any request, so you can add, remove or replace servers freely with no state to migrate.
2. Redis: easy to revoke and update, but needs a lookup and a highly available store. JWT: no lookup, but hard to revoke before it expires.
3. Periodically **persist room snapshots** (and move events) to a durable store or replicate to a standby so a replacement server can **reload** the state.

</details>

:::{admonition} Next
:class: important
Back to consistency with real-world examples: [strong vs eventual consistency](66-strong-vs-eventual-consistency.md).
:::
