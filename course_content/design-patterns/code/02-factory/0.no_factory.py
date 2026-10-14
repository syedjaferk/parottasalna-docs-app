"""Without a factory: the same if/elif is copied into every function."""


class EmailNotifier:
    def send(self, msg): print(f"EMAIL: {msg}")


class SMSNotifier:
    def send(self, msg): print(f"SMS: {msg}")


def welcome_user(channel: str):
    if channel == "email":
        n = EmailNotifier()
    elif channel == "sms":
        n = SMSNotifier()
    else:
        raise ValueError(f"unknown channel {channel}")
    n.send("Welcome!")


def send_invoice(channel: str):
    if channel == "email":      # same if/elif copied again
        n = EmailNotifier()
    elif channel == "sms":
        n = SMSNotifier()
    else:
        raise ValueError(f"unknown channel {channel}")
    n.send("Invoice ready")


welcome_user("email")
send_invoice("sms")
