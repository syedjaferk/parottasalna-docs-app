# Chapter 76 · Design a vending machine (state machine)

## Concepts to review first

This design is built from earlier chapters. Skim them if any term feels new:

- [Event-driven architecture](58-event-driven-architecture.md)
- [Fault tolerance](09-fault-tolerance.md)
- [Concurrency vs parallelism](62-concurrency-vs-parallelism.md)
- [Message queues](44-message-queues.md)

## The problem

Another **object-oriented design** question. A vending machine accepts money, lets a user pick a product, dispenses
it and returns change. The interesting part is that **what a button does depends on the machine's current state**:
pressing "select" with no money, with enough money, or with a jammed slot, are three different outcomes.

```{raw} html
:file: ../diagrams/vending-machine.html
```

## Step 1: clarify requirements

- Up to 40 slots; each holds one product with a **price** and a **quantity**.
- Accepts **coins** (and notes); returns correct **change**; supports **cancel and refund**.
- An **admin** can restock and collect cash.
- Must keep working with **no network**; must not lose a customer's money on a fault.
- Out of scope: card payments, remote management (mention as extensions).

## Step 2: list the states and events

| State | Meaning |
|---|---|
| **Idle** | Waiting; no money inserted |
| **HasMoney** | Money inserted; waiting for a selection |
| **Dispensing** | Validated; the motor is delivering the item |
| **OutOfService** | Jam, no change available, or maintenance |

| Event | Idle | HasMoney | Dispensing |
|---|---|---|---|
| **insert coin** | add, go to HasMoney | add | reject |
| **select item** | reject ("insert money first") | validate, then dispense | reject |
| **cancel** | nothing | refund, go to Idle | reject |

A table like this shows you covered **every state and event combination**.

## Step 3: the State pattern

Instead of `if state == "idle" ... elif state == "has_money"` repeated in every method, give each state its **own
class** with the same methods:

```python
class SoldOut(Exception): pass
class NotEnoughMoney(Exception): pass
class NoChange(Exception): pass

COINS = (10, 5, 2, 1)

def make_change(amount, stock):
    """Greedy: largest coin first, using only coins the machine really has. None if impossible."""
    stock, change = dict(stock), []
    for coin in COINS:
        while amount >= coin and stock.get(coin, 0) > 0:
            amount -= coin
            stock[coin] -= 1
            change.append(coin)
    return change if amount == 0 else None

class State:
    name = "State"
    def insert(self, m, coin):   raise RuntimeError(f"{self.name}: cannot insert a coin now")
    def select(self, m, code):   raise RuntimeError(f"{self.name}: cannot select now")
    def cancel(self, m):         raise RuntimeError(f"{self.name}: nothing to cancel")

class Idle(State):
    name = "Idle"
    def insert(self, m, coin):
        m.balance += coin
        m.coin_stock[coin] = m.coin_stock.get(coin, 0) + 1
        m.state = HasMoney()
    def select(self, m, code):
        raise RuntimeError("Idle: insert money first")
    def cancel(self, m):
        return []

class HasMoney(State):
    name = "HasMoney"
    def insert(self, m, coin):
        m.balance += coin
        m.coin_stock[coin] = m.coin_stock.get(coin, 0) + 1
    def select(self, m, code):
        slot = m.slots[code]
        if slot["qty"] == 0:
            raise SoldOut(code)
        if m.balance < slot["price"]:
            raise NotEnoughMoney(f"need {slot['price'] - m.balance} more")
        change = make_change(m.balance - slot["price"], m.coin_stock)    # validate BEFORE the irreversible step
        if change is None:
            raise NoChange("cannot make exact change")
        m.state = Dispensing()
        return m.state.dispense(m, code, change)
    def cancel(self, m):
        refund = make_change(m.balance, m.coin_stock) or []
        for coin in refund:
            m.coin_stock[coin] -= 1
        m.balance, m.state = 0, Idle()
        return refund

class Dispensing(State):
    name = "Dispensing"
    def dispense(self, m, code, change):
        m.slots[code]["qty"] -= 1                       # the motor drops the item
        for coin in change:
            m.coin_stock[coin] -= 1
        m.balance, m.state = 0, Idle()                  # back to Idle for the next customer
        return (code, change)

class VendingMachine:
    def __init__(self, slots, coin_stock):
        self.slots, self.coin_stock, self.balance, self.state = slots, coin_stock, 0, Idle()
    def insert(self, coin):  return self.state.insert(self, coin)
    def select(self, code):  return self.state.select(self, code)
    def cancel(self):        return self.state.cancel(self)

machine = VendingMachine(
    slots={"A1": {"price": 20, "qty": 2}, "B2": {"price": 35, "qty": 0}},
    coin_stock={10: 5, 5: 5, 2: 5, 1: 5},
)

def attempt(label, action):
    try:
        print(f"{label:<34} -> {action()}")
    except Exception as e:
        print(f"{label:<34} -> {type(e).__name__}: {e}")

attempt("select with no money", lambda: machine.select("A1"))
attempt("insert 10, insert 10, insert 5", lambda: [machine.insert(c) for c in (10, 10, 5)] and f"balance {machine.balance}, state {machine.state.name}")
attempt("select A1 (price 20, paid 25)", lambda: machine.select("A1"))
attempt("insert 10, select B2 (sold out)", lambda: (machine.insert(10), machine.select("B2"))[1])
attempt("cancel (refund the 10)", lambda: machine.cancel())
attempt("insert 5, select A1 (needs 20)", lambda: (machine.insert(5), machine.select("A1"))[1])
attempt("cancel again", lambda: machine.cancel())
print("A1 left:", machine.slots["A1"]["qty"], "| state:", machine.state.name)
```

