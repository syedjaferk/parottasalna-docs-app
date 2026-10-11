# Session 1 · Data types, variables and I/O

## The big idea

Almost all data reaches a pipeline as **text**: a line in a CSV file, a field in an API response,
a row from a log. Python doesn't know that `"55000"` is a price until you **convert** it. The first
job of every data engineer is turning raw text into correctly **typed** values, and spotting when
that goes wrong.

**Everyday example:** a delivery slip says *"Qty: 2, Price: 450"*. A person reads numbers; a
computer reads characters. Before you can calculate the bill, someone has to say "these
characters are numbers".

```{raw} html
:file: ../diagrams/s01-typing.html
```

## Variables and the basic types

A variable is a name for a value. Python works out the type from the value:

```python
order_id = 1001             # int: whole numbers
unit_price = 450.0          # float: decimals
city = "Coimbatore"         # str: text
is_delivered = True         # bool: True / False
coupon = None               # NoneType: "no value"

for value in (order_id, unit_price, city, is_delivered, coupon):
    print(repr(value), type(value).__name__)
```

```text
1001 int
450.0 float
'Coimbatore' str
True bool
None NoneType
```

`repr()` shows a value the way Python sees it, quotes included. Use it when debugging: it's the
easiest way to notice that `"1001"` is a string, not a number.

## From a raw line to a typed record

Here is one line exactly as it sits in `orders.csv`:

```python
line = "1002,2025-01-03,C02,Coimbatore,Mouse,Electronics,2,450,delivered"
fields = line.split(",")
print(fields)
print(type(fields[6]), fields[6] * 2)        # text "2" repeated, not doubled!
```

```text
['1002', '2025-01-03', 'C02', 'Coimbatore', 'Mouse', 'Electronics', '2', '450', 'delivered']
<class 'str'> 22
```

Every field is a `str`. Convert the ones you'll calculate with:

```python
line = "1002,2025-01-03,C02,Coimbatore,Mouse,Electronics,2,450,delivered"
fields = line.split(",")

order_id = int(fields[0])
quantity = int(fields[6])
unit_price = float(fields[7])
amount = quantity * unit_price

print(order_id, quantity, unit_price, amount)
print(f"Order {order_id}: {quantity} × ₹{unit_price:,.2f} = ₹{amount:,.2f}")
```

```text
1002 2 450.0 900.0
Order 1002: 2 × ₹450.00 = ₹900.00
```

`:,.2f` in an f-string adds thousands separators and two decimals: the format you want in reports.

## Conversions that bite

Real data is messy. These are the conversions that break pipelines:

```python
print(int("  42 "))              # surrounding spaces are fine
print(float("1e3"))              # scientific notation works
print(int(float("7.0")))         # "7.0" → float first, then int
print(bool("False"))             # any non-empty string is True!
print("" == None, bool(""))      # empty string is not None, but it is falsy
try:
    int("1,200")                 # thousands separator: not a valid int
except ValueError as e:
    print("ValueError:", e)
```

```text
42
1000.0
7
True
False False
ValueError: invalid literal for int() with base 10: '1,200'
```

Two rules to remember:

- **`bool(text)` is almost never what you want.** Compare instead: `text.strip().lower() in {"true", "yes", "1"}`.
- **An empty field is `""`, not `None`.** Decide on purpose what missing values become.

## Cleaning text

