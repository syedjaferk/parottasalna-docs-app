# Session 9 · Dictionaries: Annachi Kadai

📖 Based on the blog post [Task: Annachi Kadai, Python Dictionary](https://learn.parottasalna.com/blog/task-annachi-kadai-python-dictionary/).

## The big idea

A **dictionary** stores **key → value** pairs. Instead of asking "what's in position 2?", you ask
"what's the price of dal?". Lookups by key are instant, even with millions of entries.

**Everyday example:** the annachi kadai (the corner grocery shop). Annachi doesn't search shelf by
shelf; he knows *rice → ₹60, dal → ₹120*. The item name is the key, the price is the value.

```{raw} html
:file: ../diagrams/s09-dict.html
```

## Creating and reading

```python
prices = {"rice": 60, "dal": 120, "oil": 180}
print(prices["dal"])
print(len(prices))
print("oil" in prices, "tea" in prices)     # `in` checks the KEYS
```

```text
120
3
True False
```

Asking for a missing key with `[]` raises `KeyError`. `get()` returns a default instead:

```python
prices = {"rice": 60, "dal": 120}
print(prices.get("tea"))          # None
print(prices.get("tea", 0))       # your default
```

```text
None
0
```

## Adding, updating, removing

```python
prices = {"rice": 60, "dal": 120, "oil": 180}
prices["sugar"] = 45          # new key → added
prices["dal"] = 125           # existing key → updated
del prices["oil"]             # removed
removed = prices.pop("rice")  # removed, and you get the value back
print(prices, removed)
```

```text
{'dal': 125, 'sugar': 45} 60
```

Keys are **unique**: assigning to a key that exists replaces its value. Keys must be immutable
(strings, numbers, tuples); values can be anything, even lists or other dictionaries.

## Looping

```python
prices = {"rice": 60, "dal": 120}
for item, price in prices.items():
    print(f"{item:>5}: ₹{price}")
print(list(prices.keys()), list(prices.values()))
```

```text
 rice: ₹60
  dal: ₹120
['rice', 'dal'] [60, 120]
```

Since Python 3.7, a dictionary remembers the order you inserted keys.

## Counting things: a classic pattern

```python
fruits = ["apple", "banana", "apple", "orange", "banana", "banana"]
count = {}
for fruit in fruits:
    count[fruit] = count.get(fruit, 0) + 1
print(count)
```

```text
{'apple': 2, 'banana': 3, 'orange': 1}
```

## Common mistakes

- **`d["missing"]`** raises `KeyError`. Use `get()` or check `in` first.
- **Lists as keys**: `{[1, 2]: "x"}` raises `TypeError` (unhashable). Use a tuple.
- **Changing size while looping** (`for k in d: del d[k]`) raises `RuntimeError`. Loop over
  `list(d)` instead.
- **`copy()` is shallow**: nested dictionaries inside are still shared. Use `copy.deepcopy()` for
  those.

## Hands-on exercises

The tasks from [Task: Annachi Kadai](https://learn.parottasalna.com/blog/task-annachi-kadai-python-dictionary/).
Each solution sets up what it needs so you can run it alone.

**Task 1.** Create `student` with name "Alice", age 21, major "Computer Science" and print it.

<details class="solution"><summary>Solution</summary>

```python
student = {"name": "Alice", "age": 21, "major": "Computer Science"}
print(student)
```

</details>

**Task 2.** Print the values for `"name"` and `"major"`.

<details class="solution"><summary>Solution</summary>

```python
student = {"name": "Alice", "age": 21, "major": "Computer Science"}
print(student["name"], student["major"])
```

</details>

**Task 3.** Add `"gpa": 3.8`, then update `"age"` to 22.

<details class="solution"><summary>Solution</summary>

```python
student = {"name": "Alice", "age": 21, "major": "Computer Science"}
student["gpa"] = 3.8
student["age"] = 22
print(student)
```

</details>

**Task 4.** Remove `"major"` with `del` and print the dictionary.

<details class="solution"><summary>Solution</summary>

```python
student = {"name": "Alice", "age": 22, "major": "Computer Science"}
del student["major"]
print(student)
```

</details>

**Task 5.** Check whether the key `"age"` exists.

<details class="solution"><summary>Solution</summary>

```python
student = {"name": "Alice", "age": 22}
print("age" in student)      # True
```

</details>

**Task 6.** Create `prices = {"apple": 0.5, "banana": 0.3, "orange": 0.7}` and print each pair.

<details class="solution"><summary>Solution</summary>

```python
prices = {"apple": 0.5, "banana": 0.3, "orange": 0.7}
for fruit, price in prices.items():
    print(fruit, price)
```

</details>

**Task 7.** Print how many pairs `prices` has.

<details class="solution"><summary>Solution</summary>

```python
prices = {"apple": 0.5, "banana": 0.3, "orange": 0.7}
print(len(prices))     # 3
```

</details>

**Task 8.** Use `get()` for `"gpa"`, and for `"graduation_year"` with a default of 2025.

<details class="solution"><summary>Solution</summary>

```python
student = {"name": "Alice", "gpa": 3.8}
print(student.get("gpa"))                     # 3.8
print(student.get("graduation_year", 2025))   # 2025 (key doesn't exist)
```

</details>

**Task 9.** Merge `extra_info = {"graduation_year": 2025, "hometown": "Springfield"}` into
`student` with `update()`.

<details class="solution"><summary>Solution</summary>

```python
student = {"name": "Alice", "gpa": 3.8}
extra_info = {"graduation_year": 2025, "hometown": "Springfield"}
student.update(extra_info)
print(student)
```

</details>

**Task 10.** Use a dictionary comprehension to map 1–5 to their squares.

<details class="solution"><summary>Solution</summary>

```python
squares = {n: n ** 2 for n in range(1, 6)}
print(squares)     # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
```

</details>

**Task 11.** Print the keys and values of `prices` as two separate lists.

<details class="solution"><summary>Solution</summary>

```python
prices = {"apple": 0.5, "banana": 0.3, "orange": 0.7}
print(list(prices.keys()))
print(list(prices.values()))
```

</details>

**Task 12.** Create `school` with two nested students and print the age of `"student2"`.

<details class="solution"><summary>Solution</summary>

```python
school = {
    "student1": {"name": "Alice", "age": 21},
    "student2": {"name": "Bob", "age": 22},
}
print(school["student2"]["age"])     # 22
```

</details>

**Task 13.** Use `setdefault()` to add `"advisor": "Dr. Smith"` only if it's missing.

<details class="solution"><summary>Solution</summary>

```python
student = {"name": "Alice"}
student.setdefault("advisor", "Dr. Smith")
student.setdefault("advisor", "Dr. Jones")     # ignored: the key exists now
print(student)     # {'name': 'Alice', 'advisor': 'Dr. Smith'}
```

</details>

**Task 14.** `pop()` the `"hometown"` key into a variable and print it.

<details class="solution"><summary>Solution</summary>

```python
student = {"name": "Alice", "hometown": "Springfield"}
hometown = student.pop("hometown")
print(hometown, student)
```

</details>

**Task 15.** Empty `prices` with `clear()`.

<details class="solution"><summary>Solution</summary>

```python
prices = {"apple": 0.5, "banana": 0.3}
prices.clear()
print(prices)      # {}
```

</details>

**Task 16.** `copy()` the student, change the copy's name to "Charlie", print both.

<details class="solution"><summary>Solution</summary>

```python
student = {"name": "Alice", "age": 22}
clone = student.copy()
clone["name"] = "Charlie"
print(student)     # {'name': 'Alice', 'age': 22}
print(clone)       # {'name': 'Charlie', 'age': 22}
```

</details>

**Task 17.** Build a dictionary from `keys = ["name", "age", "major"]` and
`values = ["Eve", 20, "Mathematics"]` with `zip()`.

<details class="solution"><summary>Solution</summary>

```python
keys = ["name", "age", "major"]
values = ["Eve", 20, "Mathematics"]
print(dict(zip(keys, values)))
```

</details>

**Task 18.** Loop over `student` with `items()`.

<details class="solution"><summary>Solution</summary>

```python
student = {"name": "Eve", "age": 20}
for key, value in student.items():
    print(f"{key}: {value}")
```

</details>

**Task 19.** Count the fruits in `["apple", "banana", "apple", "orange", "banana", "banana"]`.

<details class="solution"><summary>Solution</summary>

```python
fruits = ["apple", "banana", "apple", "orange", "banana", "banana"]
fruit_count = {}
for fruit in fruits:
    fruit_count[fruit] = fruit_count.get(fruit, 0) + 1
print(fruit_count)     # {'apple': 2, 'banana': 3, 'orange': 1}
```

</details>

**Task 20.** Count words with `collections.defaultdict`.

<details class="solution"><summary>Solution</summary>

```python
from collections import defaultdict

word_count = defaultdict(int)          # missing keys start at int() = 0
for word in ["hello", "world", "hello", "python"]:
    word_count[word] += 1
print(dict(word_count))     # {'hello': 2, 'world': 1, 'python': 1}
```

`collections.Counter(words)` does the same in one line.

</details>
