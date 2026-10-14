"""The Pythonic Strategy: functions are objects, so a strategy can be just a function."""


def student(total):  return total * 0.9
def premium(total):  return total * 0.8
def flat_100(total): return max(total - 100, 0)


def checkout(total, discount=lambda t: t):
    return discount(total)


print(checkout(1000))               # 1000 (no discount)
print(checkout(1000, student))      # 900.0
print(checkout(1000, flat_100))     # 900

strategies = {"student": student, "premium": premium, "flat": flat_100}
print(checkout(1000, strategies["premium"]))    # 800.0: pick by name (a mini factory)
