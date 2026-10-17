# Session 2 · Sliding Window

## The big idea

You are on a train and look through a **window frame**. You only see a few carriages at a time.
When the train moves one step, **one new carriage appears on the right and one disappears on the
left**. You don't recount all the carriages you see; you just add the new one and remove the old one.

Now suppose a problem asks: *"What is the longest stretch of a string with no repeated letter?"* or
*"What is the biggest sum of 3 numbers in a row?"* Checking every stretch from scratch is slow. A
**window** that grows on the right and shrinks on the left does the job in one pass.

:::{admonition} In plain words
:class: tip
Keep a **window** `[left, right]` over a sequence and a small **state** about what is inside (a sum,
a count, a set of letters). Grow it by moving `right`. If it breaks the rule, shrink it by moving `left`.

**Reach for it when:**

- the problem is about a **contiguous** part: subarray or substring
- you want the **longest, shortest, biggest** such part
- there is a rule like "at most k distinct", "no repeats", "sum ≥ target"
:::

## The picture

```{raw} html
:file: ../diagrams/sliding-window.html
```

The right edge only ever moves forward, and so does the left edge. Together they move at most `2n`
times, which is why the pattern is **O(n)** even though it has a loop inside a loop.

## Two kinds of window

**Fixed size** (window length `k` is given): slide by adding `a[right]` and removing `a[right - k]`.

```python
def max_sum_k(a, k):
    window = sum(a[:k])
    best = window
    for right in range(k, len(a)):
        window += a[right] - a[right - k]    # one in, one out
        best = max(best, window)
    return best

print(max_sum_k([2, 1, 5, 1, 3, 2], 3))
```

**Output:**

```text
9
```

(The best window is `[5, 1, 3]`.)

**Variable size** (find the longest/shortest window that obeys a rule): grow, then shrink while broken.

```python
def longest_unique(s):
    seen = {}                       # letter -> how many times in the window
    left = best = 0
    for right, ch in enumerate(s):
        seen[ch] = seen.get(ch, 0) + 1
        while seen[ch] > 1:         # rule broken: a repeat
            seen[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best

print(longest_unique("abcabcbb"))
```

**Output:**

```text
3
```

## Step by step

`s = "abcabcbb"`

| right | char | window | repeat? | action | best |
|---|---|---|---|---|---|
| 0 | a | `a` | no | grow | 1 |
| 1 | b | `ab` | no | grow | 2 |
| 2 | c | `abc` | no | grow | 3 |
| 3 | a | `abca` | **yes** | remove `a` at left → `bca` | 3 |
| 4 | b | `bcab` | **yes** | remove `b` → `cab` | 3 |
| 5 | c | `cabc` | **yes** | remove `c` → `abc` | 3 |
| 6 | b | `abcb` | **yes** | remove `a`, `b` → `cb` | 3 |
| 7 | b | `cbb` | **yes** | remove `c`, `b` → `b` | 3 |

## The recipe in four lines

1. Move `right` forward and **add** `a[right]` to the state.
2. While the window is **invalid**, **remove** `a[left]` from the state and move `left` forward.
3. Now the window is valid: **record the answer** (longest, or best sum).
4. Repeat until `right` reaches the end.

For the *shortest* window (for example "smallest subarray with sum ≥ target"), flip step 2 and 3:
record the answer **while the window is valid**, and shrink as long as it still stays valid.

```python
def min_subarray_len(target, a):
    left = total = 0
    best = float("inf")
    for right, x in enumerate(a):
        total += x
        while total >= target:                 # still valid: try to make it smaller
            best = min(best, right - left + 1)
            total -= a[left]
            left += 1
    return 0 if best == float("inf") else best

print(min_subarray_len(7, [2, 3, 1, 2, 4, 3]))
```

**Output:**

```text
2
```

## Common mistakes

:::{warning}
- **Using it with negative numbers and a sum rule.** Shrinking might *increase* the sum, so the logic breaks. Use prefix sums + a hash map (session 6).
- **Forgetting to remove `a[left]` from the state** before moving `left`.
- **Recording the answer before the window is valid again** (for "longest" problems).
- **Off by one in the length:** it is `right - left + 1`.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Maximum Average Subarray I](https://leetcode.com/problems/maximum-average-subarray-i/) | Easy | fixed window |
| [Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | Medium | the classic |
| [Minimum Size Subarray Sum](https://leetcode.com/problems/minimum-size-subarray-sum/) | Medium | shortest window |
| [Longest Repeating Character Replacement](https://leetcode.com/problems/longest-repeating-character-replacement/) | Medium | window valid if `len - maxfreq ≤ k` |
| [Permutation in String](https://leetcode.com/problems/permutation-in-string/) | Medium | fixed window of counts |
| [Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/) | Hard | shortest window + two counters |

```{raw} html
<p><a class="reference external" href="/prep/practice/#pattern=sliding-window"><strong>Open the Sliding Window problems in the tracker →</strong></a></p>
```
