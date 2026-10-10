# Session 5 · Functions

📖 Based on the blog posts [Python Functions](https://learn.parottasalna.com/blog/python-functions/)
and [Tasks: Python Function](https://learn.parottasalna.com/blog/tasks-python-function/).

## The big idea

A function is a **recipe**: write the steps once, give them a name, and use them again whenever
you need them, with different ingredients each time.

**Everyday example:** you don't reinvent dosa every morning. You follow the same recipe; only the
batter amount changes. Functions give you:

- **Reuse**: write once, use many times.
- **Organisation**: like sections in a recipe book.
- **No repetition**: one "chop vegetables" recipe, used by many dishes.
- **Smaller problems**: a big dinner becomes chutney + tiffin + sweet.

## Before and after

Without a function, the same formula appears three times:

```python
celsius1 = 25
print(f"{celsius1}°C is {(celsius1 * 9/5) + 32}°F")
celsius2 = 30
print(f"{celsius2}°C is {(celsius2 * 9/5) + 32}°F")
```

```text
25°C is 77.0°F
30°C is 86.0°F
```

With a function, the formula lives in one place:

```python
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

for c in [25, 30, 15]:
    print(f"{c}°C is {celsius_to_fahrenheit(c)}°F")
```

```text
25°C is 77.0°F
30°C is 86.0°F
15°C is 59.0°F
```

If the formula ever has a bug, you fix it once.

## Anatomy of a function

```{raw} html
:file: ../diagrams/s05-function.html
```

| Part | Meaning |
|---|---|
| `def` | "I'm defining a function" |
| `celsius_to_fahrenheit` | its name (same rules as variables) |
| `(celsius)` | **parameters**: the inputs it expects |
| indented body | the steps; runs only when called |
| `return` | sends a value back and ends the function |
| `celsius_to_fahrenheit(25)` | a **call**; `25` is the **argument** |

## print vs return

```python
def greet(name):
    print(f"Hello, {name}!")       # shows text, returns None

def add(a, b):
    return a + b                   # gives a value back

greet("Alice")
result = add(5, 3)
print(f"The sum is: {result}")
print(greet("Bob"))
```

```text
Hello, Alice!
The sum is: 8
Hello, Bob!
None
```

`print` is for **people** to read. `return` is for the **program** to keep using the value. A
function without `return` gives back `None`.

## More examples

```python
import math

def is_even(number):
    return number % 2 == 0

def max_of_three(a, b, c):
    largest = a if a > b else b
    return largest if largest > c else c

def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)      # a function can call itself (recursion)

def area_of_circle(radius):
    return math.pi * radius ** 2

print(is_even(4), is_even(7))
print(max_of_three(3, 9, 5))
print(factorial(5))
print(round(area_of_circle(5), 2))
```

```text
True False
9
120
78.54
```

## Default values and keyword arguments

A parameter can have a default, used when the caller leaves it out:

```python
def power(number, exponent=2):
    return number ** exponent

print(power(5))               # exponent defaults to 2
print(power(2, 10))
print(power(exponent=3, number=2))   # keyword arguments: any order
```

```text
25
1024
8
```

## Common mistakes

- **Forgetting the brackets**: `greet` (no `()`) refers to the function, it doesn't call it.
- **Printing instead of returning**: `total = add_and_print(2, 3)` is `None` if the function only
  prints.
- **Code after `return`** never runs.
- **Calling before defining**: Python runs top to bottom, so `def` must come before the first call.
- **Naming a variable `max`**: it hides the built-in `max()` function (the blog's version did this;
  this page uses `largest`).

## Hands-on exercises

The seven tasks from [Tasks: Python Function](https://learn.parottasalna.com/blog/tasks-python-function/).

**Task 1.** Write `greet(name)` that prints a greeting.

<details class="solution"><summary>Solution</summary>

```python
def greet(name):
    print(f"Vanakkam, {name}!")

greet("Priya")
```

</details>

**Task 2.** Write `sum_two(a, b)` that returns the sum.

<details class="solution"><summary>Solution</summary>

```python
def sum_two(a, b):
    return a + b

print(sum_two(10, 20))     # 30
```

</details>

**Task 3.** Write `is_even(n)` that returns `True` for even numbers and `False` for odd ones.

<details class="solution"><summary>Solution</summary>

```python
def is_even(n):
    return n % 2 == 0

print(is_even(10), is_even(7))     # True False
```

`n % 2 == 0` is already `True` or `False`, so there's no need for `if … return True else return False`.

</details>

**Task 4.** Write `find_max(a, b)` that returns the larger number.

<details class="solution"><summary>Solution</summary>

```python
def find_max(a, b):
    if a > b:
        return a
    return b

print(find_max(4, 9))     # 9
```

</details>

**Task 5.** Write `multiplication_table(n)` that prints the table of `n` from 1 to 10.

<details class="solution"><summary>Solution</summary>

```python
def multiplication_table(n):
    for i in range(1, 11):
        print(f"{n} x {i} = {n * i}")

multiplication_table(7)
```

</details>

**Task 6.** Write `celsius_to_fahrenheit(c)` that returns the temperature in Fahrenheit.

<details class="solution"><summary>Solution</summary>

```python
def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32

print(celsius_to_fahrenheit(37))    # 98.6
```

</details>

**Task 7.** Write `power(number, exponent)` where `exponent` defaults to 2.

<details class="solution"><summary>Solution</summary>

```python
def power(number, exponent=2):
    return number ** exponent

print(power(9))       # 81
print(power(2, 5))    # 32
```

</details>

**Bonus · Bill splitter.** Write `split_bill(total, people, tip_percent=10)` that returns how much
each person pays, rounded to 2 decimals.

<details class="solution"><summary>Solution</summary>

```python
def split_bill(total, people, tip_percent=10):
    with_tip = total * (1 + tip_percent / 100)
    return round(with_tip / people, 2)

print(split_bill(1200, 4))         # 330.0
print(split_bill(1200, 4, 0))      # 300.0
```

</details>
