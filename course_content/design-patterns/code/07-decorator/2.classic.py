"""The classic object Decorator: wrappers with the same interface stack like layers."""
from abc import ABC, abstractmethod


class Coffee(ABC):
    @abstractmethod
    def cost(self) -> int: ...

    @abstractmethod
    def description(self) -> str: ...


class Espresso(Coffee):
    def cost(self): return 100
    def description(self): return "Espresso"


class AddOn(Coffee):                       # the decorator base
    def __init__(self, coffee: Coffee):
        self._coffee = coffee


class Milk(AddOn):
    def cost(self): return self._coffee.cost() + 20
    def description(self): return self._coffee.description() + " + Milk"


class Sugar(AddOn):
    def cost(self): return self._coffee.cost() + 5
    def description(self): return self._coffee.description() + " + Sugar"


order = Sugar(Milk(Espresso()))
print(order.description(), order.cost())    # Espresso + Milk + Sugar 125

double_milk = Milk(Milk(Espresso()))
print(double_milk.description(), double_milk.cost())    # Espresso + Milk + Milk 140