String methods return **new** strings (strings can't change in place):

```python
raw_city = "  chennai \n"
city = raw_city.strip().title()
print(repr(raw_city), "→", repr(city))

product = "Desk Lamp"
print(product.lower(), product.upper(), product.replace(" ", "_").lower())
print("C01".startswith("C"), "laptop" in "Gaming Laptop".lower())
print(" | ".join(["Chennai", "Madurai", "Salem"]))
```

```text
'  chennai \n' → 'Chennai'
desk lamp DESK LAMP desk_lamp
True True
Chennai | Madurai | Salem
```

## Dates are text too

Dates arrive as text. Turn them into `date` objects to compare or subtract them:

```python
from datetime import date

order_day = date.fromisoformat("2025-01-03")      # ISO format: YYYY-MM-DD
signup_day = date.fromisoformat("2024-11-02")
print(order_day.year, order_day.strftime("%d %b %Y"))
print((order_day - signup_day).days, "days after signup")
```

```text
2025 03 Jan 2025
62 days after signup
```

## Output: print, and where it goes

`print()` writes to **standard output** (stdout). Messages about problems should go to **standard
error** (stderr), so that a pipeline's real output stays clean:

```python
import sys

print("order_id,amount")                          # data → stdout
print("1002,900.0")
print("warning: 1 row skipped", file=sys.stderr)  # diagnostics → stderr
```

When you run `python script.py > out.csv`, only stdout goes into the file; the warning still shows
on screen. (From Session 4 on, we use `logging` instead of printing to stderr.)

## Input: from the user, and from the command line

`input()` reads what a person types; it always returns a `str`:

```py
city = input("Which city? ")
print(f"Filtering orders for {city.strip().title()}")
```

Running it and typing `  chennai`:

```text
Which city?   chennai
Filtering orders for Chennai
```

Pipelines run unattended, so they usually take **command-line arguments** instead. `sys.argv`
holds them: `python report.py Chennai 2025-01` gives `["report.py", "Chennai", "2025-01"]`.

```py
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python report.py CITY YYYY-MM")
city, month = sys.argv[1], sys.argv[2]
print(f"Report for {city}, {month}")
```

For anything bigger, the standard `argparse` module gives you `--help`, defaults and type
checking for free.

## Common mistakes

- **Doing maths on strings.** `"2" * 2` is `"22"`, and `"10" > "9"` is `False` (text compares letter
  by letter). Convert first.
- **`int("12.5")`** fails. Use `int(float("12.5"))` only if dropping the decimals is really what you
  want.
- **Floats for money.** `0.1 + 0.2` is `0.30000000000000004`. For exact money maths use
  `decimal.Decimal("0.1")`, or store paise as integers.
- **Forgetting `.strip()`.** `"Chennai " != "Chennai"`: trailing spaces quietly break joins and filters.

## Hands-on exercises

**Exercise 1 · Type check.** Print the type of each value: `"1001"`, `1001`, `"1001.5"`, `1001.5`,
`"True"`, `True`, `""`, `None`.

<details class="solution"><summary>Solution</summary>

```python
for value in ["1001", 1001, "1001.5", 1001.5, "True", True, "", None]:
    print(repr(value), type(value).__name__)
```

Only the unquoted ones are numbers, booleans or `None`; everything in quotes is `str`.

</details>

**Exercise 2 · Parse an order.** Take
`"1011,2025-02-03,C05,Chennai,Monitor,Electronics,1,9500,delivered"` and print
`Order 1011 | Monitor | ₹9,500.00`.

<details class="solution"><summary>Solution</summary>

```python
line = "1011,2025-02-03,C05,Chennai,Monitor,Electronics,1,9500,delivered"
f = line.split(",")
amount = int(f[6]) * float(f[7])
print(f"Order {f[0]} | {f[4]} | ₹{amount:,.2f}")
```

</details>

**Exercise 3 · A safe yes/no.** Write `to_bool(text)` that returns `True` for "yes", "Y", "true",
"1" (any case, with spaces) and `False` for anything else.

<details class="solution"><summary>Solution</summary>

```python
def to_bool(text):
    return text.strip().lower() in {"yes", "y", "true", "1"}

for t in ["Yes", " TRUE ", "1", "no", "False", ""]:
    print(repr(t), to_bool(t))
```

</details>

**Exercise 4 · Clean a messy amount.** Convert `" ₹1,200.50 "` to the float `1200.5`.

<details class="solution"><summary>Solution</summary>

```python
raw = " ₹1,200.50 "
amount = float(raw.strip().replace("₹", "").replace(",", ""))
print(amount)      # 1200.5
```

</details>

**Exercise 5 · Days between dates.** How many days passed between the first order
(`2025-01-03`) and the last (`2025-02-05`)?

<details class="solution"><summary>Solution</summary>

```python
from datetime import date

print((date.fromisoformat("2025-02-05") - date.fromisoformat("2025-01-03")).days)   # 33
```

</details>

**Exercise 6 · Command-line greeting.** Write `hello.py` that prints `Hello, NAME!` using the first
command-line argument, and a usage message (exit code 1) when it's missing.

<details class="solution"><summary>Solution</summary>

```py
import sys

if len(sys.argv) < 2:
    sys.exit("usage: python hello.py NAME")     # prints to stderr, exit code 1
print(f"Hello, {sys.argv[1]}!")
```

Run `python hello.py Priya`, then `python hello.py; echo $?` to see the exit code.

</details>
