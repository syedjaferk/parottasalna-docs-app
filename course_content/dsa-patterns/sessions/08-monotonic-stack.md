# Session 8 · Monotonic Stack

## The big idea

Children stand in a line for a class photo. Every child wants to know: **"Who is the first taller
child standing behind me?"**

Instead of every child looking down the whole line, we use a **pile** (a stack). Walking along the
line, when a **taller** child arrives, all the shorter children waiting on the pile learn their answer
("it's *you*!") and **leave the pile**. Then the new child joins the pile. The pile is always ordered
by height, from tall at the bottom to short at the top. That is why it is called **monotonic**.

:::{admonition} In plain words
:class: tip
Keep a **stack of items still waiting for an answer**, in sorted order. A new item **pops** everyone
it answers, then gets pushed itself. Every item is pushed once and popped once: **O(n)**.

**Reach for it when:**

- "**next** greater / smaller element", "previous greater / smaller"
- "how many days until a warmer day" (**daily temperatures**)
- rectangles or areas bounded by the nearest **taller** neighbours (histogram, trapping rain water)
:::

## The picture

```{raw} html
:file: ../diagrams/mono-stack.html
```

## Step by step: daily temperatures

For each day, how many days until a warmer one? `T = [73, 74, 75, 71, 69, 72, 76, 73]`.

We store **indexes** on the stack so we can compute distances.

| i | T[i] | stack before | pops (warmer day found) | stack after |
|---|---|---|---|---|
| 0 | 73 | [] | – | [0] |
| 1 | 74 | [0] | 0 (1 − 0 = **1**) | [1] |
| 2 | 75 | [1] | 1 (2 − 1 = **1**) | [2] |
| 3 | 71 | [2] | – | [2, 3] |
| 4 | 69 | [2, 3] | – | [2, 3, 4] |
| 5 | 72 | [2, 3, 4] | 4 (**1**), 3 (**2**) | [2, 5] |
| 6 | 76 | [2, 5] | 5 (**1**), 2 (**4**) | [6] |
| 7 | 73 | [6] | – | [6, 7] |

Days left on the stack (6 and 7) never see a warmer day, so their answer is 0.

```python
def daily_temperatures(T):
    ans = [0] * len(T)
    stack = []                            # indexes, temperatures decreasing
    for i, t in enumerate(T):
        while stack and T[stack[-1]] < t:
            j = stack.pop()
            ans[j] = i - j
        stack.append(i)
    return ans

print(daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]))
```

**Output:**

```text
[1, 1, 4, 2, 1, 1, 0, 0]
```

Time **O(n)**, space **O(n)**.

## Picking the right order

| want | stack keeps | pop while |
|---|---|---|
| next **greater** | decreasing values | `top < current` |
| next **smaller** | increasing values | `top > current` |
| previous greater / smaller | scan the same way, but the answer is the **top left behind** (what remains under the new item) | same |

## Worked example: largest rectangle in a histogram

Bars `[2, 1, 5, 6, 2, 3]`. For each bar, how far can a rectangle of **its height** stretch? Until the
nearest **smaller** bar on each side. A stack of increasing heights finds both edges.

```python
def largest_rectangle(h):
    stack = []                           # indexes, heights increasing
    best = 0
    for i, cur in enumerate(h + [0]):    # a final 0 flushes the stack
        while stack and h[stack[-1]] > cur:
            height = h[stack.pop()]
            left = stack[-1] if stack else -1
            best = max(best, height * (i - left - 1))
        stack.append(i)
    return best

print(largest_rectangle([2, 1, 5, 6, 2, 3]))
```

**Output:**

```text
10
```

(The best rectangle is the bars `5` and `6`: height 5, width 2.)

## Common mistakes

:::{warning}
- **Pushing values instead of indexes**, which loses the distance information.
- **Wrong comparison** (`<` vs `<=`) when equal values exist; decide whether equal values should pop.
- **Not flushing the stack** at the end when the problem needs those leftovers (the sentinel `0`).
- **Choosing increasing when you need decreasing**: draw the first two or three steps to check.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Next Greater Element I](https://leetcode.com/problems/next-greater-element-i/) | Easy | the base pattern |
| [Daily Temperatures](https://leetcode.com/problems/daily-temperatures/) | Medium | store indexes |
| [Online Stock Span](https://leetcode.com/problems/online-stock-span/) | Medium | previous greater |
| [Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/) | Hard | nearest smaller on both sides |
| [Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/) | Hard | pop and compute the water layer |
| [Remove K Digits](https://leetcode.com/problems/remove-k-digits/) | Medium | keep the stack increasing |

```{raw} html
<p><a class="reference external" href="/prep/#pattern=monotonic-stack"><strong>Open the Monotonic Stack problems in the tracker →</strong></a></p>
```
