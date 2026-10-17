# Session 6 · Prefix Sum

## The big idea

You keep coins in a long row of piggy banks. A friend keeps asking: *"how many coins are there
between box 3 and box 8?"* You could count them every time. Or, **once at the start**, you write on
each box the **total so far**. Now every question is a single subtraction:

> total at box 8 − total just before box 3

You did the slow work once and every question after that is instant. This is the **prefix sum**.

:::{admonition} In plain words
:class: tip
`prefix[i]` = the sum of the first `i` numbers. The sum of any range `[l, r]` is
`prefix[r + 1] − prefix[l]`: **O(1)** per query after an **O(n)** setup.

**Reach for it when:**

- you must answer **many range-sum queries**
- the problem is "count subarrays whose sum is **k**" (prefix sum + hash map)
- you need sums on a **2D grid** (a matrix of prefix sums)
:::

## The picture

```{raw} html
:file: ../diagrams/prefix-sum.html
```

The extra `0` at the front (`prefix[0] = 0`) is important: it makes ranges that start at index 0 work
with the same formula.

## Build and query

```python
def build_prefix(a):
    prefix = [0]
    for x in a:
        prefix.append(prefix[-1] + x)
    return prefix

def range_sum(prefix, l, r):          # inclusive l..r
    return prefix[r + 1] - prefix[l]

a = [3, 1, 4, 1, 5, 9]
p = build_prefix(a)
print(p)
print(range_sum(p, 2, 4))
```

**Output:**

```text
[0, 3, 4, 8, 9, 14, 23]
10
```

## The big trick: subarray sum equals k

*How many subarrays of `a` add up to `k`?* A subarray `a[i..j]` has sum `prefix[j+1] − prefix[i]`.
We need that to equal `k`, i.e. `prefix[i] = prefix[j+1] − k`. So while scanning, for the current
running sum `cur`, ask: **how many earlier prefixes were equal to `cur − k`?** A hash map keeps those counts.

```python
def subarray_sum(a, k):
    seen = {0: 1}               # the empty prefix
    cur = ans = 0
    for x in a:
        cur += x
        ans += seen.get(cur - k, 0)
        seen[cur] = seen.get(cur, 0) + 1
    return ans

print(subarray_sum([1, 2, 3, -3, 3], 3))
```

**Output:**

```text
5
```

The five subarrays with sum 3 are `[1, 2]`, `[3]` (the first one), `[1, 2, 3, -3]`, `[3, -3, 3]` and `[3]` (the last one). Here is the trace:

| x | cur | look for `cur − 3` | found | `seen` after |
|---|---|---|---|---|
| 1 | 1 | −2 | 0 | `{0:1, 1:1}` |
| 2 | 3 | 0 | 1 | `{0:1, 1:1, 3:1}` |
| 3 | 6 | 3 | 1 | `{0:1, 1:1, 3:1, 6:1}` |
| −3 | 3 | 0 | 1 | `{0:1, 1:1, 3:2, 6:1}` |
| 3 | 6 | 3 | 2 | `{0:1, 1:1, 3:2, 6:2}` |

Total: `0 + 1 + 1 + 1 + 2 = 5`.

## Works for any "equals" rule

Replace "sum" with another value you can subtract: the **remainder** when divided by `k`
(*subarray sums divisible by k*), the **count of 1s minus 0s** (*contiguous array*), or the **XOR**
(session 19).

## 2D prefix sum

`P[r][c]` = sum of the rectangle from `(0,0)` to `(r-1,c-1)`. A rectangle sum then needs four values,
by inclusion–exclusion:

```python
def build_2d(m):
    R, C = len(m), len(m[0])
    P = [[0] * (C + 1) for _ in range(R + 1)]
    for r in range(R):
        for c in range(C):
            P[r + 1][c + 1] = m[r][c] + P[r][c + 1] + P[r + 1][c] - P[r][c]
    return P

def rect_sum(P, r1, c1, r2, c2):        # inclusive corners
    return P[r2 + 1][c2 + 1] - P[r1][c2 + 1] - P[r2 + 1][c1] + P[r1][c1]
```

## Common mistakes

:::{warning}
- **Forgetting the starting `0`** in the prefix array or in the hash map (`{0: 1}`).
- **Off by one** between `prefix[r]` and `prefix[r + 1]`.
- **Using a sliding window for "sum = k" with negatives.** Prefix sum + hash map works for negatives; the window does not.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Range Sum Query - Immutable](https://leetcode.com/problems/range-sum-query-immutable/) | Easy | build once, query many |
| [Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) | Medium | prefix + hash map |
| [Contiguous Array](https://leetcode.com/problems/contiguous-array/) | Medium | treat 0 as −1 |
| [Product of Array Except Self](https://leetcode.com/problems/product-of-array-except-self/) | Medium | prefix and suffix products |
| [Subarray Sums Divisible by K](https://leetcode.com/problems/subarray-sums-divisible-by-k/) | Medium | prefix remainders |
| [Range Sum Query 2D - Immutable](https://leetcode.com/problems/range-sum-query-2d-immutable/) | Medium | 2D prefix |

```{raw} html
<p><a class="reference external" href="/prep/practice/#pattern=prefix-sum"><strong>Open the Prefix Sum problems in the tracker →</strong></a></p>
```
