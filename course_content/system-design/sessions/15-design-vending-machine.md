# Chapter 15 · Design a vending machine (state machine)

## The problem

Another **object-oriented design** question. The machine accepts money, lets a user pick a product,
dispenses it and returns change. The interesting part is that **what a button does depends on the
current state**.

```{raw} html
:file: ../diagrams/vending-machine.html
```

## Requirements to ask for

- Products with price and quantity; coins and notes accepted.
- Select, cancel/refund, return correct change.
- An admin can restock and collect cash.
- Out-of-stock and "cannot make change" cases.

## The State pattern

Instead of `if state == "idle" ... elif state == "has_money" ...` in every method, give each state
its own class that implements the same methods.

```python
class State:
    def insert_coin(self, m, coin): raise InvalidAction()
    def select(self, m, code):      raise InvalidAction()
    def cancel(self, m):            raise InvalidAction()

class Idle(State):
    def insert_coin(self, m, coin):
        m.balance += coin
        m.state = HasMoney()

class HasMoney(State):
    def insert_coin(self, m, coin): m.balance += coin
    def cancel(self, m):
        m.refund(m.balance); m.balance = 0; m.state = Idle()
    def select(self, m, code):
        item = m.inventory.get(code)
        if item.qty == 0: raise SoldOut()
        if m.balance < item.price: raise NotEnoughMoney()
        m.state = Dispensing(); m.state.dispense(m, item)
```

Adding a new state (for example `Maintenance`) means adding a class, not editing every method.

## Classes

`VendingMachine` (current state, balance), `Inventory` (code to `Slot(product, qty)`), `Product`,
`Coin`/`Note`, `ChangeCalculator`, and the `State` classes above.

## Making change

Greedy (largest coin first) works for normal coin systems. If the machine cannot make exact change,
refuse the sale up front, before taking the item out.

## Failure cases to mention

- **Power loss mid-vend:** write the state and balance to non-volatile storage; on reboot refund.
- **Jammed slot:** treat dispensing as a step that can fail; refund if no item drops.
- **Concurrent use** is not an issue for one machine, but a fleet needs a backend (sales sync,
  restock alerts) which is an easy extension to describe.

## Common mistakes

- Booleans like `hasMoney`, `isDispensing` scattered everywhere instead of one state.
- Dispensing before checking change.
- Not defining what happens on invalid input in each state.

:::{admonition} Try it in the playground
:class: important
Model it in [Design a Vending Machine](/system-design/vending-machine/).
:::
