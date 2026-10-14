"""Factory Method: one function decides which class to create; everyone else just asks."""


class EmailNotifier:
    def send(self, msg): print(f"EMAIL: {msg}")


class SMSNotifier:
    def send(self, msg): print(f"SMS: {msg}")


def create_notifier(channel: str):
    notifiers = {"email": EmailNotifier, "sms": SMSNotifier}
    try:
        return notifiers[channel]()
    except KeyError:
        raise ValueError(f"unknown channel {channel!r}. Choose from {list(notifiers)}") from None


def welcome_user(channel: str):
    create_notifier(channel).send("Welcome!")


def send_invoice(channel: str):
    create_notifier(channel).send("Invoice ready")


welcome_user("sms")       # SMS: Welcome!
send_invoice("email")     # EMAIL: Invoice ready
try:
    welcome_user("pigeon")
except ValueError as e:
    print(e)              # unknown channel 'pigeon'. Choose from ['email', 'sms']
