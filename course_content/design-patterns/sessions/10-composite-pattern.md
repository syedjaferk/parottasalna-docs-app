# Session 10 · Composite pattern

## The big idea

Some data is a **tree**: a folder holds files and other folders, a company holds departments that
hold employees, a menu holds items and sub-menus. You want to treat **one item** and **a group of
items** the same way. For example, "give me the size" should work on a file and on a whole folder.

The **Composite** pattern gives single items (leaves) and groups (composites) the **same interface**.
A group simply asks each child and combines the answers.

**Everyday example:** a school. The principal says "everyone report at 9". That message works on one
teacher, one class or the whole school. Each level passes it down.

:::{admonition} In plain words
:class: tip
When your data is a **tree** (folders in folders), let a single item and a whole group answer the same questions. A group just asks its children and adds up their answers.

**Reach for it when:**

- your data nests: folders, menus, org charts, task plans
- you want `size()` or `show()` to work the same on one item or a whole branch
- you're tired of `isinstance` checks for "is it a leaf or a group?"
:::

## Without Composite

`0.no_composite.py`: you must check the type everywhere.

```python
def total_size(item):
    if isinstance(item, dict):                  # folder
        return sum(total_size(child) for child in item["children"])
    else:                                       # file
        return item["size"]
```

Every function (size, print, search, delete) needs the same `isinstance` check.

## With Composite

`1.composite.py`:

```python
from abc import ABC, abstractmethod

class Node(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def size(self) -> int: ...
    @abstractmethod
    def show(self, indent: int = 0): ...

class File(Node):                              # leaf
    def __init__(self, name, size):
        super().__init__(name)
        self._size = size
    def size(self): return self._size
    def show(self, indent=0):
        print(" " * indent + f"📄 {self.name} ({self._size} KB)")

class Folder(Node):                            # composite
    def __init__(self, name):
        super().__init__(name)
        self.children: list[Node] = []
    def add(self, node: Node):
        self.children.append(node)
        return self
    def size(self): return sum(c.size() for c in self.children)
    def show(self, indent=0):
        print(" " * indent + f"📁 {self.name} ({self.size()} KB)")
        for c in self.children:
            c.show(indent + 2)

root = Folder("project")
src = Folder("src").add(File("main.py", 4)).add(File("utils.py", 2))
docs = Folder("docs").add(File("readme.md", 1))
root.add(src).add(docs).add(File("LICENSE", 1))

root.show()
print(root.size())
```

```text
📁 project (8 KB)
  📁 src (6 KB)
    📄 main.py (4 KB)
    📄 utils.py (2 KB)
  📁 docs (1 KB)
    📄 readme.md (1 KB)
  📄 LICENSE (1 KB)
8
```

`root.size()` and `File("x", 3).size()` are called the same way. Recursion does the rest.

```{raw} html
:file: ../diagrams/s10-composite.html
```

## Composite + AI: a tree of tasks

An agent plan is a tree: "Write blog post" has sub-tasks "Research", "Outline", "Draft", and
"Research" has its own sub-tasks (`2.task_tree.py`):

```python
class Task:
    def __init__(self, name, minutes=0):
        self.name, self.minutes, self.subtasks = name, minutes, []

    def add(self, t):
        self.subtasks.append(t)
        return self

    def total_minutes(self):
        return self.minutes + sum(t.total_minutes() for t in self.subtasks)

    def run(self, depth=0):
        print("  " * depth + f"▶ {self.name}")
        for t in self.subtasks:
            t.run(depth + 1)

plan = Task("Write blog post").add(
    Task("Research").add(Task("Search papers", 20)).add(Task("Read docs", 15))
).add(Task("Outline", 10)).add(Task("Draft", 40))

plan.run()
print(plan.total_minutes())     # 85
```

Here one class plays both roles: a task with no sub-tasks is a leaf. That is fine in Python.

## Common mistakes

- **Cycles.** A folder added inside itself loops forever. Check before adding.
- **Leaf methods that make no sense** (`File.add()`). Keep `add()` only on the composite.
- **Slow recursion on huge trees.** Compute sizes once and cache them if the tree is large.
- **Using a tree where a flat list is enough.** Don't add structure you don't need.

## Hands-on exercises

**Exercise 1 · Count files.** Add `count()` that returns the number of files below any node.

<details class="solution"><summary>Solution</summary>

```python
class File(Node):
    def count(self): return 1

class Folder(Node):
    def count(self): return sum(c.count() for c in self.children)

print(root.count())    # 4
```

(Add `count` as an abstract method on `Node` too.)

</details>

**Exercise 2 · Find by name.** `find(name)` returns the first node with that name, or `None`.

<details class="solution"><summary>Solution</summary>

```python
class File(Node):
    def find(self, name):
        return self if self.name == name else None

class Folder(Node):
    def find(self, name):
        if self.name == name:
            return self
        for c in self.children:
            hit = c.find(name)
            if hit:
                return hit
        return None

print(root.find("utils.py").name)    # utils.py
```

</details>

**Exercise 3 · Menu prices.** Build a restaurant menu: a `Menu` holds `Dish`es and sub-`Menu`s
(Starters, Mains). A `Combo` menu's price is the sum of its items. Print the full menu.

<details class="solution"><summary>Solution</summary>

```python
class Dish:
    def __init__(self, name, price): self.name, self.price = name, price
    def total(self): return self.price
    def show(self, i=0): print(" " * i + f"{self.name} ₹{self.price}")

class Menu:
    def __init__(self, name): self.name, self.items = name, []
    def add(self, x): self.items.append(x); return self
    def total(self): return sum(x.total() for x in self.items)
    def show(self, i=0):
        print(" " * i + f"{self.name} (₹{self.total()})")
        for x in self.items: x.show(i + 2)

combo = Menu("Combo").add(Dish("Parotta", 30)).add(Menu("Curries").add(Dish("Salna", 40)).add(Dish("Kurma", 50)))
combo.show()
```

</details>

## Full source

<details class="source">
<summary>1.composite.py</summary>

```{literalinclude} ../code/10-composite/1.composite.py
:language: python
```

</details>

<details class="source">
<summary>2.task_tree.py</summary>

```{literalinclude} ../code/10-composite/2.task_tree.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_composite.py <../code/10-composite/0.no_composite.py>` ·
{download}`1.composite.py <../code/10-composite/1.composite.py>` ·
{download}`2.task_tree.py <../code/10-composite/2.task_tree.py>`
