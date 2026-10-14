"""Without Strategy: a growing if/elif for every offer."""


def checkout(total, customer_type):
    if customer_type == "regular":
        return total
    elif customer_type == "student":
        return total * 0.9
    elif customer_type == "premium":
        return total * 0.8
    elif customer_type == "festival":
        return total - 100
    raise ValueError(customer_type)


for kind in ("regular", "student", "premium", "festival"):
    print(kind, checkout(1000, kind))
