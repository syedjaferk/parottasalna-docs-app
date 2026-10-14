"""The textbook Factory Method: subclasses decide which product to create."""
from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def send(self, msg: str): ...


class EmailNotifier(Notifier):
    def send(self, msg): print(f"EMAIL: {msg}")


class SMSNotifier(Notifier):
    def send(self, msg): print(f"SMS: {msg}")


class Alert(ABC):
    @abstractmethod
    def create_notifier(self) -> Notifier:      # <- the factory method
        ...

    def raise_alert(self, msg: str):
        self.create_notifier().send(msg)         # works with any notifier


class EmailAlert(Alert):
    def create_notifier(self) -> Notifier:
        return EmailNotifier()


class SMSAlert(Alert):
    def create_notifier(self) -> Notifier:
        return SMSNotifier()


EmailAlert().raise_alert("Disk is full")    # EMAIL: Disk is full
SMSAlert().raise_alert("Server down")       # SMS: Server down
