# Session 4 · Operators, conditions and input()

📖 Based on the blog post [Python: Operators, Conditionals and Input()](https://learn.parottasalna.com/blog/python-operators-conditionals-and-input/).

## The big idea

Three tools that make programs useful:

- **Operators** do the work: add, compare, combine.
- **Conditionals** (`if`, `elif`, `else`) let the program **choose** what to do.
- **`input()`** lets the user talk to the program.

**Everyday example:** a traffic signal. It *compares* (is it red?), *decides* (stop or go), and
reacts to *input* (a pedestrian presses the button).

## Arithmetic operators

```python
a, b = 7, 2
print(a + b, a - b, a * b)    # add, subtract, multiply
print(a / b)                  # division always gives a float
print(a // b)                 # floor division: round DOWN to a whole number
print(a % b)                  # modulus: the remainder
print(a ** b)                 # power: 7 squared
```

```text
9 5 14
3.5
3
1
49
```

`%` is more useful than it looks: `n % 2 == 0` means *n is even*; `n % 10` is the last digit.

:::{note}
`//` rounds **down**, not towards zero: `-7 // 2` is `-4`. And computers store decimals in binary,
so `0.1 + 0.2` gives `0.30000000000000004`. Use `round()` when you print money-like values.
:::

## Comparison operators

They always give `True` or `False`:

```python
a, b = 5, 3
print(a == b, a != b)     # equal, not equal
print(a > b, a < b)       # greater, less
print(a >= 5, b <= 2)     # greater-or-equal, less-or-equal
```

```text
False True
True False
True False
```

## Logical operators

Combine conditions with `and`, `or`, `not`:

```python
a, b = 5, 3
print(a > b and a > 0)    # both must be True
print(a < b or a > 0)     # at least one True
print(not a > 0)          # flips True/False
```

```text
True
True
False
```

Python also lets you chain comparisons like in maths: `0 < age < 120`.

## Conditionals: if / elif / else

```{raw} html
:file: ../diagrams/s04-if.html
```

```python
a, b = 3, 5
if a > b:
    print("a is greater than b")
elif a == b:
    print("a is equal to b")
else:
    print("a is less than b")
```

```text
a is less than b
```

- The **indentation** (4 spaces) is what puts a line *inside* the `if`. It isn't decoration.
- Only the **first** matching branch runs, then Python skips the rest.
- You can have any number of `elif`s, and `else` is optional.

## input(): asking the user

`input()` shows a prompt, waits for the user to type and press Enter, and returns **text**:

```python
name = input("What is your name? ")
print("Hello, " + name + "!")
```

To do maths, convert the text to a number first:

```python
age = int(input("How old are you? "))
print(f"Next year you'll be {age + 1}.")
```

## Putting it together

Is a number positive, negative or zero?

```python
number = float(input("Enter a number: "))

if number > 0:
    print("The number is positive.")
elif number < 0:
    print("The number is negative.")
else:
    print("The number is zero.")
```

```text
Enter a number: The number is positive.
```

(When you run it yourself, you type the number after the prompt.)

## Common mistakes

- **`=` instead of `==`** in a condition: `if x = 5:` is a syntax error.
- **Forgetting `int()`**: `input()` returns text, so `input() + 1` raises `TypeError`, and
  `"10" > "9"` is `False` (text compares letter by letter).
- **Missing colon or indentation**: every `if`, `elif`, `else` line ends with `:` and its block is
  indented.
- **Typing "ten"** when `int()` expects digits: `ValueError`. You'll handle this with `try/except`
  in [Session 12](12-project-number-guessing-game.md).

## Hands-on exercises

**Exercise 1 · Even or odd.** Ask for a number and print whether it's even or odd.

<details class="solution"><summary>Solution</summary>

```python
n = int(input("Enter a number: "))
if n % 2 == 0:
    print(f"{n} is even")
else:
    print(f"{n} is odd")
```

</details>

**Exercise 2 · Grade calculator.** Ask for marks (0–100) and print A (90+), B (75–89), C (50–74)
or F.

<details class="solution"><summary>Solution</summary>

```python
marks = int(input("Marks: "))
if marks >= 90:
    grade = "A"
elif marks >= 75:
    grade = "B"
elif marks >= 50:
    grade = "C"
else:
    grade = "F"
print("Grade:", grade)
```

Order matters: check the highest band first, so 95 doesn't stop at `>= 50`.

</details>

**Exercise 3 · Leap year.** A year is a leap year if it's divisible by 4, except centuries, unless
divisible by 400. Check 2024, 1900 and 2000.

<details class="solution"><summary>Solution</summary>

```python
for year in [2024, 1900, 2000]:
    is_leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
    print(year, is_leap)
```

2024 True, 1900 False, 2000 True.

</details>

**Exercise 4 · Biggest of three.** Ask for three numbers and print the largest, using `if` (not
`max()`).

<details class="solution"><summary>Solution</summary>

```python
a = float(input("a: "))
b = float(input("b: "))
c = float(input("c: "))
if a >= b and a >= c:
    largest = a
elif b >= c:
    largest = b
else:
    largest = c
print("Largest:", largest)
```

</details>

**Exercise 5 · Ticket price.** Children under 5 are free, 5–17 pay ₹50, 60 and above pay ₹60,
everyone else ₹100. Ask for the age and print the price.

<details class="solution"><summary>Solution</summary>

```python
age = int(input("Age: "))
if age < 5:
    price = 0
elif age <= 17:
    price = 50
elif age >= 60:
    price = 60
else:
    price = 100
print(f"Ticket: ₹{price}")
```

</details>

**Exercise 6 · Simple calculator.** Ask for two numbers and an operator (`+ - * /`) and print the
result. Print a message instead of crashing when dividing by zero.

<details class="solution"><summary>Solution</summary>

```python
a = float(input("First number: "))
op = input("Operator (+ - * /): ")
b = float(input("Second number: "))

if op == "+":
    print(a + b)
elif op == "-":
    print(a - b)
elif op == "*":
    print(a * b)
elif op == "/":
    if b == 0:
        print("Can't divide by zero")
    else:
        print(a / b)
else:
    print("Unknown operator")
```

</details>
