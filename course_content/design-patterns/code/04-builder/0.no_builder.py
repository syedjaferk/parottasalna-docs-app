"""Without Builder: a long positional constructor. Which True is which?"""


class Pizza:
    def __init__(self, size, crust, cheese, toppings, extra_cheese, sauce, gluten_free):
        self.size, self.crust, self.cheese = size, crust, cheese
        self.toppings, self.extra_cheese = toppings, extra_cheese
        self.sauce, self.gluten_free = sauce, gluten_free


p = Pizza("large", "thin", True, ["olives", "corn"], False, "tomato", True)
print(vars(p))
