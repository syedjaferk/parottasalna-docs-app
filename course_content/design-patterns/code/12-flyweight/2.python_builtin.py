"""Python already shares some objects: string interning and __slots__."""
import sys
import tracemalloc

a = "hello"
b = "hello"
print(a is b)                 # True: short literal strings are interned

x = sys.intern("some long string from a file " + str(42))
y = sys.intern("some long string from a file " + str(42))
print(x is y)                 # True: sys.intern makes equal strings share one object


class PlainPoint:
    def __init__(self, x, y):
        self.x, self.y = x, y


class SlotPoint:
    __slots__ = ("x", "y")    # no per-object __dict__, saves memory

    def __init__(self, x, y):
        self.x, self.y = x, y


for cls in (PlainPoint, SlotPoint):
    tracemalloc.start()
    points = [cls(i, i) for i in range(100_000)]
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"{cls.__name__:10} {current / 1e6:5.1f} MB for 100,000 points")
