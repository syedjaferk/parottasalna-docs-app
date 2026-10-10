# Session 3 · A variable is a name, not a box

📖 Based on the blog post [Python Variable: Is a Container or a Reference?](https://learn.parottasalna.com/blog/python-variable-is-a-container-or-a-reference/).

:::{tip}
This is a **deep dive**. If you're brand new, skim it now and come back after Session 7 (lists).
It explains some of the most surprising bugs beginners hit.
:::

## The big idea

In many languages a variable is a **box** that holds a value. In Python, a variable is a **name
tag** tied to an object. The object lives somewhere in memory; the name just points to it. Two
names can point to the **same** object.

**Everyday example:** your friend is "Priya" at college and "Chellam" at home. Two names, one
person. If Priya gets a haircut, Chellam has the haircut too.

## Everything is an object

Numbers, text, lists, functions: all of them are objects.

```python
for thing in [26, "Idly", [1, 2], print]:
    print(type(thing).__name__, isinstance(thing, object))
```

```text
int True
str True
list True
builtin_function_or_method True
```

## Names point to objects: `id()`

`id()` gives an object's identity (in CPython, its memory address). A name has the same id as the
object it points to:

```python
age = 26
print(id(age) == id(26))
```

```text
True
```

## Two names, one object

```{raw} html
:file: ../diagrams/s03-refs.html
```

```python
a = [1, 2]
b = a              # b points to the SAME list, it's not a copy
b.append(3)
print(a)
print(a is b)
```

```text
[1, 2, 3]
True
```

`is` checks "same object?"; `==` checks "same value?". To get a separate list, make a **copy**:

```python
a = [1, 2]
b = a.copy()       # or list(a), or a[:]
b.append(3)
print(a, b, a is b)
```

```text
[1, 2] [1, 2, 3] False
```

### Why don't numbers and strings surprise us?

Numbers, strings and tuples are **immutable**: they can't change. `x += 1` doesn't change the
object 5; it makes a new object 6 and moves the name `x` to it:

```python
x = 5
y = x
x += 1
print(x, y)
```

```text
6 5
```

Lists, dictionaries and sets are **mutable**: changing them in place is seen through every name
that points to them.

## Where do names live? Namespaces

Python keeps names in **namespaces**: dictionaries that map names to objects. Each function call
gets its own local namespace; the module (your file) has a global one. Tying a name to an object
is called **binding**.

```python
def greet():
    message = "Vanakkam"
    print(locals())          # the function's own namespace

greet()
```

```text
{'message': 'Vanakkam'}
```

## How big is a variable?

`sys.getsizeof(x)` returns the size of the **object** `x` points to, not of the name:

```python
import sys
print(sys.getsizeof(10))     # an int object, in bytes
```

```text
28
```

The name itself is just a reference (a pointer): **8 bytes** on a 64-bit computer. We can estimate
it: a list of 1,000 references to the same object is about 8,000 bytes bigger than an empty list.

```python
import sys
size_of_one_reference = (sys.getsizeof([123] * 1000) - sys.getsizeof([])) / 1000
print(size_of_one_reference)
```

```text
8.0
```

## Summary

- A variable is a **label** for an object, not a container.
- Variables have no type; `type(x)` tells you the type of the **object** `x` points to.
- Names live in **namespaces**; a reference is 8 bytes on 64-bit Python.
- `b = a` never copies. Use `.copy()` when you need an independent object.

## Common mistakes

- **`b = a` to "back up" a list.** Changing `b` changes `a`. Use `b = a.copy()`.
- **Using `is` to compare values.** `x is 1000` may be `False` even when `x == 1000`. Use `==` for
  values; use `is` only with `None` (`if x is None:`).
- **Default list arguments.** `def add(item, bucket=[])` shares **one** list between all calls.
  Use `bucket=None`, then `if bucket is None: bucket = []`.

## Hands-on exercises

**Exercise 1 · Predict.** What does this print? `x = [1]; y = x; y = [2]; print(x)`

<details class="solution"><summary>Answer</summary>

`[1]`. `y = [2]` doesn't change the list; it moves the name `y` to a **new** list. Only
in-place changes (`append`, `y[0] = …`) affect the shared object.

</details>

**Exercise 2 · Same or equal?** Make two lists with the same values. Show that `==` is `True` but
`is` is `False`.

<details class="solution"><summary>Solution</summary>

```python
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b, a is b)     # True False
```

</details>

**Exercise 3 · Safe backup.** Back up `marks = [80, 90]`, change `marks[0]` to 85, and show the
backup still has 80.

<details class="solution"><summary>Solution</summary>

```python
marks = [80, 90]
backup = marks.copy()
marks[0] = 85
print(marks, backup)      # [85, 90] [80, 90]
```

</details>

**Exercise 4 · The shared default bug.** Run this and explain the output:

```python
def add_item(item, bucket=[]):
    bucket.append(item)
    return bucket

print(add_item("idly"))
print(add_item("dosa"))
```

<details class="solution"><summary>Answer and fix</summary>

It prints `['idly']`, then `['idly', 'dosa']`. The default list is created **once**, when the
function is defined, and every call shares it. Fix:

```python
def add_item(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

</details>

**Exercise 5 · Inside a function.** Write `def show(): x = 1; y = "a"; print(locals())`. What do you
see, and what happens to those names after the function returns?

<details class="solution"><summary>Answer</summary>

`{'x': 1, 'y': 'a'}`. The local namespace disappears when the function returns; if nothing else
points to those objects, Python frees them.

</details>
