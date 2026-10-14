# Session 14 · Observer pattern

## The big idea

When one object changes, **other objects need to know**, but you don't want the first object to
know who they are. The **Observer** pattern lets objects *subscribe* to a **subject**. When
something happens, the subject notifies every subscriber. Add or remove subscribers without touching
the subject.

**Everyday example:** a YouTube channel. You subscribe once. When a new video is uploaded, everyone
subscribed gets a notification. The channel doesn't know your name or phone, and it doesn't call
each person by hand.

:::{admonition} In plain words
:class: tip
When something happens, **tell everyone who's interested**, without knowing who they are. They subscribe once; you just announce the event.

**Reach for it when:**

- one event should trigger several reactions (email, stock, analytics)
- the code that causes the event shouldn't depend on every reaction
- reactions are added and removed over time
:::

## Without Observer

`0.no_observer.py`: the order code knows about everyone who cares.

```python
class OrderService:
    def place_order(self, item):
        print(f"Order placed: {item}")
        send_email(item)          # tight coupling
        update_inventory(item)
        notify_warehouse(item)
        log_analytics(item)
```

Every new reaction means editing `place_order`. It can't be tested without all four helpers.

## With Observer

`1.observer.py`:

```python
class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list] = {}

    def subscribe(self, event: str, handler):
        self._subscribers.setdefault(event, []).append(handler)

    def unsubscribe(self, event: str, handler):
        self._subscribers[event].remove(handler)

    def publish(self, event: str, data):
        for handler in self._subscribers.get(event, []):
            handler(data)

bus = EventBus()

def email(order):      print(f"📧 email for {order['item']}")
def inventory(order):  print(f"📦 stock -1 for {order['item']}")
def analytics(order):  print(f"📊 logged {order['item']}")

bus.subscribe("order_placed", email)
bus.subscribe("order_placed", inventory)
bus.subscribe("order_placed", analytics)

class OrderService:
    def __init__(self, bus): self.bus = bus
    def place_order(self, item):
        print(f"Order placed: {item}")
        self.bus.publish("order_placed", {"item": item})

OrderService(bus).place_order("laptop")
```

```text
Order placed: laptop
📧 email for laptop
📦 stock -1 for laptop
📊 logged laptop
```

`OrderService` doesn't know who is listening. A new reaction is one `subscribe` call.

```{raw} html
:file: ../diagrams/s14-observer.html
```

## Observer + AI: streaming tokens

LLM answers arrive token by token. Many parts want them: the screen, a log file, a cost counter
(`2.token_stream.py`):

```python
class TokenStream:
    def __init__(self):
        self.listeners = []

    def subscribe(self, fn):
        self.listeners.append(fn)

    def emit(self, token: str):
        for fn in self.listeners:
            fn(token)

stream = TokenStream()
buffer, count = [], [0]

stream.subscribe(lambda t: print(t, end="", flush=True))      # show on screen
stream.subscribe(lambda t: buffer.append(t))                  # keep full text
stream.subscribe(lambda t: count.__setitem__(0, count[0] + 1))  # count tokens

for token in ["Design ", "patterns ", "are ", "fun."]:
    stream.emit(token)

print(f"\n{count[0]} tokens, text={''.join(buffer)!r}")
```

LangChain's callback handlers work exactly like this: your handler gets `on_llm_new_token` calls.

## Common mistakes

- **Forgetting to unsubscribe.** Old handlers keep running and keep objects alive: a memory leak.
- **A handler that crashes** and stops the others. Wrap each call in `try/except` and log.
- **Slow handlers.** One slow subscriber delays everything. Run heavy work in a queue or thread.
- **Notification loops.** A handler that publishes the event it listens to loops forever.
- **Relying on order.** Don't assume subscribers run in the order they subscribed.

## Hands-on exercises

**Exercise 1 · Safe publish.** Make `publish` continue even if one handler raises.

<details class="solution"><summary>Solution</summary>

```python
def publish(self, event, data):
    for handler in self._subscribers.get(event, []):
        try:
            handler(data)
        except Exception as e:
            print(f"handler {handler.__name__} failed: {e}")
```

</details>

**Exercise 2 · Stock alert.** A `Stock` has a `price`. When it changes, notify watchers; one prints a
message when the price drops below 100.

<details class="solution"><summary>Solution</summary>

```python
class Stock:
    def __init__(self, name, price):
        self.name, self._price, self.watchers = name, price, []

    @property
    def price(self): return self._price

    @price.setter
    def price(self, value):
        old, self._price = self._price, value
        for w in self.watchers:
            w(self.name, old, value)

def alert(name, old, new):
    if new < 100:
        print(f"⚠️ {name} fell to {new} (was {old})")

s = Stock("ABC", 120)
s.watchers.append(alert)
s.price = 95        # ⚠️ ABC fell to 95 (was 120)
```

</details>

**Exercise 3 · One-time subscriber.** Add `once(event, handler)` that unsubscribes after the first call.

<details class="solution"><summary>Solution</summary>

```python
def once(self, event, handler):
    def wrapper(data):
        self.unsubscribe(event, wrapper)
        handler(data)
    self.subscribe(event, wrapper)
```

</details>

## Full source

<details class="source">
<summary>1.observer.py</summary>

```{literalinclude} ../code/14-observer/1.observer.py
:language: python
```

</details>

<details class="source">
<summary>2.token_stream.py</summary>

```{literalinclude} ../code/14-observer/2.token_stream.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_observer.py <../code/14-observer/0.no_observer.py>` ·
{download}`1.observer.py <../code/14-observer/1.observer.py>` ·
{download}`2.token_stream.py <../code/14-observer/2.token_stream.py>`
