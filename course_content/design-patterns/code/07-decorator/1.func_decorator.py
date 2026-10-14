"""Python function decorators: add timing and logging without touching the function."""
import time
from functools import wraps


def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter() - start:.4f}s")
        return result
    return wrapper


def logged(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}{args}")
        return func(*args, **kwargs)
    return wrapper


@logged
@timed
def get_price(item):
    """Look up the price of a fruit."""
    return {"apple": 120, "mango": 200}[item]


print(get_price("apple"))
print(get_price.__name__, "-", get_price.__doc__)    # @wraps keeps the real name and docstring
