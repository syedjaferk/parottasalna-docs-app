# Session 2 · Variables, constants and data types

📖 Based on the blog post [Python Fundamentals: Constants, Variables and Data Types](https://learn.parottasalna.com/blog/python-fundamentals-constants-variables-and-data-types/).

## The big idea

Programs remember things in **variables**: a name for a value, so you can use it again. Every
value also has a **type** (number, text, list…) that decides what you can do with it: you can
add numbers, join text, add items to a list.

**Everyday example:** labelled jars in a kitchen. The label ("sugar") is the variable name; what's
inside is the value; and you don't pour rice into the tea, because the *kind* of thing matters.
(In [Session 3](03-variables-are-references.md) we'll see the label is really a tag *pointing* to
the jar.)

## Making a variable

```python
age = 25                 # int
name = "John Doe"        # str
height = 5.9             # float
is_student = True        # bool
print(name, age, height, is_student)
```

```text
John Doe 25 5.9 True
```

`=` means **"assign"**, not "is equal to". `age = 25` means *"let the name `age` refer to 25"*.

### Naming rules

| ✅ Valid | ❌ Invalid | Why invalid |
|---|---|---|
| `my_variable` | `1variable` | can't start with a digit |
| `variable1` | `my-variable` | `-` means minus |
| `_hidden` | `for` | `for` is a Python keyword |
| `userName` | `my variable` | no spaces |

Names are **case-sensitive**: `age`, `Age` and `AGE` are three different variables. Python's
convention is `snake_case`: lowercase words joined by underscores.

## Many at once, swapping and unpacking

```python
a, b, c = 5, 10, 15            # three variables in one line
print(a, b, c)

x, y = 1, 2
x, y = y, x                    # swap without a temporary variable
print(x, y)

person = ("Alice", 30, "Engineer")
name, age, profession = person     # unpack a tuple into variables
print(name, profession)
```

```text
5 10 15
2 1
Alice Engineer
```

## Dynamic typing

You never declare a type. Python works it out from the value, and a name can later point to a
different type:

```python
my_var = 42
print(type(my_var))
my_var = "Python"
print(type(my_var))
```

```text
<class 'int'>
<class 'str'>
```

## Constants

A constant is a value that shouldn't change, like π or the maximum number of users. Python has no
real constants; by **convention** we write them in `UPPER_CASE` so everyone knows not to change
them:

```python
PI = 3.14159
MAX_USERS = 100
```

Python won't stop you writing `PI = 3`, but your teammates will!

## The data types

```{raw} html
:file: ../diagrams/s02-types.html
```

| Type | Example | Notes |
|---|---|---|
| `int` | `42`, `-7` | whole numbers, any size |
| `float` | `3.14`, `2.0` | decimals |
| `complex` | `2 + 3j` | for maths and engineering |
| `str` | `"Idly"` | text, in quotes |
| `bool` | `True`, `False` | yes/no |
| `NoneType` | `None` | "no value" |
| `list` | `[1, 2, 3]` | ordered, changeable ([Session 7](07-lists.md)) |
| `tuple` | `(1, 2, 3)` | ordered, unchangeable ([Session 8](08-tuples.md)) |
| `range` | `range(5)` | a sequence of numbers 0–4 |
| `dict` | `{"rice": 60}` | key → value ([Session 9](09-dictionaries.md)) |
| `set` | `{1, 2, 3}` | unique items ([Session 10](10-sets.md)) |
| `frozenset` | `frozenset({1, 2})` | a set that can't change |

:::{note}
Since Python 3.7, dictionaries **keep the order** in which you add keys. Older material
(including some blog posts) still calls them "unordered".
:::

### Converting between types

```python
print(int("42") + 1)       # text → number
print(str(42) + "!")       # number → text
print(float("3.5"))
print(int(3.99))           # cuts off the decimals, doesn't round
print(bool(0), bool(""), bool("0"))
```

```text
43
42!
3.5
3
False False True
```

`0`, `""`, `[]`, `{}` and `None` count as `False`; almost everything else is `True`, even the text
`"0"`.

## Why data types matter

The type decides which operations work:

```python
print(5 + 3)        # numbers add
print("5" + "3")    # strings join
print("5" * 3)      # a string repeats
```

```text
8
53
555
```

Mixing them (`"5" + 3`) raises a `TypeError`. Python refuses to guess what you meant.

## Common mistakes

- **Using `=` to compare.** `if age = 18:` is a syntax error. Comparison is `==`
  ([Session 4](04-operators-conditionals-input.md)).
- **Quotes around numbers.** `age = "25"` is text; `age + 1` fails. Use `age = 25`.
- **Overwriting built-ins.** `list = [1, 2]` or `print = 5` hides Python's own `list`/`print` for
  the rest of the program.
- **Expecting `int(3.99)` to round.** It truncates to 3. Use `round(3.99)` for 4.

## Hands-on exercises

**Exercise 1 · Introduce yourself.** Store your name, age, city and whether you're a student in
four variables, then print one sentence using all four.

<details class="solution"><summary>Solution</summary>

```python
name = "Priya"
age = 21
city = "Madurai"
is_student = True
print(f"I am {name}, {age} years old, from {city}. Student: {is_student}")
```

</details>

**Exercise 2 · Valid or not?** Which of these names are valid: `total_marks`, `2nd_place`,
`_count`, `class`, `firstName`, `price$`?

<details class="solution"><summary>Answer</summary>

Valid: `total_marks`, `_count`, `firstName`. Invalid: `2nd_place` (starts with a digit), `class`
(keyword), `price$` (`$` isn't allowed).

</details>

**Exercise 3 · Swap.** Given `a = "tea"` and `b = "coffee"`, swap them in one line and print both.

<details class="solution"><summary>Solution</summary>

```python
a, b = "tea", "coffee"
a, b = b, a
print(a, b)     # coffee tea
```

</details>

**Exercise 4 · What type?** Print the type of `10`, `10.0`, `"10"`, `True`, `None`, `[10]`,
`(10,)` and `{10}`.

<details class="solution"><summary>Solution</summary>

```python
for value in [10, 10.0, "10", True, None, [10], (10,), {10}]:
    print(repr(value), type(value))
```

`int`, `float`, `str`, `bool`, `NoneType`, `list`, `tuple`, `set`.

</details>

**Exercise 5 · Circle area.** Use a constant `PI = 3.14159` and a variable `radius = 7` to print the
area (π r²) with two decimals.

<details class="solution"><summary>Solution</summary>

```python
PI = 3.14159
radius = 7
area = PI * radius ** 2
print(f"Area: {area:.2f}")      # Area: 153.94
```

</details>

**Exercise 6 · Fix the bug.** `age = "25"; print("Next year you'll be " + age + 1)`. Make it print
`Next year you'll be 26`.

<details class="solution"><summary>Solution</summary>

```python
age = "25"
print("Next year you'll be " + str(int(age) + 1))
# or simply: print(f"Next year you'll be {int(age) + 1}")
```

Convert the text to a number to add, then back to text to join.

</details>

**Exercise 7 · Unpack.** Unpack `("Ooty", 2024, "July")` into three variables and print them on one
line separated by ` | `.

<details class="solution"><summary>Solution</summary>

```python
place, year, month = ("Ooty", 2024, "July")
print(place, year, month, sep=" | ")     # Ooty | 2024 | July
```

</details>
