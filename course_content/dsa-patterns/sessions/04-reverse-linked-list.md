# Session 4 · Reversing a Linked List

## The big idea

A line of children, each **holding the hand of the child in front**. You want the line to face the
other way. Each child must let go of the child in front and **grab the hand of the child behind**.

You do it **one child at a time**, from the front. Before a child lets go, you must **remember who is
next in line**, otherwise the rest of the line is lost.

That is the whole pattern: **flip one link, remember the next node, step forward.**

:::{admonition} In plain words
:class: tip
Walk through the list with three names (`prev`, `curr`, `next`). At each node, point it backwards
instead of forwards. No new list is created, so memory stays **O(1)**.

**Reach for it when:**

- you must **reverse** a linked list, or **part** of it (between positions `left` and `right`)
- you need to reverse in **groups of k**
- a problem needs the second half reversed (palindrome check, reorder list)
:::

## The picture

```{raw} html
:file: ../diagrams/reverse-list.html
```

## Step by step

Reverse `1 → 2 → 3 → null`. We keep `prev = None` and `curr = head`.

| step | `curr` | save `nxt` | flip `curr.next` | move |
|---|---|---|---|---|
| 1 | 1 | 2 | `1.next = None` | `prev = 1`, `curr = 2` |
| 2 | 2 | 3 | `2.next = 1` | `prev = 2`, `curr = 3` |
| 3 | 3 | None | `3.next = 2` | `prev = 3`, `curr = None` |

`curr` is `None`, so we stop. `prev` is the new head: `3 → 2 → 1 → null`.

```python
class Node:
    def __init__(self, val, next=None):
        self.val, self.next = val, next

def reverse(head):
    prev, curr = None, head
    while curr:
        nxt = curr.next      # 1. remember the rest
        curr.next = prev     # 2. flip the link
        prev, curr = curr, nxt   # 3. step forward
    return prev

def to_list(n):
    out = []
    while n:
        out.append(n.val); n = n.next
    return out

print(to_list(reverse(Node(1, Node(2, Node(3))))))
```

**Output:**

```text
[3, 2, 1]
```

Time **O(n)**, space **O(1)**.

## Reversing only a part

*Reverse the nodes from position `left` to `right`.*

1. Walk to the node **just before** `left` (call it `before`). A **dummy node** in front of the head
   avoids special cases when `left = 1`.
2. Reverse `right - left + 1` nodes with the same three-line loop.
3. **Reconnect** the three pieces: `before` → reversed part → the rest.

```python
def reverse_between(head, left, right):
    dummy = Node(0, head)
    before = dummy
    for _ in range(left - 1):
        before = before.next
    curr = before.next
    for _ in range(right - left):            # move one node to the front, repeatedly
        nxt = curr.next
        curr.next = nxt.next
        nxt.next = before.next
        before.next = nxt
    return dummy.next

head = Node(1, Node(2, Node(3, Node(4, Node(5)))))
print(to_list(reverse_between(head, 2, 4)))
```

**Output:**

```text
[1, 4, 3, 2, 5]
```

## Using it inside other problems

**Palindrome linked list** in O(1) space: find the middle (session 3), reverse the second half,
compare it with the first half, optionally reverse it back.

```python
def is_palindrome(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    second = reverse(slow)
    first = head
    while second:
        if first.val != second.val:
            return False
        first, second = first.next, second.next
    return True
```

## Common mistakes

:::{warning}
- **Flipping before saving `next`.** Then `curr.next` is gone and the rest of the list is lost.
- **Forgetting to return `prev`** (not `curr`, which is `None` at the end).
- **Not reconnecting the pieces** in sub-list reversal, which leaves the list broken or cyclic.
- **Skipping the dummy node** and fighting special cases for `left = 1`.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/) | Easy | the basic loop |
| [Reverse Linked List II](https://leetcode.com/problems/reverse-linked-list-ii/) | Medium | sub-list + reconnect |
| [Reverse Nodes in k-Group](https://leetcode.com/problems/reverse-nodes-in-k-group/) | Hard | repeat the sub-list reversal |
| [Palindrome Linked List](https://leetcode.com/problems/palindrome-linked-list/) | Easy | middle + reverse half |
| [Reorder List](https://leetcode.com/problems/reorder-list/) | Medium | middle, reverse, merge |

```{raw} html
<p><a class="reference external" href="/prep/practice/#pattern=reversal-of-linked-list"><strong>Open the Reversal of Linked List problems in the tracker →</strong></a></p>
```
