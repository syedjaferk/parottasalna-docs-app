# Session 10 · Sets: the rose garden and the botanical garden

📖 Based on the blog post [Task: The Botanical Garden and Rose Garden, Python Sets](https://learn.parottasalna.com/blog/task-the-botanical-garden-and-rose-garden-python-sets/).

## The big idea

A **set** is a collection of **unique** items with no order. Adding something that's already there
does nothing. Sets are perfect for removing duplicates, checking membership fast, and comparing
groups: what's common, what's different.

**Everyday example:** two gardens. Which flowers grow in both? Which only in the rose garden? Which
in either? Those are set questions.

```{raw} html
:file: ../diagrams/s10-sets.html
```

## Creating sets

```python
rose_garden = {"red rose", "white rose", "red rose"}     # duplicate is dropped
print(len(rose_garden))
print(set(["rose", "tulip", "rose", "daisy"]) == {"rose", "tulip", "daisy"})
empty = set()            # NOT {} — that's an empty dictionary
print(type(empty), type({}))
```

```text
2
True
<class 'set'> <class 'dict'>
```

A set has **no positions**: `rose_garden[0]` is a `TypeError`. The printed order can vary between
runs, so the examples below use `sorted()` to show results in a fixed order.

## Adding and removing

```python
garden = {"red rose", "white rose"}
garden.add("pink rose")
garden.add("red rose")          # already there: nothing happens
garden.remove("white rose")     # KeyError if missing
garden.discard("blue rose")     # no error if missing
print(sorted(garden))
```

```text
['pink rose', 'red rose']
```

## Comparing gardens

```python
rose = {"red rose", "white rose", "pink rose"}
botanical = {"sunflower", "tulip", "red rose"}

print(sorted(rose | botanical))   # union: in either
print(sorted(rose & botanical))   # intersection: in both
print(sorted(rose - botanical))   # difference: only in rose
print(sorted(rose ^ botanical))   # symmetric difference: in one, not both
```

```text
['pink rose', 'red rose', 'sunflower', 'tulip', 'white rose']
['red rose']
['pink rose', 'white rose']
['pink rose', 'sunflower', 'tulip', 'white rose']
```

Each operator also has a method name: `union()`, `intersection()`, `difference()`,
`symmetric_difference()`.

### Subsets and supersets

```python
small = {"red rose", "white rose"}
rose = {"red rose", "white rose", "pink rose"}
print(small <= rose, small.issubset(rose))       # every small flower is in rose
print(rose >= small, rose.issuperset(small))
```

```text
True True
True True
```

## Why sets are fast

`x in my_list` checks items one by one. `x in my_set` jumps straight to the answer, like a
dictionary key lookup. For big collections that's the difference between seconds and
microseconds.

## frozenset

A set that can't change. Use it when you need a set as a dictionary key, or as a constant.

```python
immutable_garden = frozenset({"orchid", "daisy", "red rose"})
try:
    immutable_garden.add("lily")
except AttributeError as e:
    print("AttributeError:", e)
```

```text
AttributeError: 'frozenset' object has no attribute 'add'
```

## Common mistakes

- **`{}` is an empty dict**, not a set. Use `set()`.
- **Expecting order or indexes.** Sets have neither; convert with `sorted(s)` or `list(s)`.
- **`remove()` vs `discard()`**: `remove` raises `KeyError` for a missing item, `discard` doesn't.
- **Lists inside sets**: `{[1, 2]}` raises `TypeError` (unhashable). Use tuples.

## Hands-on exercises

The tasks from [Task: The Botanical Garden and Rose Garden](https://learn.parottasalna.com/blog/task-the-botanical-garden-and-rose-garden-python-sets/).
After tasks 1–3 the rose garden is `{"red rose", "white rose", "pink rose"}`; the later solutions
start from that.

**Task 1.** Create `rose_garden` with red, white and yellow roses and print it.

<details class="solution"><summary>Solution</summary>

```python
rose_garden = {"red rose", "white rose", "yellow rose"}
print(rose_garden)
```

</details>

**Task 2.** Add "pink rose".

<details class="solution"><summary>Solution</summary>

```python
rose_garden = {"red rose", "white rose", "yellow rose"}
rose_garden.add("pink rose")
print(rose_garden)
```

</details>

**Task 3.** Remove "yellow rose" with `remove()`.

<details class="solution"><summary>Solution</summary>

```python
rose_garden = {"red rose", "white rose", "yellow rose", "pink rose"}
rose_garden.remove("yellow rose")
print(rose_garden)
```

</details>

**Task 4.** Create `botanical_garden = {"sunflower", "tulip", "red rose"}` and print the union.

<details class="solution"><summary>Solution</summary>

```python
rose_garden = {"red rose", "white rose", "pink rose"}
botanical_garden = {"sunflower", "tulip", "red rose"}
print(rose_garden | botanical_garden)
```

</details>

**Task 5.** Print the intersection.

<details class="solution"><summary>Solution</summary>

```python
rose_garden = {"red rose", "white rose", "pink rose"}
botanical_garden = {"sunflower", "tulip", "red rose"}
print(rose_garden & botanical_garden)       # {'red rose'}
```

</details>

**Task 6.** Print what's only in the rose garden.

<details class="solution"><summary>Solution</summary>

```python
rose_garden = {"red rose", "white rose", "pink rose"}
botanical_garden = {"sunflower", "tulip", "red rose"}
print(rose_garden - botanical_garden)       # white rose, pink rose
```

</details>

**Task 7.** Print the symmetric difference.

<details class="solution"><summary>Solution</summary>

```python
rose_garden = {"red rose", "white rose", "pink rose"}
botanical_garden = {"sunflower", "tulip", "red rose"}
print(rose_garden ^ botanical_garden)       # everything except red rose
```

</details>

**Task 8.** Is `small_garden = {"red rose", "white rose"}` a subset of `rose_garden`?

<details class="solution"><summary>Solution</summary>

```python
rose_garden = {"red rose", "white rose", "pink rose"}
small_garden = {"red rose", "white rose"}
print(small_garden.issubset(rose_garden))   # True
```

</details>

**Task 9.** Is `rose_garden` a superset of `small_garden`?

<details class="solution"><summary>Solution</summary>

```python
rose_garden = {"red rose", "white rose", "pink rose"}
small_garden = {"red rose", "white rose"}
print(rose_garden.issuperset(small_garden)) # True
```

</details>

**Task 10.** Print the number of roses.

<details class="solution"><summary>Solution</summary>

```python
rose_garden = {"red rose", "white rose", "pink rose"}
print(len(rose_garden))      # 3
```

</details>

**Task 11.** `discard()` "pink rose", then try to discard "blue rose".

<details class="solution"><summary>Solution</summary>

```python
rose_garden = {"red rose", "white rose", "pink rose"}
rose_garden.discard("pink rose")
rose_garden.discard("blue rose")       # not there: no error, nothing happens
print(rose_garden)
```

</details>

**Task 12.** `clear()` the rose garden.

<details class="solution"><summary>Solution</summary>

```python
rose_garden = {"red rose", "white rose"}
rose_garden.clear()
print(rose_garden)           # set()
```

</details>

**Task 13.** Copy `botanical_garden`, add "lily" to the copy, print both.

<details class="solution"><summary>Solution</summary>

```python
botanical_garden = {"sunflower", "tulip", "red rose"}
garden_copy = botanical_garden.copy()
garden_copy.add("lily")
print(botanical_garden)      # unchanged
print(garden_copy)           # has lily
```

</details>

**Task 14.** Create a frozenset and try to add or remove an element.

<details class="solution"><summary>Answer</summary>

```python
immutable_garden = frozenset({"orchid", "daisy", "red rose"})
print(hasattr(immutable_garden, "add"), hasattr(immutable_garden, "remove"))   # False False
```

Calling `immutable_garden.add("lily")` raises `AttributeError`: a frozenset has no methods that
change it.

</details>

**Task 15.** Loop over `botanical_garden`.

<details class="solution"><summary>Solution</summary>

```python
botanical_garden = {"sunflower", "tulip", "red rose"}
for flower in sorted(botanical_garden):     # sorted() for a predictable order
    print(flower)
```

</details>

**Task 16.** Use a set comprehension for the even numbers from 1 to 10.

<details class="solution"><summary>Solution</summary>

```python
even_numbers = {n for n in range(1, 11) if n % 2 == 0}
print(sorted(even_numbers))    # [2, 4, 6, 8, 10]
```

</details>

**Task 17.** Remove duplicates from `["rose", "tulip", "rose", "daisy", "tulip"]`.

<details class="solution"><summary>Solution</summary>

```python
flowers = ["rose", "tulip", "rose", "daisy", "tulip"]
print(set(flowers))            # {'rose', 'tulip', 'daisy'} in some order
```

</details>

**Task 18.** Is "sunflower" in `botanical_garden`?

<details class="solution"><summary>Solution</summary>

```python
botanical_garden = {"sunflower", "tulip", "red rose"}
print("sunflower" in botanical_garden)     # True
```

</details>

**Task 19.** Keep only the botanical flowers that are also in the rose garden with
`intersection_update()`.

<details class="solution"><summary>Solution</summary>

```python
rose_garden = {"red rose", "white rose", "pink rose"}
botanical_garden = {"sunflower", "tulip", "red rose"}
botanical_garden.intersection_update(rose_garden)
print(botanical_garden)        # {'red rose'}
```

The `_update` methods change the set in place instead of returning a new one.

</details>

**Task 20.** Remove everything in `small_garden` from `botanical_garden` with
`difference_update()`.

<details class="solution"><summary>Solution</summary>

```python
botanical_garden = {"sunflower", "tulip", "red rose"}
small_garden = {"red rose", "white rose"}
botanical_garden.difference_update(small_garden)
print(sorted(botanical_garden))   # ['sunflower', 'tulip']
```

</details>
