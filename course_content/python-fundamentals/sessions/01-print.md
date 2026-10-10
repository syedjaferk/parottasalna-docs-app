# Session 1 · The print() function

📖 Based on the blog post [Python Fundamentals: The Print()](https://learn.parottasalna.com/blog/python-fundamentals-the-print/)
and [Task 1: Print exercises](https://learn.parottasalna.com/blog/task-1-python-print-exercises/).

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/zr3skBHzbAI"
  title="Print() Python | ParottaSalna - Part 1" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 [Watch on YouTube](https://www.youtube.com/watch?v=zr3skBHzbAI) (Tamil)

## The big idea

The first thing you learn in any language is how to **show something on the screen**. In Python
that's `print()`. It looks simple, but it has a few tricks that you'll use every day, from greeting
a user to finding bugs.

**Everyday example:** a shop's display board. Whatever the shopkeeper writes on it, customers see.
`print()` is your program's display board.

## Printing text, variables and numbers

Text goes inside quotes, single or double:

```python
print("Hello, world!")
```

```text
Hello, world!
```

Variables and numbers go in without quotes. Python prints their value:

```python
name = "Parotta Salna"
print(name)
print(12345)
print(5 + 3)
```

```text
Parotta Salna
12345
8
```

## Several items at once

Separate items with commas. Python puts a space between them:

```python
name = "Parotta Salna"
age = 25
city = "Chennai"
print("Name:", name, "Age:", age, "City:", city)
```

```text
Name: Parotta Salna Age: 25 City: Chennai
```

```{raw} html
:file: ../diagrams/s01-print.html
```

### `sep` and `end`

`sep` is what goes **between** items (a space by default). `end` is what goes **after** the last
one (a newline by default):

```python
print("Hello", "world", sep="-", end="!\n")
print("Hello", end=" ")
print("world!")
```

```text
Hello-world!
Hello world!
```

## Four ways to mix text and values

```python
name, age, city = "Parotta Salna", 25, "Chennai"

print(f"Name: {name}, Age: {age}, City: {city}")                 # 1. f-string (recommended)
print("Name: {}, Age: {}, City: {}".format(name, age, city))      # 2. .format()
print("Name: " + name + ", City: " + city)                        # 3. + (strings only)
print("Name:", name, "Age:", age)                                 # 4. commas
```

```text
Name: Parotta Salna, Age: 25, City: Chennai
Name: Parotta Salna, Age: 25, City: Chennai
Name: Parotta Salna, City: Chennai
Name: Parotta Salna Age: 25
```

`+` only joins strings. To add a number, convert it with `str()` first:

```python
temperature = 22.5
print("The temperature is " + str(temperature) + " degrees Celsius.")
```

```text
The temperature is 22.5 degrees Celsius.
```

f-strings can also **format** values: `:.2f` keeps two decimals, `:<10` / `:>10` pad to a width.

```python
pi = 3.14159
print(f"The value of pi is approximately {pi:.2f}")
print(f"{'left':<10}|{'right':>10}|")
```

```text
The value of pi is approximately 3.14
left      |     right|
```

## Special characters

| You write | You get |
|---|---|
| `"Line1\nLine2"` | a new line between them (`\n`) |
| `"Name\tAge"` | a tab (`\t`) |
| `'He said, "Hello!"'` | double quotes inside single quotes |
| `r"C:\Users\Name"` | a **raw** string: backslashes printed as they are |
| `"""three\nlines"""` | triple quotes: a string over several lines |

```python
print("Line1\nLine2\nLine3")
print('He said, "Hello, world!"')
print(r"C:\Users\Name")
```

```text
Line1
Line2
Line3
He said, "Hello, world!"
C:\Users\Name
```

## Printing other things

```python
print("Hello " * 3)                                   # repeat a string
print(True, None)                                     # booleans and None
print(["apple", "banana", "cherry"])                  # a list
print({"name": "Alice", "age": 25})                   # a dictionary
for i in range(3):                                    # in a loop
    print("Iteration", i)
```

```text
Hello Hello Hello 
True None
['apple', 'banana', 'cherry']
{'name': 'Alice', 'age': 25}
Iteration 0
Iteration 1
Iteration 2
```

## print() for debugging

When a program gives a wrong answer, print the values in the middle to see where it goes wrong:

```python
def add(a, b):
    print(f"Adding {a} and {b}")      # debug line
    return a + b

result = add(5, 3)
print("Result:", result)
```

```text
Adding 5 and 3
Result: 8
```

Remove the debug prints when you're done.

## Common mistakes

- **`Print("hi")`**: Python is case-sensitive. It's `print`, all lowercase.
- **Forgetting quotes**: `print(Hello)` looks for a *variable* called `Hello` → `NameError`.
- **`"Age: " + 25`**: you can't `+` a string and a number → `TypeError`. Use an f-string or `str(25)`.
- **Windows paths**: in `"C:\new_folder"`, `\n` becomes a new line! Use `r"C:\new_folder"`.

## Hands-on exercises

These are the 17 tasks from [Task 1](https://learn.parottasalna.com/blog/task-1-python-print-exercises/).
Try each one before opening the solution.

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/k6pwbOZtQ30"
  title="Task 1: Python print exercises (solutions)" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

📺 [Solutions video on YouTube](https://www.youtube.com/watch?v=k6pwbOZtQ30) (Tamil)

**Task 1.** Print the string "Hello, world!".

<details class="solution"><summary>Solution</summary>

```python
print("Hello, world!")
```

</details>

**Task 2.** Print the value of a variable `name` set to your name.

<details class="solution"><summary>Solution</summary>

```python
name = "Syed Jafer"
print(name)
```

</details>

**Task 3.** Print `name`, `age` and `city` with the labels "Name:", "Age:" and "City:".

<details class="solution"><summary>Solution</summary>

```python
name, age, city = "Syed Jafer", 25, "Chennai"
print("Name:", name, "Age:", age, "City:", city)
```

</details>

**Task 4.** Use an f-string to print them as "Name: …, Age: …, City: …".

<details class="solution"><summary>Solution</summary>

```python
name, age, city = "Syed Jafer", 25, "Chennai"
print(f"Name: {name}, Age: {age}, City: {city}")
```

</details>

**Task 5.** Join `greeting = "Hello"` and `target = "world"` with a space between and print it.

<details class="solution"><summary>Solution</summary>

```python
greeting, target = "Hello", "world"
print(greeting + " " + target)
```

</details>

**Task 6.** Print "Line1", "Line2" and "Line3" on separate lines, with one `print`.

<details class="solution"><summary>Solution</summary>

```python
print("Line1\nLine2\nLine3")
```

</details>

**Task 7.** Print `He said, "Hello, world!"` including the double quotes.

<details class="solution"><summary>Solution</summary>

```python
print('He said, "Hello, world!"')
# or escape them: print("He said, \"Hello, world!\"")
```

</details>

**Task 8.** Print `C:\Users\Name` without escaping the backslashes.

<details class="solution"><summary>Solution</summary>

```python
print(r"C:\Users\Name")
```

</details>

**Task 9.** Print the result of `5 + 3`.

<details class="solution"><summary>Solution</summary>

```python
print(5 + 3)
```

</details>

**Task 10.** Print "Hello" and "world" separated by a hyphen.

<details class="solution"><summary>Solution</summary>

```python
print("Hello", "world", sep="-")
```

</details>

**Task 11.** Print "Hello" followed by a space, then "world!" on the same line, using two `print`
calls.

<details class="solution"><summary>Solution</summary>

```python
print("Hello", end=" ")
print("world!")
```

</details>

**Task 12.** Print a boolean variable `is_active` set to `True`.

<details class="solution"><summary>Solution</summary>

```python
is_active = True
print(is_active)
```

</details>

**Task 13.** Print "Hello " three times in a row.

<details class="solution"><summary>Solution</summary>

```python
print("Hello " * 3)
```

</details>

**Task 14.** Print `The temperature is 22.5 degrees Celsius.` using a variable `temperature`.

<details class="solution"><summary>Solution</summary>

```python
temperature = 22.5
print(f"The temperature is {temperature} degrees Celsius.")
```

</details>

**Task 15.** Print `name`, `age` and `city` using `.format()`.

<details class="solution"><summary>Solution</summary>

```python
name, age, city = "Syed Jafer", 25, "Chennai"
print("Name: {}, Age: {}, City: {}".format(name, age, city))
```

</details>

**Task 16.** Print pi (3.14159) rounded to two decimals: `The value of pi is approximately 3.14`.

<details class="solution"><summary>Solution</summary>

```python
pi = 3.14159
print(f"The value of pi is approximately {pi:.2f}")
```

</details>

**Task 17.** Print "left" left-aligned and "right" right-aligned, each within 10 characters.

<details class="solution"><summary>Solution</summary>

```python
print(f"{'left':<10}{'right':>10}")
```

Output: `left           right` (each word padded to 10 characters).

</details>
