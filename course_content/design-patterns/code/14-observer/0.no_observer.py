"""Without Observer: the order code calls every interested party itself."""


def send_email(item): print(f"📧 email for {item}")
def update_inventory(item): print(f"📦 stock -1 for {item}")
def notify_warehouse(item): print(f"🏭 warehouse told about {item}")
def log_analytics(item): print(f"📊 logged {item}")


class OrderService:
    def place_order(self, item):
        print(f"Order placed: {item}")
        send_email(item)          # tight coupling: every new reaction edits this method
        update_inventory(item)
        notify_warehouse(item)
        log_analytics(item)


OrderService().place_order("laptop")
