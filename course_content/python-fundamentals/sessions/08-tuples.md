# Session 8 · Tuples: the magic photo album

📖 Based on the blog posts [The Magic Photo Album: Python Tuple](https://learn.parottasalna.com/blog/the-magic-photo-album-python-tuple/)
and [Python Task: Tuple](https://learn.parottasalna.com/blog/python-task-tuple/).

## The big idea

A **tuple** is like a list that's **sealed**: ordered, but it can't be changed after it's created.
Use a tuple for a fixed group of values that belong together: a date, a GPS point, one row of
data.

**Everyday example:** a printed photo. Once it's taken, the place, date and moment are fixed. You
can look at it, copy it and put it in an album, but you can't edit the photo itself.

```{raw} html
:file: ../diagrams/s08-tuple.html
```

## Morning: creating snapshots

Round brackets, or just commas:

```python
ooty = ("Ooty", "2024-07-01", "Visited Botanical Garden")
munnar = ("Munnar", "2023-12-15", "Saw Nilgiri Tahr in Eravikulam national park")
manjolai = ("Manjolai", "2023-05-21", "Enjoyed hill stations")
photo_album = [ooty, munnar, manjolai]      # a list of tuples
print(type(ooty), len(photo_album))
```

```text
<class 'tuple'> 3
```

## Noon and afternoon: reading and unpacking

```python
ooty = ("Ooty", "2024-07-01", "Visited Botanical Garden")
munnar = ("Munnar", "2023-12-15", "Saw Nilgiri Tahr in Eravikulam national park")

print(ooty[0], ooty[-1])                     # indexing works like lists
location, date, description = munnar         # unpacking
print(f"Location: {location}, Date: {date}")
```

```text
Ooty Visited Botanical Garden
Location: Munnar, Date: 2023-12-15
```

## Trying to edit a photo

```python
ooty = ("Ooty", "2024-07-01", "Visited Botanical Garden")
try:
    ooty[2] = "Visited Doddabeta Peak"
except TypeError as e:
    print("TypeError:", e)
```

```text
TypeError: 'tuple' object does not support item assignment
```

To "change" a tuple, build a new one, for example via a list:

```python
ooty = ("Ooty", "2024-07-01", "Visited Botanical Garden")
as_list = list(ooty)
as_list[2] = "Visited Doddabeta Peak"
ooty = tuple(as_list)            # a NEW tuple, bound to the same name
print(ooty)
```

```text
('Ooty', '2024-07-01', 'Visited Doddabeta Peak')
```

## Evening and night: joining, repeating, checking

```python
ooty = ("Ooty", "2024-07-01")
munnar = ("Munnar", "2023-12-15")
album = [ooty, munnar]

print(ooty + munnar)          # concatenate: a new, longer tuple
print(ooty * 2)               # repeat
print(ooty in album)          # membership
print(len(album))
```

```text
('Ooty', '2024-07-01', 'Munnar', '2023-12-15')
('Ooty', '2024-07-01', 'Ooty', '2024-07-01')
True
2
```

## Why use tuples?

- **Safety**: values that must not change can't be changed by accident.
- **Dictionary keys**: tuples can be keys (`{(0, 0): "origin"}`); lists can't.
- **Returning several values** from a function: `return min_v, max_v` returns a tuple.
- **Slightly faster and smaller** than lists.

## Common mistakes

- **One-item tuple without a comma**: `("x")` is just the string `"x"`. Write `("x",)`.

  ```python
  print(type(("x")), type(("x",)))
  ```

  ```text
  <class 'str'> <class 'tuple'>
  ```

- **Unpacking the wrong number**: `a, b = (1, 2, 3)` raises `ValueError: too many values to
  unpack`.
- **"Immutable" doesn't mean "frozen all the way down"**: a tuple holding a list can't swap the
  list for another, but the list inside can still change: `t = (1, [2]); t[1].append(3)` works.

## Hands-on exercises

The 19 tasks from [Python Task: Tuple](https://learn.parottasalna.com/blog/python-task-tuple/).

**Task 1.** Create a tuple of three fruits; print it and its type.

<details class="solution"><summary>Solution</summary>

```python
fruits = ("mango", "banana", "jackfruit")
print(fruits, type(fruits))
```

</details>

**Task 2.** Print the second element of `t = ("apple", "banana", "cherry")`.

<details class="solution"><summary>Solution</summary>

```python
t = ("apple", "banana", "cherry")
print(t[1])     # banana
```

</details>

**Task 3.** Unpack `t = (1, 2, 3)` into `a`, `b`, `c`.

<details class="solution"><summary>Solution</summary>

```python
t = (1, 2, 3)
a, b, c = t
print(a, b, c)
```

</details>

**Task 4.** Concatenate `t1 = (1, 2)` and `t2 = (3, 4)`.

<details class="solution"><summary>Solution</summary>

```python
t1, t2 = (1, 2), (3, 4)
print(t1 + t2)     # (1, 2, 3, 4)
```

</details>

**Task 5.** Repeat `t = ("repeat",)` three times.

<details class="solution"><summary>Solution</summary>

```python
t = ("repeat",)
print(t * 3)       # ('repeat', 'repeat', 'repeat')
```

</details>

**Task 6.** Count the 2s in `t = (1, 2, 3, 2, 2, 4)`.

<details class="solution"><summary>Solution</summary>

```python
t = (1, 2, 3, 2, 2, 4)
print(t.count(2))  # 3
```

</details>

**Task 7.** Find the index of `"c"` in `t = ("a", "b", "c", "d")`.

<details class="solution"><summary>Solution</summary>

```python
t = ("a", "b", "c", "d")
print(t.index("c"))   # 2
```

</details>

**Task 8.** Check whether 5 is in `t = (1, 2, 3, 4)`.

<details class="solution"><summary>Solution</summary>

```python
t = (1, 2, 3, 4)
print(5 in t)      # False
```

</details>

**Task 9.** Print the length of `t = ("one", "two", "three")`.

<details class="solution"><summary>Solution</summary>

```python
t = ("one", "two", "three")
print(len(t))      # 3
```

</details>

**Task 10.** From `t = (0, 1, 2, 3, 4, 5)`, slice out the elements at indexes 2 to 4.

<details class="solution"><summary>Solution</summary>

```python
t = (0, 1, 2, 3, 4, 5)
print(t[2:5])      # (2, 3, 4): stop is excluded, so 5 not 4
```

</details>

**Task 11.** With `points = ((1, 2), (3, 4))`, print the second coordinate of the second point.

<details class="solution"><summary>Solution</summary>

```python
points = ((1, 2), (3, 4))
print(points[1][1])    # 4
```

</details>

**Task 12.** Try to change the first element of `t = (1, 2, 3)`. What happens?

<details class="solution"><summary>Answer</summary>

`t[0] = 10` raises `TypeError: 'tuple' object does not support item assignment`.

</details>

**Task 13.** Convert `[1, 2, 3]` to a tuple, and `(4, 5, 6)` to a list.

<details class="solution"><summary>Solution</summary>

```python
print(tuple([1, 2, 3]))     # (1, 2, 3)
print(list((4, 5, 6)))      # [4, 5, 6]
```

</details>

**Task 14.** Create a one-item tuple containing 5 and check its type.

<details class="solution"><summary>Solution</summary>

```python
t = (5,)
print(type(t))     # <class 'tuple'>   (without the comma it would be int)
```

</details>

**Task 15.** Loop over `("ParottaSalna", "is", "good")` and print each element.

<details class="solution"><summary>Solution</summary>

```python
for word in ("ParottaSalna", "is", "good"):
    print(word)
```

</details>

**Task 16.** Turn `"hello"` into a tuple of characters.

<details class="solution"><summary>Solution</summary>

```python
print(tuple("hello"))      # ('h', 'e', 'l', 'l', 'o')
```

</details>

**Task 17.** Turn `d = {"one": 1, "two": 2}` into a tuple of its items.

<details class="solution"><summary>Solution</summary>

```python
d = {"one": 1, "two": 2}
print(tuple(d.items()))    # (('one', 1), ('two', 2))
```

</details>

**Task 18.** Write a function that returns the sum of a tuple of numbers.

<details class="solution"><summary>Solution</summary>

```python
def tuple_sum(numbers):
    total = 0
    for n in numbers:
        total += n
    return total

print(tuple_sum((10, 20, 30)))    # 60   (or simply sum((10, 20, 30)))
```

</details>

**Task 19.** Use tuples as dictionary keys for points on a grid.

<details class="solution"><summary>Solution</summary>

```python
grid = {(0, 0): "origin", (1, 2): "point A", (3, 1): "point B"}
print(grid[(1, 2)])                 # point A
for (x, y), name in grid.items():
    print(f"{name} is at x={x}, y={y}")
```

This works because tuples are immutable (hashable); `{[0, 0]: "origin"}` would raise `TypeError`.

</details>
