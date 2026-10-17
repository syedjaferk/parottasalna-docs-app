# Session 20 · Top K Elements

## The big idea

A talent show must pick the **3 best singers** from 1,000 contestants. You don't have to rank all of
them. You build a small **podium with only 3 places**. Every new singer is compared with the **weakest
person on the podium**. If the newcomer is better, the weakest steps down and the newcomer climbs up.
At the end, the podium holds the best 3.

The podium is a **min-heap of size K**, a tiny structure that always tells you its smallest item in
one step.

:::{admonition} In plain words
:class: tip
A **heap** gives you the smallest (or largest) element in **O(1)** and lets you add or remove one in
**O(log n)**. To keep the **K largest**, hold a **min-heap of size K**: the top is the *K-th largest so
far* and the first one to be kicked out. Total time **O(n log k)**, much better than sorting for small k.

**Reach for it when:**

- "the **K largest / smallest / most frequent / closest**"
- "the **K-th** largest element"
- you stream data and must always know the top few
:::

## The picture

```{raw} html
:file: ../diagrams/top-k.html
```

## Python's heap

`heapq` is a **min**-heap on a plain list.

```python
import heapq

h = []
for x in [5, 2, 9, 1]:
    heapq.heappush(h, x)
print(h[0], heapq.heappop(h), h[0])       # smallest, remove it, new smallest
```

**Output:**

```text
1 1 2
```

For a **max**-heap, push **negated** values and negate again when you read them.

## K largest elements

```python
import heapq

def k_largest(nums, k):
    heap = []
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)           # drop the smallest of the K+1
    return sorted(heap, reverse=True)

print(k_largest([5, 2, 9, 1, 7, 8], 3))
```

**Output:**

```text
[9, 8, 7]
```

The **K-th largest** is simply `heap[0]` after the loop.

## Why a min-heap for the largest?

The thing you must repeatedly find is "**the weakest of the current top K**", because that is what
a newcomer must beat. That is a **minimum**. Using a max-heap would hand you the strongest, which is useless.

| want | heap | size |
|---|---|---|
| K **largest** | **min**-heap | K |
| K **smallest** | **max**-heap (negate) | K |

## Top K frequent words

Count first (hash map), then keep a heap of size K by `(frequency, word)`.

```python
import heapq
from collections import Counter

def top_k_frequent(nums, k):
    count = Counter(nums)
    return heapq.nlargest(k, count.keys(), key=count.get)

print(top_k_frequent([1, 1, 1, 2, 2, 3], 2))
```

**Output:**

```text
[1, 2]
```

`heapq.nlargest` and `nsmallest` are shortcuts that do exactly this.

## K closest points to the origin

Distance is `x² + y²` (no square root needed to compare). Keep the K **smallest** distances: a
**max**-heap of size K, so we push `-distance`.

```python
import heapq

def k_closest(points, k):
    heap = []
    for x, y in points:
        d = -(x * x + y * y)               # negative: max-heap behaviour
        heapq.heappush(heap, (d, x, y))
        if len(heap) > k:
            heapq.heappop(heap)            # remove the farthest
    return [[x, y] for _, x, y in heap]

print(sorted(k_closest([[1, 3], [-2, 2], [5, 8], [0, 1]], 2)))
```

**Output:**

```text
[[-2, 2], [0, 1]]
```

## Alternatives worth knowing

| approach | time | when |
|---|---|---|
| sort everything | O(n log n) | simplest, small n |
| **heap of size K** | O(n log k) | **streams** and small k |
| quickselect | O(n) average | one-shot K-th element |
| bucket sort by frequency | O(n) | top K frequent |

## Common mistakes

:::{warning}
- **Max-heap when you need min-heap** (or the reverse) for the "K largest".
- **Forgetting that `heapq` is a min-heap only**: negate for max.
- **Comparing unorderable items** in tuples when priorities tie (dicts, nodes). Add a tie-breaking counter: `(priority, count, item)`.
- **Returning the heap unsorted** when the problem wants ordered output.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/) | Medium | min-heap of size k |
| [Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) | Medium | counter + heap |
| [K Closest Points to Origin](https://leetcode.com/problems/k-closest-points-to-origin/) | Medium | max-heap of size k |
| [Kth Largest Element in a Stream](https://leetcode.com/problems/kth-largest-element-in-a-stream/) | Easy | persistent heap |
| [Sort Characters By Frequency](https://leetcode.com/problems/sort-characters-by-frequency/) | Medium | count, then order |
| [Reorganize String](https://leetcode.com/problems/reorganize-string/) | Medium | always take the most frequent |

```{raw} html
<p><a class="reference external" href="/prep/practice/#pattern=top-k-elements"><strong>Open the Top K Elements problems in the tracker →</strong></a></p>
```
