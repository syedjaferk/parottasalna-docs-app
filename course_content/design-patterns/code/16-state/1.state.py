"""State: each state is a class; the order delegates to its current state."""
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

    def ship(self, order):
        print("❌ pay first")

    def cancel(self, order):
        print("🚫 order cancelled")
        order.state = Cancelled()


class Paid(OrderState):
    def pay(self, order):
        print("already paid")

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
