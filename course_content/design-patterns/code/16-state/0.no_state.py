"""Without State: the same if/elif ladder on a status string in every method."""


class Order:
    def __init__(self):
        self.status = "placed"

    def pay(self):
        if self.status == "placed":
            self.status = "paid"
            print("💰 payment received")
        elif self.status == "paid":
            print("already paid")
        elif self.status == "shipped":
            print("already shipped")
        elif self.status == "cancelled":
            print("order is cancelled")

    def ship(self):
        if self.status == "paid":
            self.status = "shipped"
            print("🚚 shipped")
        elif self.status == "placed":
            print("❌ pay first")
        else:
            print(f"can't ship: {self.status}")
    # ... and the same ladder again for cancel(), refund(), ...


o = Order()
o.ship()
o.pay()
o.ship()
