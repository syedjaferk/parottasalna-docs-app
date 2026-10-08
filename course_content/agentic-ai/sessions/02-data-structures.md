# Session 2 · Data Structures

## The big idea

One variable holds one value. But real programs juggle **many** values: a list of students, a
user's profile, a set of animals. **Data structures** are containers for groups of values.

**Everyday example:**

- a **shopping list** keeps items in order (a *list*)
- a **contact card** has labelled fields: name, phone, email (a *dictionary*)
- your **date of birth** never changes once written (a *tuple*)
- a **guest list** has each name only once (a *set*)

| Container | Looks like | Keeps order? | Can change? | Duplicates? | Use it for |
|---|---|---|---|---|---|
| List | `[1, 2, 3]` | ✅ | ✅ | ✅ allowed | things in order |
| Dictionary | `{"name": "Ravi"}` | ✅ | ✅ | keys are unique | labelled info about one thing |
| Tuple | `(1, 2, 3)` | ✅ | ❌ | ✅ allowed | fixed groups of values |
| Set | `{1, 2, 3}` | ❌ | ✅ | ❌ never | unique items and comparisons |

## 1. Lists

A list is an ordered row of boxes. Each box has a **position number** called an **index**.

```python
nums = [1, 10, 23, 2, 4, -9, 10]
```

```{raw} html
:file: ../diagrams/s02-list.html
```

```python
nums[0]       # 1     ← counting starts at 0, not 1!
nums[-1]      # 10    ← negative numbers count from the end
len(nums)     # 7     ← how many items
nums[9]       # IndexError: there is no box number 9
```

**Changing a list:**

```python
nums = [3, 1, 2]
nums.append(99)       # add to the end     → [3, 1, 2, 99]
nums.insert(0, -10)   # add at position 0  → [-10, 3, 1, 2, 99]
nums.sort()           # sort small to big  → [-10, 1, 2, 3, 99]
nums.reverse()        # flip the order     → [99, 3, 2, 1, -10]
nums.count(3)         # how many 3s?       → 1
nums.clear()          # empty it           → []
```

:::{warning}
**Common mistake:** `nums = nums.sort()` makes `nums` become `None` (nothing)! `.sort()` changes the
list in place and doesn't hand anything back. Write just `nums.sort()`, or `new_list = sorted(nums)`
if you want to keep the original.
:::

## 2. Dictionaries

A dictionary stores **labelled** information, like a contact card. Each label is a **key** and
each key has a **value**.

```python
profile = {
    "name": "Syed Jafer K",
    "age": 28,
    "marks": {              # a value can be another dictionary!
        "tamil": 95,
        "maths": 45,
        "biology": 75,
    },
}
```

```{raw} html
:file: ../diagrams/s02-dict.html
```

**Reading and changing values:**

```python
profile["name"]                    # 'Syed Jafer K'
profile["marks"]["tamil"]          # 95   ← go one level deeper with another [ ]
profile["marks"]["tamil"] = 85     # change a value
profile["marks"]["social"] = 45    # add a new key
```

**Asking for a key that might not exist:**

```python
profile["address"]              # ❌ KeyError: crashes the program
profile.get("address")          # ✅ None, no crash
profile.get("address", "N/A")   # ✅ 'N/A', your own fallback
```

Use `.get()` whenever a key might be missing. Answers from AI models and websites often have
missing keys.

**Looping through a dictionary:**

```python
for key, value in profile.items():
    print(key, "→", value)
```

**Output:**

```text
name → Syed Jafer K
age → 28
marks → {'tamil': 85, 'maths': 45, 'biology': 75, 'social': 45}
```

### A list of dictionaries: a mini table

```python
students = [
    {"name": "Syed", "marks": {"tamil": 85}},
    {"name": "Parthiban", "marks": {"tamil": 95}},
]

for student in students:
    print(student["name"], student["marks"]["tamil"])
```

**Output:**

```text
Syed 85
Parthiban 95
```

:::{note}
**Why this matters for AI:** a chat with an AI model is exactly this shape: a **list** of
**dictionaries**:

```python
messages = [
    {"role": "system", "content": "You are a helpful tutor."},
    {"role": "user", "content": "What is Python?"},
]
```

You'll send lists like this to a model from [Session 5](05-prompt-engineering.md) onwards.
:::

## 3. Tuples

A tuple is like a list that's **locked**: once made, it can't change.

```python
vowels = ("A", "E", "I", "O", "U")
vowels[0]          # 'A'
vowels[0] = "Z"    # ❌ TypeError: tuples can't be changed
```

Python uses tuples when a function gives back several values at once:

```python
def get_numbers():
    return 1, 2, 3

a, b, c = get_numbers()    # a = 1, b = 2, c = 3
```

## 4. Sets

A set keeps each item **only once**, and it's great at comparing groups.

```python
vandalur_zoo = {"Lion", "Elephant", "Giraffe", "Kangaroo"}
bannerghatta_zoo = {"Giraffe", "Gorilla", "Butterfly", "Lion"}
```

```{raw} html
:file: ../diagrams/s02-venn.html
```

```python
bannerghatta_zoo.intersection(vandalur_zoo)          # {'Lion', 'Giraffe'}  ← in BOTH zoos
bannerghatta_zoo.union(vandalur_zoo)                 # all 6 animals, each once
bannerghatta_zoo.symmetric_difference(vandalur_zoo)  # animals in only ONE zoo

bannerghatta_zoo.add("Tiger")    # added
bannerghatta_zoo.add("Lion")     # already there: nothing happens
"Lion" in bannerghatta_zoo       # True ← very fast check, even with millions of items
```

## Try it yourself

1. With `nums = [5, 3, 8, 3, 1]`, find the biggest number **without** using `max()` or `sort()`.
   (Hint: keep a variable `biggest` and update it in a loop.)
2. Using the `students` list above, print the name of the student with the highest Tamil mark.
3. Some people registered for a workshop and some attended. Who registered but didn't come?

   <details class="solution">
   <summary>Answer to 3</summary>

   ```python
   registered = {"a@x.com", "b@x.com", "c@x.com"}
   attended = {"a@x.com", "c@x.com"}
   print(registered - attended)    # {'b@x.com'}
   ```

   </details>

## Session materials

- {download}`Notebook from class (data_structures.ipynb) <../code/02-data-structures/data_structures.ipynb>`
- {download}`Whiteboard (open at excalidraw.com) <../code/02-data-structures/whiteboard.excalidraw>`
