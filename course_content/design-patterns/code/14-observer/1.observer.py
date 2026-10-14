"""Observer: subscribers register for an event; the publisher doesn't know who they are."""


class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list] = {}

    def subscribe(self, event: str, handler):
        self._subscribers.setdefault(event, []).append(handler)

    def unsubscribe(self, event: str, handler):
        self._subscribers[event].remove(handler)

    def publish(self, event: str, data):
        for handler in list(self._subscribers.get(event, [])):
            try:
                handler(data)
            except Exception as e:                 # one broken handler must not stop the rest
                print(f"handler {handler.__name__} failed: {e}")


bus = EventBus()


def email(order):      print(f"📧 email for {order['item']}")
def inventory(order):  print(f"📦 stock -1 for {order['item']}")
def analytics(order):  print(f"📊 logged {order['item']}")


bus.subscribe("order_placed", email)
bus.subscribe("order_placed", inventory)
bus.subscribe("order_placed", analytics)


class OrderService:
    def __init__(self, bus):
        self.bus = bus

    def place_order(self, item):
        print(f"Order placed: {item}")
        self.bus.publish("order_placed", {"item": item})


OrderService(bus).place_order("laptop")
