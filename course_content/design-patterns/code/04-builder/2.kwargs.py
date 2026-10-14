"""Often enough in Python: keyword arguments with defaults (no builder needed)."""
from dataclasses import dataclass, field


@dataclass
class Pizza:
    size: str = "medium"
    crust: str = "regular"
    sauce: str = "tomato"
    toppings: list[str] = field(default_factory=list)
    extra_cheese: bool = False


print(Pizza(size="large", crust="thin", toppings=["olives"], extra_cheese=True))
print(Pizza())    # every default
