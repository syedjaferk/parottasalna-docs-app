# Session 18 · Dynamic Programming

## The big idea

You are climbing a staircase and you can take **1 or 2 steps at a time**. How many different ways are there
to reach step 5? You ask a smaller question: *"How many ways to reach the step just below me, and the
step two below me?"* Then you **add** those two answers.

Notice the trick: you ask the **same small questions again and again** ("ways to reach step 3"). A
clever child writes each answer on a **sticky note** the first time and just **reads the note** the next time.

**Dynamic programming (DP) = a big problem built from smaller problems + sticky notes (a table or cache).**

:::{admonition} In plain words
:class: tip
Every DP solution is the same four decisions:

1. **State**: what does `dp[i]` mean, in plain words?
2. **Transition**: how is `dp[i]` computed from smaller states?
3. **Base case**: the smallest answers you know without thinking.
4. **Order / answer**: fill from small to large; which cell holds the final answer?

**Reach for it when:**

- "**count the ways**", "**minimum cost**", "**maximum profit**", "can we make exactly X?"
- the choices at each step **overlap** (the same sub-problem comes up again)
- greedy fails and brute force is exponential
:::

## The picture: why a cache helps

```{raw} html
:file: ../diagrams/dp-fib.html
```

Plain recursion for `fib(5)` computes `fib(3)` twice and `fib(2)` three times. For `fib(40)` it makes
hundreds of millions of calls. With a cache each value is computed **once**.

## Two ways to write the same thing

**Top-down (memoisation)**: write the recursion, then add a cache.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def ways(n):
    if n <= 1:
        return 1                    # base case: one way to stand at step 0 or 1
    return ways(n - 1) + ways(n - 2)

print(ways(5), ways(40))
```

**Output:**

```text
8 165580141
```

**Bottom-up (tabulation)**: fill a table from the base cases up. No recursion, easy to optimise memory.

```python
def ways_table(n):
    dp = [1] * (n + 1)              # dp[i] = ways to reach step i
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

print(ways_table(5))
```

**Output:**

```text
8
```

Since `dp[i]` only needs the previous two values, you can keep two variables and use **O(1)** space.

## Pattern 1 · 1D: House robber

You cannot rob two adjacent houses. Maximise the money.

- **State:** `dp[i]` = best money using houses `0..i`.
- **Transition:** either skip house `i` (`dp[i-1]`) or rob it (`dp[i-2] + nums[i]`).

```python
def rob(nums):
    prev2 = prev1 = 0
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1

print(rob([2, 7, 9, 3, 1]))
```

**Output:**

```text
12
```

## Pattern 2 · Coin change (minimum coins)

- **State:** `dp[a]` = fewest coins to make amount `a`.
- **Transition:** `dp[a] = 1 + min(dp[a - c])` over every coin `c ≤ a`.
- **Base:** `dp[0] = 0`.

```python
def coin_change(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else -1

print(coin_change([1, 3, 4], 6), coin_change([2], 3))
```

**Output:**

```text
2 -1
```

(Greedy would have said 3 coins for amount 6. DP finds `3 + 3`.)

## Pattern 3 · 2D grid: unique paths

```{raw} html
:file: ../diagrams/dp-grid.html
```

Each cell is reached from above or from the left, so `dp[r][c] = dp[r-1][c] + dp[r][c-1]`.

```python
def unique_paths(rows, cols):
    dp = [[1] * cols for _ in range(rows)]        # first row and column are all 1
    for r in range(1, rows):
        for c in range(1, cols):
            dp[r][c] = dp[r - 1][c] + dp[r][c - 1]
    return dp[-1][-1]

print(unique_paths(3, 4))
```

**Output:**

```text
10
```

## Pattern 4 · Two strings: longest common subsequence

`dp[i][j]` = LCS length of the first `i` letters of `a` and the first `j` letters of `b`.

- If `a[i-1] == b[j-1]`: they extend a match → `dp[i-1][j-1] + 1`.
- Otherwise: drop one letter from either side → `max(dp[i-1][j], dp[i][j-1])`.

```python
def lcs(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]

print(lcs("abcde", "ace"))
```

**Output:**

```text
3
```

Edit distance, longest palindromic subsequence and "interleaving strings" all use the same grid.

## Pattern 5 · Knapsack (choose or skip)

Items with weight and value, capacity `W`. For each item, **skip it** or **take it**.

```python
def knapsack(weights, values, W):
    dp = [0] * (W + 1)                       # dp[w] = best value with capacity w
    for wt, val in zip(weights, values):
        for w in range(W, wt - 1, -1):       # backwards, so each item is used once
            dp[w] = max(dp[w], dp[w - wt] + val)
    return dp[W]

print(knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7))
```

**Output:**

```text
9
```

Looping `w` **forwards** instead would allow an item to be reused (unbounded knapsack = coin change).

## How to find the DP

1. Write a **brute-force recursion** (what choices do I have at this step?).
2. Find the **parameters** that change: those are your state. Keep it small.
3. Add a **cache** (top-down).
4. If you want, convert to a **table** (bottom-up) and shrink memory.

## Common mistakes

:::{warning}
- **A vague state** ("dp[i] is the answer"). Say exactly: "dp[i] = the best value using the first i items".
- **Wrong iteration order**, so a needed value is not computed yet.
- **Forgetting the base case**, or initialising `INF` too small / `0` where "impossible" is needed.
- **Using greedy** where choices overlap (coin change with odd coins).
- **Mutable default cache** shared between test cases; reset it.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Climbing Stairs](https://leetcode.com/problems/climbing-stairs/) | Easy | the first DP |
| [House Robber](https://leetcode.com/problems/house-robber/) | Medium | skip or take |
| [Coin Change](https://leetcode.com/problems/coin-change/) | Medium | unbounded |
| [Unique Paths](https://leetcode.com/problems/unique-paths/) | Medium | grid |
| [Longest Common Subsequence](https://leetcode.com/problems/longest-common-subsequence/) | Medium | two strings |
| [Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence/) | Medium | O(n²) then O(n log n) |
| [Partition Equal Subset Sum](https://leetcode.com/problems/partition-equal-subset-sum/) | Medium | 0/1 knapsack |
| [Edit Distance](https://leetcode.com/problems/edit-distance/) | Medium | insert / delete / replace |

```{raw} html
<p><a class="reference external" href="/prep/practice/#pattern=dynamic-programming"><strong>Open the Dynamic Programming problems in the tracker →</strong></a></p>
```
