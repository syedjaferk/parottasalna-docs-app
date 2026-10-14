"""Strategy: each way of doing the job is its own class with the same interface."""
from abc import ABC, abstractmethod


class Discount(ABC):
    @abstractmethod
    def apply(self, total: float) -> float: ...


class NoDiscount(Discount):
    def apply(self, total): return total


class StudentDiscount(Discount):
    def apply(self, total): return total * 0.9


class PremiumDiscount(Discount):
    def apply(self, total): return total * 0.8


class FlatOff(Discount):
    def __init__(self, amount): self.amount = amount
    def apply(self, total): return max(total - self.amount, 0)


class Cart:
    def __init__(self, discount: Discount):
        self.discount = discount
        self.total = 0

    def add(self, price):
        self.total += price

    def checkout(self):
        return self.discount.apply(self.total)


cart = Cart(StudentDiscount())
cart.add(500)
cart.add(500)
print(cart.checkout())            # 900.0

cart.discount = FlatOff(100)      # swap at run time
print(cart.checkout())            # 900
