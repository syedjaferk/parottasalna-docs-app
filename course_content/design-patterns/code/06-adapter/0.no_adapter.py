"""Without Adapter: checkout knows every provider's method name and units."""


class RazorpayClient:
    def make_payment(self, rupees: float):
        print(f"Razorpay charged ₹{rupees}")


class StripeClient:
    def charge(self, amount_in_paise: int):
        print(f"Stripe charged {amount_in_paise} paise")


def checkout(provider, rupees):
    if isinstance(provider, RazorpayClient):
        provider.make_payment(rupees)
    elif isinstance(provider, StripeClient):
        provider.charge(int(rupees * 100))


checkout(RazorpayClient(), 499)
checkout(StripeClient(), 499)
