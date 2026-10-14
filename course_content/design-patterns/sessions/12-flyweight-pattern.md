# Session 12 · Flyweight pattern

## The big idea

If your program needs **thousands or millions of similar objects**, memory becomes the problem.
Often most of the data inside them is **identical**; only a small part is different. The
**Flyweight** pattern splits the data in two:

- **Intrinsic** state: shared, never changes (a tree's species, texture, colour). Stored **once**.
- **Extrinsic** state: unique per object (x, y position). Passed in from outside.

**Everyday example:** a printing press. There is one set of letter blocks "A", "B", "C". The page
uses them thousands of times in different positions. You don't carve a new "A" for every position.

:::{admonition} In plain words
:class: tip
When you have **thousands** of similar objects, store the big part they share **once**, and let each object keep only what is truly its own (like its position).

**Reach for it when:**

- you create a huge number of objects
- most of the data inside them is identical
- memory use is a real, measured problem
:::

## Without Flyweight

`0.no_flyweight.py`: every tree carries its own heavy data.

```python
import sys

class Tree:
    def __init__(self, x, y, species, texture):
        self.x, self.y = x, y
        self.species = species
        self.texture = texture          # imagine 1 MB of image data

forest = [Tree(i, i, "Neem", "x" * 1_000_000) for i in range(100)]
print(f"{sys.getsizeof(forest[0].texture) * 100 / 1e6:.0f} MB just for textures")
```

```text
100 MB just for textures
```

100 trees, 100 copies of the same texture. Imagine a game with 100,000 trees.

## With Flyweight

`1.flyweight.py`:

```python
class TreeType:                       # flyweight: shared
    def __init__(self, species, texture):
        self.species = species
        self.texture = texture

    def draw(self, x, y):
        print(f"Drawing {self.species} at ({x}, {y})")

class TreeFactory:
    _types: dict[str, TreeType] = {}

    @classmethod
    def get(cls, species, texture):
        if species not in cls._types:
            cls._types[species] = TreeType(species, texture)
        return cls._types[species]

class Tree:                           # context: only x and y
    def __init__(self, x, y, tree_type: TreeType):
        self.x, self.y, self.type = x, y, tree_type

    def draw(self):
        self.type.draw(self.x, self.y)

forest = [Tree(i, i * 2, TreeFactory.get("Neem", "x" * 1_000_000)) for i in range(100)]
print(len(TreeFactory._types))                          # 1
print(forest[0].type is forest[99].type)                # True
```

100 trees now share **one** texture. Memory drops from about 100 MB to about 1 MB.

```{raw} html
:file: ../diagrams/s12-flyweight.html
```

## Python already does this

Python itself reuses small objects (`2.python_builtin.py`):

```python
a = "hello"
b = "hello"
print(a is b)                 # True: strings can be shared (interning)

import sys
x = sys.intern("some long string from a file")
y = sys.intern("some long string from a file")
print(x is y)                 # True
```

`sys.intern` is a built-in flyweight for strings. Also, `__slots__` makes each instance smaller:

```python
class Point:
    __slots__ = ("x", "y")    # no per-object __dict__, saves memory
    def __init__(self, x, y):
        self.x, self.y = x, y
```

## Flyweight + AI: share the heavy parts

Loading an embedding model takes seconds and gigabytes. Many "retrievers" can share one
(`3.shared_model.py`):

```python
class ModelCache:
    _models = {}

    @classmethod
    def get(cls, name):
        if name not in cls._models:
            print(f"Loading {name}... (slow)")
            cls._models[name] = load_embedding_model(name)     # your loader
        return cls._models[name]

class Retriever:
    def __init__(self, collection, model_name="all-MiniLM-L6-v2"):
        self.collection = collection                  # extrinsic: different per retriever
        self.model = ModelCache.get(model_name)       # intrinsic: shared
```

100 retrievers, one model in memory.

## Common mistakes

- **Mutable shared state.** If one object changes the flyweight, all of them change. Keep it
  read-only.
- **Using it too early.** It only pays off with a very large number of objects. Measure first.
- **Mixing extrinsic data into the flyweight.** Position, owner, id → pass them in.
- **Never freeing the cache.** For long-running apps, cap it or use `weakref`.

## Hands-on exercises

**Exercise 1 · Measure.** Create 100,000 `Point` objects with and without `__slots__` and compare
memory using `tracemalloc`.

<details class="solution"><summary>Solution</summary>

```python
import tracemalloc

class PlainPoint:
    def __init__(self, x, y): self.x, self.y = x, y

class SlotPoint:
    __slots__ = ("x", "y")
    def __init__(self, x, y): self.x, self.y = x, y

for cls in (PlainPoint, SlotPoint):
    tracemalloc.start()
    items = [cls(i, i) for i in range(100_000)]
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(cls.__name__, f"{current / 1e6:.1f} MB")
```

`SlotPoint` uses noticeably less.

</details>

**Exercise 2 · Text editor glyphs.** Make a `Glyph` flyweight per character (font, size) and a
document with 10,000 characters that shares them.

<details class="solution"><summary>Solution</summary>

```python
class Glyph:
    def __init__(self, char, font, size):
        self.char, self.font, self.size = char, font, size

class GlyphFactory:
    _cache = {}
    @classmethod
    def get(cls, char, font="Arial", size=12):
        key = (char, font, size)
        if key not in cls._cache:
            cls._cache[key] = Glyph(*key)
        return cls._cache[key]

text = "hello world " * 1000
doc = [(GlyphFactory.get(ch), i) for i, ch in enumerate(text)]   # (glyph, position)
print(len(doc), "characters,", len(GlyphFactory._cache), "glyph objects")
```

</details>

**Exercise 3 · Particles.** A game has 50,000 bullets of 3 types. Share the sprite per type.

<details class="solution"><summary>Solution</summary>

```python
class BulletType:
    def __init__(self, name, sprite): self.name, self.sprite = name, sprite

class BulletTypes:
    _t = {}
    @classmethod
    def get(cls, name):
        return cls._t.setdefault(name, BulletType(name, f"{name}.png-data"))

class Bullet:
    def __init__(self, x, y, speed, kind):
        self.x, self.y, self.speed, self.kind = x, y, speed, BulletTypes.get(kind)

bullets = [Bullet(i, 0, 5, ["small", "medium", "big"][i % 3]) for i in range(50_000)]
print(len(BulletTypes._t))    # 3
```

</details>

## Full source

<details class="source">
<summary>1.flyweight.py</summary>

```{literalinclude} ../code/12-flyweight/1.flyweight.py
:language: python
```

</details>

<details class="source">
<summary>3.shared_model.py</summary>

```{literalinclude} ../code/12-flyweight/3.shared_model.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_flyweight.py <../code/12-flyweight/0.no_flyweight.py>` ·
{download}`1.flyweight.py <../code/12-flyweight/1.flyweight.py>` ·
{download}`2.python_builtin.py <../code/12-flyweight/2.python_builtin.py>` ·
{download}`3.shared_model.py <../code/12-flyweight/3.shared_model.py>`
