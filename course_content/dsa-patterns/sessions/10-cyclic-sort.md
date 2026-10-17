# Session 10 · Cyclic Sort

## The big idea

Five children wear jerseys numbered **1 to 5**. There are five seats in a row, and **seat 1 is for
jersey 1, seat 2 for jersey 2**, and so on. The children sit in random seats.

You say: "Everyone sitting in a wrong seat, go to **your own seat**!" A child walks to their seat and
**swaps with whoever is sitting there**. That child then also checks their own number and walks to *their*
seat. After a few swaps **everyone is home**. If a jersey is missing, its seat is occupied by someone
else, which shows you **which number is missing**.

:::{admonition} In plain words
:class: tip
If the array holds numbers in the range **1..n** (or 0..n), each number has a **natural index**
(`value − 1`). Put every number at its index by swapping. Then any index holding the wrong value points to a
**missing** or **duplicate** number, in **O(n) time and O(1) space**.

**Reach for it when:**

- the numbers are in a **known small range** (1..n)
- the problem asks for the **missing**, **duplicate** or **first missing positive** number
- you are told **not to use extra space** (no hash set)
:::

## The picture

```{raw} html
:file: ../diagrams/cyclic-sort.html
```

## The core loop

```python
def cyclic_sort(a):
    i = 0
    while i < len(a):
        j = a[i] - 1               # where a[i] belongs
        if a[i] != a[j]:           # not already there
            a[i], a[j] = a[j], a[i]
        else:
            i += 1                 # correct (or a duplicate): move on
    return a

print(cyclic_sort([3, 1, 5, 4, 2]))
```

**Output:**

```text
[1, 2, 3, 4, 5]
```

The loop **does not advance `i` after a swap**: the new value now at `i` also needs checking. Each
swap puts one number into its final seat, so there are at most `n` swaps. The whole thing is **O(n)**.

Why compare `a[i] != a[j]` and not `i != j`? With **duplicates** (`[2, 2]`), `i != j` would swap two
equal numbers forever. Comparing values makes the loop stop.

## Find the missing number

After sorting, the first index `i` where `a[i] != i + 1` shows the missing number `i + 1`. In `[3, 1, 5, 4]` the sorted-in-place array is `[1, 5, 3, 4]`: index 1 holds `5` instead of `2`, so **2 is missing**. (5 does not fit in a 4-slot array, so it stays out of place.)

```python
def find_missing(a):               # values should be 1..n; return the smallest one that is absent
    n = len(a)
    i = 0
    while i < n:
        j = a[i] - 1
        if 0 <= j < n and a[i] != a[j]:
            a[i], a[j] = a[j], a[i]
        else:
            i += 1
    for i in range(n):
        if a[i] != i + 1:
            return i + 1
    return n + 1

print(find_missing([3, 1, 5, 4]))
```

**Output:**

```text
2
```

## All duplicates / all missing numbers

After sorting `[4, 3, 2, 7, 8, 2, 3, 1]`, the array becomes `[1, 2, 3, 4, 3, 2, 7, 8]`.

- Index 4 holds `3` (should be `5`) → **5 is missing**, **3 is a duplicate**.
- Index 5 holds `2` (should be `6`) → **6 is missing**, **2 is a duplicate**.

```python
def find_disappeared(a):
    i = 0
    while i < len(a):
        j = a[i] - 1
        if a[i] != a[j]:
            a[i], a[j] = a[j], a[i]
        else:
            i += 1
    return [i + 1 for i, x in enumerate(a) if x != i + 1]

print(find_disappeared([4, 3, 2, 7, 8, 2, 3, 1]))
```

**Output:**

```text
[5, 6]
```

## First missing positive

Numbers can be negative or huge. Ignore anything outside `1..n` (it cannot be the answer, because the
answer is at most `n + 1`), sort the rest into place, then find the first wrong index. That is the
`find_missing` function above: the guard `0 <= j < n` is what skips out-of-range numbers.

## Common mistakes

:::{warning}
- **Advancing `i` after a swap.** The swapped-in number still needs to be placed.
- **Comparing indexes instead of values** (infinite loop with duplicates).
- **Forgetting the range guard** `0 <= j < n` when the data may contain out-of-range numbers.
- **Using it when the range is not 1..n.** Then use a hash set instead.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Missing Number](https://leetcode.com/problems/missing-number/) | Easy | 0..n |
| [Find All Numbers Disappeared in an Array](https://leetcode.com/problems/find-all-numbers-disappeared-in-an-array/) | Easy | the loop above |
| [Find the Duplicate Number](https://leetcode.com/problems/find-the-duplicate-number/) | Medium | also solvable with fast/slow |
| [Find All Duplicates in an Array](https://leetcode.com/problems/find-all-duplicates-in-an-array/) | Medium | values at wrong indexes |
| [First Missing Positive](https://leetcode.com/problems/first-missing-positive/) | Hard | range guard |

```{raw} html
<p><a class="reference external" href="/prep/#pattern=cyclic-sort"><strong>Open the Cyclic Sort problems in the tracker →</strong></a></p>
```
