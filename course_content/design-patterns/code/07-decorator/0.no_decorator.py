"""Without Decorator: timing and logging are mixed into the real work."""
import time


def get_price(item):
    start = time.time()
    print(f"calling get_price({item})")
    price = {"apple": 120, "mango": 200}[item]
    print(f"took {time.time() - start:.4f}s")
    return price


print(get_price("apple"))
