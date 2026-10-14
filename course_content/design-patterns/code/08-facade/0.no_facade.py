"""Without Facade: every caller runs each subsystem step in the right order."""


class Inventory:
    def check(self, item): print(f"{item} in stock"); return True


class Payment:
    def charge(self, amount): print(f"charged ₹{amount}"); return True


class Shipping:
    def book(self, item): print(f"shipping booked for {item}")


class Notifier:
    def send(self, msg): print(f"sent: {msg}")


# every page that places an order repeats this:
inv, pay, ship, note = Inventory(), Payment(), Shipping(), Notifier()
if inv.check("laptop") and pay.charge(55000):
    ship.book("laptop")
    note.send("Order placed")
