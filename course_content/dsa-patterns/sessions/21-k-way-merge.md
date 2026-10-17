# Session 21 · K-way Merge

## The big idea

There are **three queues of children**, and each queue is already sorted by height (short at the
front). A teacher wants **one big queue** sorted by height.

She doesn't need to compare every child with every other child. She only looks at the **front child
of each queue**, takes the **shortest of those three**, and then looks at that queue's *new* front
child. She repeats until all queues are empty. The three front children are the only candidates that
matter at any moment: a tiny **heap** keeps them.

:::{admonition} In plain words
:class: tip
Keep a **min-heap with one candidate from each sorted list**. Pop the smallest, write it to the output,
then **push the next item from the same list**. Heap size stays at K, so each of the N items costs
**O(log K)**: total **O(N log K)**.

**Reach for it when:**

- you must **merge K sorted lists / arrays / linked lists**
- "the **K-th smallest** in a sorted matrix" or in several sorted sources
- "smallest range covering at least one number from each list"
:::

## The picture

```{raw} html
:file: ../diagrams/kway.html
```

## Step by step

Lists: `[1, 4, 7]`, `[2, 5, 8]`, `[3, 6, 9]`.

| step | heap (value, list) | pop | output | push |
|---|---|---|---|---|
| start | (1,A) (2,B) (3,C) | | | |
| 1 | (2,B) (3,C) | (1,A) | 1 | (4,A) |
| 2 | (3,C) (4,A) | (2,B) | 1 2 | (5,B) |
| 3 | (4,A) (5,B) | (3,C) | 1 2 3 | (6,C) |
| 4 | (5,B) (6,C) | (4,A) | 1 2 3 4 | (7,A) |
| … | | | | |

## Merge K sorted arrays

```python
import heapq

def merge_k(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]   # (value, which list, index in it)
    heapq.heapify(heap)
    out = []
    while heap:
        val, i, j = heapq.heappop(heap)
        out.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))        # next item from the same list
    return out

print(merge_k([[1, 4, 7], [2, 5, 8], [3, 6, 9]]))
```

**Output:**

```text
[1, 2, 3, 4, 5, 6, 7, 8, 9]
```

Putting the **list index** in the tuple is also what breaks ties safely (no comparing of lists).

## Merge K sorted linked lists

Same idea, but the heap stores `(node.val, list_id, node)`.

```python
import heapq

class ListNode:
    def __init__(self, val, next=None):
        self.val, self.next = val, next

def merge_k_lists(lists):
    heap = [(n.val, i, n) for i, n in enumerate(lists) if n]
    heapq.heapify(heap)
    dummy = tail = ListNode(0)
    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next

def make(*vals):
    head = None
    for v in reversed(vals):
        head = ListNode(v, head)
    return head

res, out = merge_k_lists([make(1, 4, 5), make(1, 3, 4), make(2, 6)]), []
while res:
    out.append(res.val); res = res.next
print(out)
```

**Output:**

```text
[1, 1, 2, 3, 4, 4, 5, 6]
```

## K-th smallest in a sorted matrix

Every **row** is a sorted list, so the matrix is K lists. Start with the first element of each row (or
the first K rows), pop `k` times; the last popped value is the answer.

```python
import heapq

def kth_smallest(matrix, k):
    heap = [(row[0], r, 0) for r, row in enumerate(matrix)]
    heapq.heapify(heap)
    for _ in range(k):
        val, r, c = heapq.heappop(heap)
        if c + 1 < len(matrix[r]):
            heapq.heappush(heap, (matrix[r][c + 1], r, c + 1))
    return val

print(kth_smallest([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8))
```

**Output:**

```text
13
```

## Merge sort vs K-way merge

Merge sort merges **two** sorted halves with two pointers. K-way merge generalises "pick the smaller
of two fronts" to "pick the smallest of K fronts", and a **heap** makes that choice quick. For `K = 2`
the heap is overkill; use two pointers.

## Common mistakes

:::{warning}
- **Pushing all elements** into the heap at once: O(N log N), and you lose the memory benefit. Only push the **next** item.
- **No tie-breaker** in the tuple: Python then tries to compare the nodes or lists and crashes.
- **Forgetting empty lists** at the start (`if lst`).
- **Not advancing the list index** after a pop.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/) | Easy | the K = 2 case |
| [Merge k Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) | Hard | heap of nodes |
| [Kth Smallest Element in a Sorted Matrix](https://leetcode.com/problems/kth-smallest-element-in-a-sorted-matrix/) | Medium | rows are lists |
| [Find K Pairs with Smallest Sums](https://leetcode.com/problems/find-k-pairs-with-smallest-sums/) | Medium | expand neighbours |
| [Smallest Range Covering Elements from K Lists](https://leetcode.com/problems/smallest-range-covering-elements-from-k-lists/) | Hard | track the current max |

```{raw} html
<p><a class="reference external" href="/prep/#pattern=k-way-merge"><strong>Open the K-way Merge problems in the tracker →</strong></a></p>
```
