# Session 1 · Two Pointers

## The big idea

Imagine a long line of children sorted from the shortest to the tallest. You want to find **two
children whose heights add up to exactly 10**. You could test every pair, but that is slow: with 100
children there are almost 5,000 pairs.

A smarter way: you stand at the **short end**, and a friend stands at the **tall end**. Add your two
heights.

- If the sum is **too small**, you step towards the tall end (a taller partner for you).
- If the sum is **too big**, your friend steps towards the short end.
- If it is **just right**, you are done.

You never look at a pair twice, and you never go backwards. That is the **two pointers** pattern.

:::{admonition} In plain words
:class: tip
Use **two index variables** that move through the data instead of one. Each step, the data tells you
*which* pointer to move, so every element is touched only a few times.

**Reach for it when:**

- the array or string is **sorted** (or you can sort it)
- you need a **pair, triplet or sub-part** that meets a condition
- the problem says "in place", "without extra space", "palindrome" or "remove duplicates"
:::

## The picture

```{raw} html
:file: ../diagrams/two-pointers.html
```

Why does moving only one pointer work? The array is sorted. When `1 + 11` is too big, **11 can never
be part of any answer with a number to the right of 1**, because everything right of 1 is bigger and
would make the sum even larger. So we can throw 11 away safely, and the problem shrinks by one every step.

## Step by step

Find two numbers in `[1, 3, 4, 6, 8, 11]` that add up to `10`.

| step | L | R | `a[L]` | `a[R]` | sum | decision |
|---|---|---|---|---|---|---|
| 1 | 0 | 5 | 1 | 11 | 12 | too big → `R -= 1` |
| 2 | 0 | 4 | 1 | 8 | 9 | too small → `L += 1` |
| 3 | 1 | 4 | 3 | 8 | 11 | too big → `R -= 1` |
| 4 | 1 | 3 | 3 | 6 | 9 | too small → `L += 1` |
| 5 | 2 | 3 | 4 | 6 | 10 | **found** |

Five steps for six numbers. Each step removed at least one candidate.

## The template

```python
def two_sum_sorted(a, target):
    left, right = 0, len(a) - 1
    while left < right:
        total = a[left] + a[right]
        if total == target:
            return [left, right]
        if total < target:
            left += 1       # need a bigger sum
        else:
            right -= 1      # need a smaller sum
    return []
```

**Output for `([1, 3, 4, 6, 8, 11], 10)`:**

```text
[2, 3]
```

Complexity: **time O(n)** (each pointer only moves one way), **space O(1)**.

## Three flavours of the pattern

1. **Opposite ends** (above): pair sums, palindromes, container with most water.
2. **Same direction, slow and fast writer**: remove duplicates in place. One pointer *reads* every
   element; the other marks where the next kept element is *written*.
3. **Sort first, then fix one element**: 3Sum. For every `i`, run the opposite-ends scan on the rest.

```python
def remove_duplicates(a):          # a is sorted
    write = 1
    for read in range(1, len(a)):
        if a[read] != a[read - 1]:
            a[write] = a[read]
            write += 1
    return write                    # new length

nums = [1, 1, 2, 2, 3]
print(remove_duplicates(nums), nums[:3])
```

**Output:**

```text
3 [1, 2, 3]
```

## Worked example: 3Sum

*Find all unique triplets that add up to 0.* Sort, then for each `i` look for two numbers on its right
that sum to `-a[i]`.

```python
def three_sum(a):
    a.sort()
    out = []
    for i in range(len(a) - 2):
        if i and a[i] == a[i - 1]:
            continue                       # skip duplicate first numbers
        l, r = i + 1, len(a) - 1
        while l < r:
            s = a[i] + a[l] + a[r]
            if s == 0:
                out.append([a[i], a[l], a[r]])
                l += 1
                while l < r and a[l] == a[l - 1]:
                    l += 1                 # skip duplicate second numbers
            elif s < 0:
                l += 1
            else:
                r -= 1
    return out

print(three_sum([-1, 0, 1, 2, -1, -4]))
```

**Output:**

```text
[[-1, -1, 2], [-1, 0, 1]]
```

Time **O(n²)** (n starting points × an O(n) scan), space O(1) apart from the answer.

## Common mistakes

:::{warning}
- **Forgetting to sort.** The "move the smaller side" logic only works on sorted data.
- **`left <= right` instead of `left < right`.** With `<=` a number can pair with itself.
- **Not skipping duplicates** in 3Sum, which gives repeated triplets.
- **Using it on unsorted data where you must keep the original indexes.** Sorting destroys them; use a hash map (session 7) instead.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Two Sum II – Input Array Is Sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) | Medium | the textbook version |
| [Valid Palindrome](https://leetcode.com/problems/valid-palindrome/) | Easy | pointers from both ends, skip symbols |
| [Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) | Easy | read/write pointers |
| [Container With Most Water](https://leetcode.com/problems/container-with-most-water/) | Medium | move the shorter wall |
| [3Sum](https://leetcode.com/problems/3sum/) | Medium | sort + fix one + two pointers |
| [Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/) | Hard | track left max and right max |

```{raw} html
<p><a class="reference external" href="/prep/practice/#pattern=two-pointers"><strong>Open the Two Pointers problems in the tracker →</strong></a></p>
```
