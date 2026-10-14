# Session 16 · State pattern

## The big idea

Some objects behave **differently depending on what state they are in**: an order can be *placed*,
*paid*, *shipped* or *cancelled*, and what you may do changes with each. Tracking this with flags
and `if status == ...` everywhere gets messy. The **State** pattern makes **each state its own
class**. The object holds a current state and delegates to it. Changing state means swapping the object.

**Everyday example:** a traffic light. The same light behaves differently in red, green and yellow.
It doesn't ask "am I red?" before every action. Each colour knows what comes next.

:::{admonition} In plain words
:class: tip
An object behaves differently depending on what **state** it's in. Give each state its own class that knows what's allowed and what comes next.

**Reach for it when:**

- many methods start with the same `if status == …` ladder
- there are clear rules for moving from one state to another
- invalid moves (shipping before paying) must be impossible
:::

## Without State

`0.no_state.py`: `if/elif` on a status string in every method.

```python
class Order:
    def __init__(self): self.status = "placed"

    def pay(self):
        if self.status == "placed":
            self.status = "paid"
        elif self.status == "paid":
            print("already paid")
        elif self.status == "shipped":
            print("already shipped")
        elif self.status == "cancelled":
            print("order is cancelled")

    def cancel(self):
        if self.status == "placed": ...
        elif self.status == "paid": ...
        # same ladder again for ship(), refund(), ...
```

Every method repeats the ladder, and adding a state means editing all of them.

## With State

`1.state.py`:

```python
from abc import ABC, abstractmethod

class OrderState(ABC):
    @abstractmethod
    def pay(self, order): ...
    @abstractmethod
    def ship(self, order): ...
    @abstractmethod
    def cancel(self, order): ...

class Placed(OrderState):
    def pay(self, order):
        print("💰 payment received")
        order.state = Paid()
    def ship(self, order):  print("❌ pay first")
    def cancel(self, order):
        print("🚫 order cancelled")
        order.state = Cancelled()

class Paid(OrderState):
    def pay(self, order):   print("already paid")
    def ship(self, order):
        print("🚚 shipped")
        order.state = Shipped()
    def cancel(self, order):
        print("🚫 cancelled, refund started")
        order.state = Cancelled()

class Shipped(OrderState):
    def pay(self, order):    print("already paid")
    def ship(self, order):   print("already shipped")
    def cancel(self, order): print("❌ too late to cancel")

class Cancelled(OrderState):
    def pay(self, order):    print("❌ order cancelled")
    def ship(self, order):   print("❌ order cancelled")
    def cancel(self, order): print("already cancelled")

class Order:
    def __init__(self):
        self.state: OrderState = Placed()
    def pay(self):    self.state.pay(self)
    def ship(self):   self.state.ship(self)
    def cancel(self): self.state.cancel(self)

o = Order()
o.ship()       # ❌ pay first
o.pay()        # 💰 payment received
o.ship()       # 🚚 shipped
o.cancel()     # ❌ too late to cancel
```

Rules of each state sit together in one class. New state = new class.

```{raw} html
:file: ../diagrams/s16-state.html
```

## A lighter way: a transition table

For simple machines, a dictionary is enough (`2.table.py`):

```python
transitions = {
    ("placed", "pay"): "paid",
    ("placed", "cancel"): "cancelled",
    ("paid", "ship"): "shipped",
    ("paid", "cancel"): "cancelled",
}

def move(state, action):
    try:
        return transitions[(state, action)]
    except KeyError:
        raise ValueError(f"cannot {action} when {state}")

s = "placed"
s = move(s, "pay")      # paid
s = move(s, "ship")     # shipped
move(s, "cancel")       # ValueError: cannot cancel when shipped
```

Use the table for few states with simple rules. Use state classes when each state has real behaviour.

## State + AI: agent lifecycle

An agent is rarely "just running". It *plans*, *calls tools*, *waits for a human*, *answers* or
*fails* (`3.agent_states.py`):

```python
agent_transitions = {
    ("planning", "tool_needed"): "calling_tool",
    ("planning", "answer_ready"): "answering",
    ("calling_tool", "tool_done"): "planning",
    ("calling_tool", "tool_failed"): "failed",
    ("answering", "done"): "finished",
}
```

Clear states stop bugs like answering before the tool result arrives. LangGraph is built on this
idea: nodes are states, edges are transitions.

## Common mistakes

- **State classes that hold data of the order.** Keep data in the context (`Order`); states only
  hold behaviour.
- **Letting anyone set `order.state` directly** from outside. Transitions should happen inside the
  states.
- **No terminal state.** Define clearly where the process ends.
- **Too many states for a boolean.** If it is just on/off, a `bool` is fine.

## Hands-on exercises

**Exercise 1 · Traffic light.** `Red → Green → Yellow → Red`, each with a `next()` and a message.

<details class="solution"><summary>Solution</summary>

```python
class Red:
    def next(self, light):
        print("Red → Green: go")
        light.state = Green()
class Green:
    def next(self, light):
        print("Green → Yellow: slow down")
        light.state = Yellow()
class Yellow:
    def next(self, light):
        print("Yellow → Red: stop")
        light.state = Red()

class TrafficLight:
    def __init__(self): self.state = Red()
    def next(self): self.state.next(self)

t = TrafficLight()
for _ in range(4): t.next()
```

</details>

**Exercise 2 · Media player.** `Stopped`, `Playing`, `Paused` with `play()` and `pause()`.

<details class="solution"><summary>Solution</summary>

```python
class Stopped:
    def play(self, p):  print("▶ playing"); p.state = Playing()
    def pause(self, p): print("nothing to pause")
class Playing:
    def play(self, p):  print("already playing")
    def pause(self, p): print("⏸ paused"); p.state = Paused()
class Paused:
    def play(self, p):  print("▶ resumed"); p.state = Playing()
    def pause(self, p): print("already paused")

class Player:
    def __init__(self): self.state = Stopped()
    def play(self): self.state.play(self)
    def pause(self): self.state.pause(self)
```

</details>

**Exercise 3 · Draw it.** Using the table in `2.table.py`, list the allowed actions for
state `paid`.

<details class="solution"><summary>Solution</summary>

```python
def allowed(state):
    return [a for (s, a) in transitions if s == state]

print(allowed("paid"))    # ['ship', 'cancel']
```

Useful for showing or hiding buttons in a UI.

</details>

## Full source

<details class="source">
<summary>1.state.py</summary>

```{literalinclude} ../code/16-state/1.state.py
:language: python
```

</details>

<details class="source">
<summary>2.table.py</summary>

```{literalinclude} ../code/16-state/2.table.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_state.py <../code/16-state/0.no_state.py>` ·
{download}`1.state.py <../code/16-state/1.state.py>` ·
{download}`2.table.py <../code/16-state/2.table.py>` ·
{download}`3.agent_states.py <../code/16-state/3.agent_states.py>`
