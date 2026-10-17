# Session 5 · Binary Search

## The big idea

I think of a number between 1 and 100. You guess **50**. I say "higher". Now you know the number is in
51–100, so you guess **75**. I say "lower". You guess **62**… Each guess **throws away half** of the
possibilities. Even for a million numbers you need only about **20 guesses**.

That is binary search. The magic is not about arrays: it works any time you can answer a **yes/no
question** that flips from "no" to "yes" exactly once as you go along.

:::{admonition} In plain words
:class: tip
Keep a range `[lo, hi]` where the answer must live. Look at the **middle**. The middle tells you
which half cannot contain the answer. Throw that half away. Repeat.

**Reach for it when:**

- the data is **sorted** or **rotated sorted**
- the problem says "find the **minimum** X such that …" or "the **largest** X that still works" (search on the *answer*)
- you see `O(log n)` in the hints, or n up to 10⁹ and more
:::

## The picture

```{raw} html
:file: ../diagrams/binary-search.html
```

## Step by step

Find `23` in `[2, 5, 8, 12, 16, 23, 38, 56, 72, 91]`.

| step | lo | hi | mid | `a[mid]` | decision |
|---|---|---|---|---|---|
| 1 | 0 | 9 | 4 | 16 | 16 < 23 → `lo = mid + 1` |
| 2 | 5 | 9 | 7 | 56 | 56 > 23 → `hi = mid - 1` |
| 3 | 5 | 6 | 5 | 23 | **found** |

## The classic template

```python
def binary_search(a, target):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target:
            return mid
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

print(binary_search([2, 5, 8, 12, 16, 23, 38, 56, 72, 91], 23))
```

**Output:**

```text
5
```

## The most useful template: "first position where it becomes true"

Most interview problems are really: *"what is the smallest `x` where `check(x)` is true?"* The checks
look like `no no no no yes yes yes`. Find the first `yes`.

```python
def first_true(lo, hi, check):
    """Smallest x in [lo, hi] with check(x) True. hi must be a valid answer."""
    while lo < hi:
        mid = (lo + hi) // 2
        if check(mid):
            hi = mid          # mid might be the answer, keep it
        else:
            lo = mid + 1      # mid is too small, drop it
    return lo
```

Use this one by default. It never skips the answer and it always ends when `lo == hi`.

## Searching on the answer

*Koko eats bananas.* There are piles `[3, 6, 7, 11]` and `h = 8` hours. What is the **slowest speed**
`k` (bananas per hour) that still finishes in time?

We cannot index into "speeds", but `check(k)` = "can she finish at speed `k`?" is monotonic: if
speed 4 works, so does speed 5.

```python
import math

def min_speed(piles, h):
    can_finish = lambda k: sum(math.ceil(p / k) for p in piles) <= h
    return first_true(1, max(piles), can_finish)

print(min_speed([3, 6, 7, 11], 8))
```

**Output:**

```text
4
```

The same idea solves "ship packages in D days", "split array largest sum" and "minimum days to make
bouquets".

## Rotated sorted array

`[4, 5, 6, 7, 0, 1, 2]` is a sorted array that was cut and swapped. **One half is always sorted.**
Find which half, check whether the target lies in it, then keep that half or drop it.

```python
def search_rotated(a, target):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target:
            return mid
        if a[lo] <= a[mid]:                       # left half is sorted
            if a[lo] <= target < a[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                     # right half is sorted
            if a[mid] < target <= a[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1

print(search_rotated([4, 5, 6, 7, 0, 1, 2], 0))
```

**Output:**

```text
4
```

## Common mistakes

:::{warning}
- **Infinite loop:** writing `lo = mid` (instead of `mid + 1`) with `lo <= hi`.
- **Mixing the two styles:** `while lo <= hi` goes with `hi = mid - 1`; `while lo < hi` goes with `hi = mid`.
- **Overflow** in other languages: use `lo + (hi - lo) // 2`. Python does not overflow, but interviewers like to hear it.
- **Forgetting that the check must be monotonic.** If it flips back and forth, binary search is invalid.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Binary Search](https://leetcode.com/problems/binary-search/) | Easy | the template |
| [First Bad Version](https://leetcode.com/problems/first-bad-version/) | Easy | `first_true` |
| [Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/) | Medium | one half is sorted |
| [Find Minimum in Rotated Sorted Array](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/) | Medium | compare with `a[hi]` |
| [Koko Eating Bananas](https://leetcode.com/problems/koko-eating-bananas/) | Medium | search on the answer |
| [Median of Two Sorted Arrays](https://leetcode.com/problems/median-of-two-sorted-arrays/) | Hard | binary search on the partition |

```{raw} html
<p><a class="reference external" href="/prep/#pattern=modified-binary-search"><strong>Open the Modified Binary Search problems in the tracker →</strong></a></p>
```
