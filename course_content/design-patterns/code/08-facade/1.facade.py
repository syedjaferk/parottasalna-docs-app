"""Facade: one simple front door that runs the whole order flow."""


class Inventory:
    def check(self, item): print(f"{item} in stock"); return True


class Payment:
    def charge(self, amount): print(f"charged ₹{amount}"); return True
    def refund(self, amount): print(f"refunded ₹{amount}")


class Shipping:
    def book(self, item): print(f"shipping booked for {item}")


class Notifier:
    def send(self, msg): print(f"sent: {msg}")


class OrderFacade:
    def __init__(self):
        self._inventory = Inventory()
        self._payment = Payment()
        self._shipping = Shipping()
        self._notifier = Notifier()

    def place_order(self, item: str, amount: int) -> bool:
        if not self._inventory.check(item):
            return False
        if not self._payment.charge(amount):
            return False
        self._shipping.book(item)
        self._notifier.send(f"Order placed for {item}")
        return True

    def cancel_order(self, item: str, amount: int):
        self._payment.refund(amount)
        self._notifier.send(f"Order cancelled for {item}")


shop = OrderFacade()
shop.place_order("laptop", 55000)
shop.cancel_order("laptop", 55000)
