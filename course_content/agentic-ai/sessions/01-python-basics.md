# Session 1 · Python Basics

## The big idea

A program is a list of instructions the computer follows **from top to bottom**. In this session
you'll learn the first few instructions: show something on screen, remember a value, and repeat
work in a loop.

**Everyday example:** a recipe. "Take 2 eggs" (remember a value), "beat them" (do something), "repeat
for each egg" (a loop), "if the pan is hot, add butter" (a decision).

## 1. Showing output with `print()`

`print()` shows text on the screen. You can give it several things, separated by commas:

```python
print("Hello World")
print("Hello World", "Hi", "How Are You ?")
```

**Output:**

```text
Hello World
Hello World Hi How Are You ?
```

Python puts a space between each item for you.

## 2. Variables: a name tag on a value

A **variable** is a name you stick on a value so you can use it later.

```python
name = "Syed Jafer K"
age = 28
is_machine_on = False
```

Read `=` as **"points to"**, not "equals": *`age` points to 28*.

```{raw} html
:file: ../diagrams/s01-variables.html
```

Python works out the **type** (the kind of value) by itself:

| Value | Type | In simple words |
|---|---|---|
| `"Syed Jafer K"` | `str` (string) | text, always inside quotes |
| `28` | `int` (integer) | a whole number |
| `False` | `bool` (boolean) | yes/no, `True` or `False` |

You can move a name tag to a different value, even a different type:

```python
age = 28
age = "Twenty Eight"     # now age points to text
print(age)               # Twenty Eight
```

:::{note}
**Why this matters later:** Python doesn't stop you from putting the "wrong" kind of value in a
variable. When data comes from an AI model, this can cause surprises. In
[Session 9](09-data-validation.md) you'll learn a tool (Pydantic) that checks types for you.
:::

## 3. Ask a value what it can do: `dir()`

Every value comes with built-in abilities, called **methods**. You don't need to memorise them:
`dir()` lists them.

```python
age = "Twenty Eight"
dir(age)          # [..., 'lower', 'strip', 'swapcase', 'upper', ...]
age.swapcase()    # 'tWENTY eIGHT'   ← upper becomes lower and lower becomes upper
age.upper()       # 'TWENTY EIGHT'
```

## 4. Cleaning text

Text typed by people (or copied from a PDF) often has extra spaces. String methods tidy it up:

```python
name = "   Syed    "
name.strip()    # 'Syed'        removes spaces on both sides
name.lstrip()   # 'Syed    '    removes spaces on the left
name.rstrip()   # '   Syed'     removes spaces on the right
```

These methods give you a **new** string. The original `name` doesn't change unless you write
`name = name.strip()`.

## 5. Loops and decisions: FizzBuzz

**The task:** print the numbers 1 to 20. But:

- if a number divides by 3, print **Fizz** instead
- if it divides by 5, print **Buzz** instead
- if it divides by both 3 and 5, print **FizzBuzz**

Here's the code from class:

```python
total_nums = 20

for itr in range(1, total_nums + 1):
    if itr % 3 == 0:
        print("Fizz")
    elif itr % 5 == 0:
        print("Buzz")
    elif itr % 3 == 0 and itr % 5 == 0:
        print("FizzBuzz")
    else:
        print(itr)
```

Let's read it slowly:

| Code | In simple words |
|---|---|
| `for itr in range(1, 21):` | repeat for itr = 1, 2, 3 … 20. The end number (21) is **not** included. |
| `itr % 3` | the **remainder** after dividing by 3. `9 % 3` is 0, `10 % 3` is 1. |
| `itr % 3 == 0` | "does it divide by 3 exactly?" |
| `if` / `elif` / `else` | check conditions top to bottom; run **only the first** one that's true |

```{raw} html
:file: ../diagrams/s01-fizzbuzz.html
```

:::{warning}
**Spot the bug!** Run the class code and look at 15. It prints `Fizz`, not `FizzBuzz`.

Why? 15 divides by 3, so the **first** `if` is true, and Python skips everything below it. The
FizzBuzz line can never run. The fix is to put the most specific check (3 **and** 5) **first**, as
in the diagram above.
:::

## Try it yourself

1. Fix FizzBuzz so that 15 prints `FizzBuzz`.

   <details class="solution">
   <summary>Answer</summary>

   ```python
   for itr in range(1, 21):
       if itr % 3 == 0 and itr % 5 == 0:   # most specific check first
           print("FizzBuzz")
       elif itr % 3 == 0:
           print("Fizz")
       elif itr % 5 == 0:
           print("Buzz")
       else:
           print(itr)
   ```

   </details>

2. Ask the user for their name, tidy it, and greet them:

   ```python
   name = input("What's your name? ").strip()
   print(f"Hello, {name}!")       # the f before the quotes lets you put variables inside {}
   ```

3. Run `dir(42)` and try one method you haven't seen before.

## Session materials

- {download}`Notebook from class (python_basics.ipynb) <../code/01-python-basics/python_basics.ipynb>`
- {download}`Whiteboard (open at excalidraw.com) <../code/01-python-basics/whiteboard.excalidraw>`
