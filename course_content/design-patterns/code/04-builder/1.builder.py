"""Builder: set one thing per step, validate once in build()."""
from dataclasses import dataclass, field


@dataclass
class Pizza:
    size: str
    crust: str
    sauce: str
    toppings: list[str] = field(default_factory=list)
    extra_cheese: bool = False


class PizzaBuilder:
    def __init__(self):
        self.reset()

    def reset(self):
        self._size = "medium"
        self._crust = "regular"
        self._sauce = "tomato"
        self._toppings = []
        self._extra_cheese = False
        return self

    def size(self, s):        self._size = s;            return self
    def crust(self, c):       self._crust = c;           return self
    def sauce(self, s):       self._sauce = s;           return self
    def topping(self, t):     self._toppings.append(t);  return self
    def extra_cheese(self):   self._extra_cheese = True; return self

    def build(self) -> Pizza:
        if len(self._toppings) > 5:
            raise ValueError("max 5 toppings")
        pizza = Pizza(self._size, self._crust, self._sauce, list(self._toppings), self._extra_cheese)
        self.reset()                     # ready for the next pizza
        return pizza


pizza = (PizzaBuilder()
         .size("large")
         .crust("thin")
         .topping("olives")
         .topping("corn")
         .extra_cheese()
         .build())
print(pizza)
