# Session 22 · Two Heaps

## The big idea

Children arrive one at a time and you must always be able to say **who is standing in the exact middle
when they are sorted by height**. Sorting after every arrival is slow.

So you split the children into **two groups**:

- a **"shorter half"** where you can instantly see the **tallest** child of that half, and
- a **"taller half"** where you can instantly see the **shortest** child of that half.

The two children facing each other across the divide are **the middle**. If you keep the groups the
same size, the median is right there. Each newcomer is slotted into the correct group, and a **quick
balance** keeps the sizes even.

:::{admonition} In plain words
:class: tip
Use a **max-heap for the smaller half** and a **min-heap for the larger half**. Keep their sizes equal
(or the max-heap one bigger). The **tops** of the heaps are the middle values, so the median is read
in **O(1)**, and a new number is inserted in **O(log n)**.

**Reach for it when:**

- **median of a data stream** (or of a sliding window)
- you must split a set into two halves and track the **boundary** (IPO / maximise capital)
- "schedule tasks", where you keep two priority groups
:::

## The picture

```{raw} html
:file: ../diagrams/two-heaps.html
```

## The invariant

1. Every number in the **lower** heap ≤ every number in the **upper** heap.
2. `len(lower) == len(upper)` or `len(lower) == len(upper) + 1`.

If both hold, the median is `lower[0]` (odd count) or the average of both tops (even count).

## Median of a stream

Python's `heapq` is a min-heap, so we store the lower half with **negated** values.

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.lo = []                    # max-heap (stored negated): smaller half
        self.hi = []                    # min-heap: larger half

    def add(self, x):
        heapq.heappush(self.lo, -x)                        # 1. add to the lower half
        heapq.heappush(self.hi, -heapq.heappop(self.lo))   # 2. its largest moves to the upper half
        if len(self.hi) > len(self.lo):                    # 3. keep lo as the (equal or) bigger one
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def median(self):
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2

m = MedianFinder()
medians = []
for x in [1, 2, 3, 4, 5, 7]:
    m.add(x)
    medians.append(m.median())
print(medians)
```

**Output:**

```text
[1, 1.5, 2, 2.5, 3, 3.5]
```

## Why the three-step insert works

Pushing into `lo` and then moving its top to `hi` guarantees that the **ordering rule** (everything in
`lo` ≤ everything in `hi`) stays true no matter where `x` belongs. Step 3 repairs the **sizes**.

| add | `lo` (top is max) | `hi` (top is min) | median |
|---|---|---|---|
| 1 | [1] | [] | 1 |
| 2 | [1] | [2] | 1.5 |
| 3 | [2, 1] | [3] | 2 |
| 4 | [2, 1] | [3, 4] | 2.5 |
| 5 | [3, 2, 1] | [4, 5] | 3 |
| 7 | [3, 2, 1] | [4, 5, 7] | 3.5 |

## Second use: maximise capital (IPO)

You can finish at most `k` projects. Each has a required **capital** and gives **profit**. You start
with `w` capital. Strategy: among projects you can **afford**, always do the **most profitable**.
Two heaps: a **min-heap by capital** (projects waiting to become affordable) and a **max-heap by profit**
(affordable now).

```python
import heapq

def max_capital(k, w, profits, capital):
    waiting = sorted(zip(capital, profits))      # by capital
    avail, i = [], 0
    for _ in range(k):
        while i < len(waiting) and waiting[i][0] <= w:
            heapq.heappush(avail, -waiting[i][1])  # affordable → into the profit max-heap
            i += 1
        if not avail:
            break
        w -= heapq.heappop(avail)               # minus a negative = plus the profit
    return w

print(max_capital(2, 0, [1, 2, 3], [0, 1, 1]))
```

**Output:**

```text
4
```

## Common mistakes

:::{warning}
- **Forgetting to negate** for the max-heap, both on push and on read (`-self.lo[0]`).
- **Skipping the re-balance**, so the sizes drift and the median is wrong.
- **Pushing straight into the "right" heap by comparing with a top** on an empty heap: use the always-valid three-step insert.
- **Integer vs float median:** use `/ 2` for the even case, or `// 2` if the problem asks for an integer.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/) | Hard | the class above |
| [Sliding Window Median](https://leetcode.com/problems/sliding-window-median/) | Hard | removals need lazy deletion |
| [IPO](https://leetcode.com/problems/ipo/) | Hard | affordable vs best profit |
| [Kth Largest Element in a Stream](https://leetcode.com/problems/kth-largest-element-in-a-stream/) | Easy | a single heap is enough |
| [Meeting Rooms II](https://leetcode.com/problems/meeting-rooms-ii/) | Medium | heap of end times |

```{raw} html
<p><a class="reference external" href="/prep/practice/#pattern=two-heaps"><strong>Open the Two Heaps problems in the tracker →</strong></a></p>
```
