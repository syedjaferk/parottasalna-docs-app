# Session 7 · Lists: the delivery man's busy day

📖 Based on the blog posts [Python List: The Delivery Man's Busy Day](https://learn.parottasalna.com/blog/python-list-the-delivery-mans-busy-day/)
and [Task: The Delivery Man](https://learn.parottasalna.com/blog/task-the-delivery-man-python-list/).

## The big idea

A **list** is an ordered row of items that you can **change**: add, remove, sort, reorder. It's
Python's most used collection.

**Everyday example:** meet Alex, a delivery man. His truck has a row of bins, and each bin holds a
package. Let's follow his day.

```{raw} html
:file: ../diagrams/s07-list.html
```

## Morning: loading the truck

```python
packages = ["Letter", "Box", "Parcel"]
print(packages, len(packages))
```

```text
['Letter', 'Box', 'Parcel'] 3
```

Square brackets, items separated by commas. A list can hold anything, even mixed types:
`[1, "two", 3.0, True]`.

## Through the day

```python
packages = ["Letter", "Box", "Parcel"]

item = packages[1]                         # a customer needs the Box (index 1)
print("Deliver:", item)

packages.append("Special Delivery")        # new package at the end
packages.insert(2, "Fragile Box")          # squeeze one in at index 2
print(packages)

packages.remove("Box")                     # loaded by mistake: remove by value
print(packages)

last_package = packages.pop()              # take the last one off, and get it back
print("Took off:", last_package)
print(packages)

print("Parcel is in bin", packages.index("Parcel"))
print(packages[0:3])                       # a slice, like Session 6
```

```text
Deliver: Box
['Letter', 'Box', 'Fragile Box', 'Parcel', 'Special Delivery']
['Letter', 'Fragile Box', 'Parcel', 'Special Delivery']
Took off: Special Delivery
['Letter', 'Fragile Box', 'Parcel']
Parcel is in bin 2
['Letter', 'Fragile Box', 'Parcel']
```

## Evening: organising

```python
packages = ["Letter", "Fragile Box", "Parcel"]
packages.sort()            # alphabetical, changes the list in place
print(packages)
packages.reverse()         # reverse order, in place
print(packages)
```

```text
['Fragile Box', 'Letter', 'Parcel']
['Parcel', 'Letter', 'Fragile Box']
```

:::{warning}
`sort()` and `reverse()` change the list and return **`None`**. `packages = packages.sort()` loses
your list! Use `sorted(packages)` when you want a new sorted list and to keep the original.
:::

## Cheat sheet

| What | How |
|---|---|
| add at the end / at a position | `append(x)` / `insert(i, x)` |
| add many | `extend(other_list)` or `+` |
| remove by value / by position | `remove(x)` / `pop(i)` or `del lst[i]` |
| find / count | `index(x)` / `count(x)` |
| is it there? | `x in lst` |
| change an item | `lst[i] = new` |
| length | `len(lst)` |
| sort / reverse | `sort()` / `reverse()` (in place) or `sorted()` / `lst[::-1]` (new list) |
| empty it | `clear()` |
| loop | `for item in lst:` |

## List comprehensions

A short way to build a new list from another one:

```python
items = ["Notebook", "Pencil", "Eraser"]
upper = [item.upper() for item in items]
short = [item for item in items if len(item) <= 6]
print(upper)
print(short)
```

```text
['NOTEBOOK', 'PENCIL', 'ERASER']
['Pencil', 'Eraser']
```

Read it as *"`item.upper()` for each `item` in `items`"*, optionally *"if …"*.

## Common mistakes

- **`lst = lst.sort()`**: makes `lst` `None` (see the warning above).
- **`remove()` a missing item**: `ValueError`. Check `if x in lst:` first.
- **Changing a list while looping over it**: items get skipped. Loop over a copy (`for x in lst[:]`)
  or build a new list with a comprehension.
- **`b = a` to copy**: both names share one list ([Session 3](03-variables-are-references.md)).

## Hands-on exercises

The 19 tasks from [Task: The Delivery Man](https://learn.parottasalna.com/blog/task-the-delivery-man-python-list/).
Each solution starts from the same list so you can run it on its own.

**Task 1.** Create a list of five delivery items and print the third.

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Pencil", "Eraser", "Ruler", "Marker"]
print(items[2])        # Eraser
```

</details>

**Task 2.** Add "Glue Stick" to the end and print the list.

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Pencil", "Eraser", "Ruler", "Marker"]
items.append("Glue Stick")
print(items)
```

</details>

**Task 3.** Insert "Highlighter" between the second and third items.

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Pencil", "Eraser", "Ruler", "Marker"]
items.insert(2, "Highlighter")
print(items)    # ['Notebook', 'Pencil', 'Highlighter', 'Eraser', 'Ruler', 'Marker']
```

</details>

**Task 4.** A delivery was cancelled: remove "Ruler".

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Pencil", "Eraser", "Ruler", "Marker"]
items.remove("Ruler")
print(items)
```

</details>

**Task 5.** Print only the first three items.

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Pencil", "Eraser", "Ruler", "Marker"]
print(items[:3])
```

</details>

**Task 6.** Make an uppercase copy with a list comprehension.

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Pencil", "Eraser", "Ruler", "Marker"]
print([item.upper() for item in items])
```

</details>

**Task 7.** Check whether "Marker" is in the list and print a message.

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Pencil", "Eraser", "Ruler", "Marker"]
if "Marker" in items:
    print("Marker is still to be delivered")
else:
    print("Marker is not in the list")
```

</details>

**Task 8.** Print the number of items.

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Pencil", "Eraser", "Ruler", "Marker"]
print(len(items))      # 5
```

</details>

**Task 9.** Sort the list alphabetically.

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Pencil", "Eraser", "Ruler", "Marker"]
items.sort()
print(items)    # ['Eraser', 'Marker', 'Notebook', 'Pencil', 'Ruler']
```

</details>

**Task 10.** Reverse the order of deliveries.

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Pencil", "Eraser", "Ruler", "Marker"]
items.reverse()
print(items)
```

</details>

**Task 11.** Make a list where each element is `[item, delivery_time]`. Print the first item and its
time.

<details class="solution"><summary>Solution</summary>

```python
schedule = [["Notebook", "09:00"], ["Pencil", "10:30"], ["Eraser", "12:15"]]
item, time = schedule[0]
print(f"{item} at {time}")      # Notebook at 09:00
```

</details>

**Task 12.** Count how many times "Ruler" appears.

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Ruler", "Pencil", "Ruler"]
print(items.count("Ruler"))     # 2
```

</details>

**Task 13.** Find the index of "Pencil".

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Pencil", "Eraser", "Ruler", "Marker"]
print(items.index("Pencil"))    # 1
```

</details>

**Task 14.** Extend the list with another list of new items.

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Pencil"]
items.extend(["Stapler", "Sharpener"])
print(items)
```

`append(["Stapler", "Sharpener"])` would add **one** item: a list inside the list.

</details>

**Task 15.** Clear the list.

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Pencil", "Eraser", "Ruler", "Marker"]
items.clear()
print(items)    # []
```

</details>

**Task 16.** Make a list with "Notebook" repeated three times.

<details class="solution"><summary>Solution</summary>

```python
print(["Notebook"] * 3)
```

</details>

**Task 17.** With a comprehension, build `[item, length]` pairs.

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Pencil", "Eraser", "Ruler", "Marker"]
print([[item, len(item)] for item in items])
```

</details>

**Task 18.** Keep only items that contain the letter "e".

<details class="solution"><summary>Solution</summary>

```python
items = ["Notebook", "Pencil", "Eraser", "Ruler", "Marker", "Glue Stick", "Map"]
print([item for item in items if "e" in item])
```

The first five all contain a lowercase "e" (check Eraser: E-r-a-s-**e**-r); "Map" is filtered out.
`"e" in item` is case-sensitive.

</details>

**Task 19.** Remove duplicates.

<details class="solution"><summary>Solution</summary>

```python
items = ["Pencil", "Ruler", "Pencil", "Marker", "Ruler"]
unique = list(dict.fromkeys(items))     # keeps the original order
print(unique)                           # ['Pencil', 'Ruler', 'Marker']
```

`list(set(items))` also removes duplicates, but loses the order ([Session 10](10-sets.md)).

</details>
