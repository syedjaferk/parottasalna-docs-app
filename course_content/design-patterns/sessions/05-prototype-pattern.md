# Session 5 · Prototype pattern

## The big idea

Sometimes creating an object from scratch is slow or complicated (loading a file, calling an API,
long setup). If you already have a ready object, it is easier to **copy it** and change a few
things. The **Prototype** pattern creates new objects by cloning an existing one.

**Everyday example:** a photocopy of a filled form. You copy the form and only change the name,
instead of writing everything again.

:::{admonition} In plain words
:class: tip
If making an object from scratch is slow, make one carefully, then **copy it** and change a few things. Use a *deep* copy so the copies don't share their insides.

**Reach for it when:**

- creating the object is slow or complicated (files, API calls, long setup)
- the new objects are mostly the same as an existing one
- you keep ready-made templates to start from
:::

## Without Prototype

`0.no_prototype.py`: every new object repeats the long setup.

```python
class AgentConfig:
    def __init__(self):
        print("Loading defaults... (slow)")
        self.model = "gpt-oss-120b"
        self.temperature = 0.2
        self.tools = ["search", "calculator"]

support_bot = AgentConfig()
sales_bot = AgentConfig()     # slow setup again
sales_bot.temperature = 0.7
```

## With Prototype: `copy.deepcopy`

`1.prototype.py`:

```python
import copy

base = AgentConfig()                 # slow setup once

support_bot = copy.deepcopy(base)
sales_bot = copy.deepcopy(base)
sales_bot.temperature = 0.7
sales_bot.tools.append("crm")

print(base.tools)         # ['search', 'calculator']   ← base untouched
print(sales_bot.tools)    # ['search', 'calculator', 'crm']
```

```text
Loading defaults... (slow)
['search', 'calculator']
['search', 'calculator', 'crm']
```

The slow setup ran once. Each copy can change without affecting the others.

```{raw} html
:file: ../diagrams/s05-prototype.html
```

## Shallow copy vs deep copy

This is the part that causes bugs (`2.shallow_vs_deep.py`):

```python
import copy

a = {"name": "bot", "tools": ["search"]}

shallow = copy.copy(a)
shallow["tools"].append("calc")
print(a["tools"])         # ['search', 'calc']   ← a changed too!

deep = copy.deepcopy(a)
deep["tools"].append("crm")
print(a["tools"])         # ['search', 'calc']   ← a is safe
```

A shallow copy copies the outer dictionary but **shares** the inner list. A deep copy copies
everything inside as well.

## A registry of prototypes

Keep ready-made templates and clone by name (`3.registry.py`):

```python
class PrototypeRegistry:
    def __init__(self):
        self._items = {}

    def register(self, name, obj):
        self._items[name] = obj

    def clone(self, name, **changes):
        obj = copy.deepcopy(self._items[name])
        for k, v in changes.items():
            setattr(obj, k, v)
        return obj

registry = PrototypeRegistry()
registry.register("default", base)
bot = registry.clone("default", temperature=0.9)
```

## Prototype + AI: agent templates

Keep one tested "base agent" with its tools and system prompt. Create a customer-support agent, a
sales agent and a coding agent by cloning it and changing the prompt. Dataclasses make this easy
with `dataclasses.replace(base, system_prompt="...")`, which is a shallow clone with changes.

## Common mistakes

- **Shallow copying nested data.** Lists and dicts inside are shared. Use `deepcopy`.
- **Copying things that can't be copied**: open files, database connections, locks. Give the class
  a `__deepcopy__` method that skips or recreates them.
- **Cloning when creating is cheap.** For small objects, normal construction is clearer.

## Hands-on exercises

**Exercise 1 · Prove the bug.** Make a shallow copy of an object with a list, change the copy, and
show the original changed.

<details class="solution"><summary>Solution</summary>

```python
import copy

class Config:
    def __init__(self):
        self.tags = ["a"]

c1 = Config()
c2 = copy.copy(c1)
c2.tags.append("b")
print(c1.tags)    # ['a', 'b']
```

</details>

**Exercise 2 · Game enemies.** Create one `Orc` template with 100 health and a `weapons` list,
then spawn 3 enemies with different names.

<details class="solution"><summary>Solution</summary>

```python
import copy

class Enemy:
    def __init__(self, name, health, weapons):
        self.name, self.health, self.weapons = name, health, weapons

template = Enemy("Orc", 100, ["axe"])

enemies = []
for i in range(3):
    e = copy.deepcopy(template)
    e.name = f"Orc-{i + 1}"
    enemies.append(e)

enemies[0].weapons.append("shield")
print(enemies[1].weapons)    # ['axe']   ← independent
```

</details>

**Exercise 3 · Custom `clone()`.** Add a `clone()` method that returns a deep copy.

<details class="solution"><summary>Solution</summary>

```python
import copy

class Document:
    def __init__(self, title, sections):
        self.title, self.sections = title, sections

    def clone(self):
        return copy.deepcopy(self)

report = Document("Monthly report", ["intro", "numbers"])
march = report.clone()
march.title = "March report"
```

</details>

## Full source

<details class="source">
<summary>1.prototype.py</summary>

```{literalinclude} ../code/05-prototype/1.prototype.py
:language: python
```

</details>

<details class="source">
<summary>3.registry.py</summary>

```{literalinclude} ../code/05-prototype/3.registry.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_prototype.py <../code/05-prototype/0.no_prototype.py>` ·
{download}`1.prototype.py <../code/05-prototype/1.prototype.py>` ·
{download}`2.shallow_vs_deep.py <../code/05-prototype/2.shallow_vs_deep.py>` ·
{download}`3.registry.py <../code/05-prototype/3.registry.py>`
