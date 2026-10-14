"""Adapter: define the interface you want, and wrap each provider to fit it."""
from abc import ABC, abstractmethod


class RazorpayClient:                       # third-party code you can't change
    def make_payment(self, rupees: float):
        print(f"Razorpay charged ₹{rupees}")


class StripeClient:                         # third-party code you can't change
    def charge(self, amount_in_paise: int):
        print(f"Stripe charged {amount_in_paise} paise")


class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, rupees: float): ...


class RazorpayAdapter(PaymentGateway):
    def __init__(self, client: RazorpayClient):
        self._client = client

    def pay(self, rupees):
        self._client.make_payment(rupees)


class StripeAdapter(PaymentGateway):
    def __init__(self, client: StripeClient):
        self._client = client

    def pay(self, rupees):
        self._client.charge(int(rupees * 100))     # translate rupees -> paise


def checkout(gateway: PaymentGateway, rupees: float):
    gateway.pay(rupees)


checkout(RazorpayAdapter(RazorpayClient()), 499)
checkout(StripeAdapter(StripeClient()), 499)