**Output:**

```text
select with no money               -> RuntimeError: Idle: insert money first
insert 10, insert 10, insert 5     -> balance 25, state HasMoney
select A1 (price 20, paid 25)      -> ('A1', [5])
insert 10, select B2 (sold out)    -> SoldOut: B2
cancel (refund the 10)             -> [10]
insert 5, select A1 (needs 20)     -> NotEnoughMoney: need 15 more
cancel again                       -> [5]
A1 left: 1 | state: Idle
```

Read the output top to bottom: the same `select` call did different things depending on the state, with **no
`if` ladder** anywhere. Adding a `Maintenance` state is a new class, not an edit to every method.

## Step 4: making change correctly

Greedy (largest coin first) is optimal for normal currencies, but the machine only owns the coins in its tray.
**Check that exact change is possible before dispensing**, and refuse the sale otherwise (or accept only exact
money, as many machines show with an "exact change only" light).

```python
def make_change(amount, stock):
    stock, change = dict(stock), []
    for coin in (10, 5, 2, 1):
        while amount >= coin and stock.get(coin, 0) > 0:
            amount -= coin
            stock[coin] -= 1
            change.append(coin)
    return change if amount == 0 else None

print("37 with a full tray      :", make_change(37, {10: 5, 5: 5, 2: 5, 1: 5}))
print("37 with only 10s and 5s  :", make_change(37, {10: 5, 5: 5}))
print("6 with only 5s           :", make_change(6, {5: 9}))
```

**Output:**

```text
37 with a full tray      : [10, 10, 10, 5, 2]
37 with only 10s and 5s  : None
6 with only 5s           : None
```

## Step 5: failure cases

| Fault | Safe behaviour |
|---|---|
| **Power loss mid-vend** | Persist balance and state to durable storage before moving the motor; on reboot, refund |
| **Item jams in the slot** | The motor reports no drop: refund the customer, mark the slot faulty |
| **Sold out** | Reject the selection, keep the money available so the customer can choose again |
| **No exact change** | Reject before dispensing (the code above) |
| **Concurrent admin and customer** | Serialise changes to a slot's quantity with a lock so an update is not lost |
| **Invalid event in a state** | Defined, safe response for every state/event pair (the table in step 2) |

## Step 6: extensions

- **Payment methods** (Strategy pattern): a `PaymentMethod` interface with `CoinPayment`, `CardPayment`, `UpiPayment`.
- **Fleet of 10,000 machines:** each machine is **offline-first** and authoritative for its own sales; it sends sales,
  stock and fault events to a backend through a queue when it has a connection. The backend powers restock routes and
  reports. A central server must **not** approve every sale (a network blip would stop sales).
- **Events:** emit `ItemSold`, `SlotEmpty`, `JamDetected` so restocking is driven by data.

## Trade-offs

| Choice | You gain | You pay |
|---|---|---|
| State pattern | Clear behaviour per state, easy to extend | More classes than a simple `switch` |
| Validate before the irreversible step | Never trap a customer's money | Some sales refused (no change) |
| Offline-first fleet | Machines always work | Backend data arrives late |
| Persisting state on every step | Survives power loss | Slightly slower, wear on flash storage |

## Common mistakes

:::{warning}
- Boolean flags like `hasMoney` and `isDispensing` instead of one explicit state.
- Dispensing before checking that change can be made.
- No defined behaviour for an action that is invalid in the current state.
- Forgetting power loss and jams.
:::

## Try it yourself

1. Add a `Maintenance` state. Which existing classes must change?
2. A user inserts 50 for a 35 item, and the tray holds only 10s. What should happen?
3. When is a simple `switch` statement better than the State pattern?

<details class="solution"><summary>Answers</summary>

1. None of the existing states. Add a `Maintenance` class, and let the machine switch to it on an admin event (plus a transition out).
2. Change is 15, which cannot be made with 10s. The machine should refuse (`NoChange`) before dispensing and offer a refund.
3. When there are only two simple states and no growth expected: the pattern then adds more code than clarity.

</details>

:::{admonition} Try it in the playground
:class: important
Model it in [Design a Vending Machine](/system-design/vending-machine/).
:::

:::{admonition} Next
:class: important
Next case study: [Design a distributed key-value store](77-design-key-value-store.md).
:::
