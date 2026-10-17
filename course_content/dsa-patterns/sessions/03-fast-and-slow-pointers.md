# Session 3 · Fast and Slow Pointers

## The big idea

Two children run on a track. **One runs twice as fast.**

- If the track is a **straight road**, the fast child reaches the end first, and at that moment the
  slow child is **exactly in the middle**.
- If the track is a **circle**, the fast child eventually comes up behind the slow one and they **meet**.

So "do they meet?" tells you whether there is a loop, with no notebook needed. This is the
**fast and slow pointers** pattern (also called *Floyd's tortoise and hare*).

:::{admonition} In plain words
:class: tip
Move two pointers through a linked list (or a sequence) at **different speeds**: slow by 1, fast by 2.
Their meeting, or the place where the fast one ends, answers your question using **O(1) memory**.

**Reach for it when:**

- the problem mentions a **cycle** or a **loop** in a linked list or a repeating sequence
- you need the **middle** of a linked list in one pass
- you must find a **duplicate** or a "happy number" without extra space
:::

## The picture

```{raw} html
:file: ../diagrams/fast-slow.html
```

Inside the loop, the fast pointer gains **one step per move** on the slow one. A gap that shrinks by
1 each move must reach 0, so they always meet.

## Step by step: is there a cycle?

List `1 → 2 → 3 → 4 → 5 → 3 …` (5 points back to 3).

| move | slow | fast |
|---|---|---|
| start | 1 | 1 |
| 1 | 2 | 3 |
| 2 | 3 | 5 |
| 3 | 4 | 4 |
| 4 | 5 | 3 |
| 5 | 3 | 5 |
| 6 | 4 | 4 ← **meet** |

```python
class Node:
    def __init__(self, val, next=None):
        self.val, self.next = val, next

def has_cycle(head):
    slow = fast = head
    while fast and fast.next:        # fast can take 2 steps
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False                     # fast fell off the end
```

Time **O(n)**, space **O(1)**. A hash set would also work but costs O(n) memory.

## Finding where the cycle starts

After they meet, put **one pointer back at the head** and move *both* **one step at a time**. They
meet again exactly at the **start of the cycle**.

Why? Let the head be `a` steps from the cycle start and the meeting point be `b` steps into the
cycle, with cycle length `c`. Fast has travelled twice as far as slow, so `a + b = k·c` for some
whole number `k`. That means walking `a` more steps from the meeting point lands you on the
cycle start, which is also where the head pointer ends up after `a` steps.

```python
def cycle_start(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            slow = head
            while slow is not fast:
                slow, fast = slow.next, fast.next
            return slow
    return None
```

## Finding the middle

When the fast pointer reaches the end, the slow one is in the middle.

```python
def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow

# 1 -> 2 -> 3 -> 4 -> 5
head = Node(1, Node(2, Node(3, Node(4, Node(5)))))
print(middle(head).val)
```

**Output:**

```text
3
```

For an even length (`1→2→3→4`) this returns the **second** middle (3). If you need the first, start
`fast` at `head.next`.

## Not only linked lists: Happy Number

Repeatedly replace a number with the sum of the squares of its digits. It either reaches 1
(*happy*) or loops forever. A loop in a **sequence** is detected the same way.

```python
def is_happy(n):
    step = lambda x: sum(int(d) ** 2 for d in str(x))
    slow, fast = n, step(n)
    while fast != 1 and slow != fast:
        slow, fast = step(slow), step(step(fast))
    return fast == 1

print(is_happy(19), is_happy(2))
```

**Output:**

```text
True False
```

## Common mistakes

:::{warning}
- **`while fast.next.next`** without checking `fast` and `fast.next` first: a crash on `None`.
- **Starting the two pointers at different nodes** for cycle detection (they must both begin at the head).
- **Forgetting the "reset one pointer to head" step** when asked for the cycle *start*.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Linked List Cycle](https://leetcode.com/problems/linked-list-cycle/) | Easy | detect |
| [Middle of the Linked List](https://leetcode.com/problems/middle-of-the-linked-list/) | Easy | slow ends in the middle |
| [Linked List Cycle II](https://leetcode.com/problems/linked-list-cycle-ii/) | Medium | find the start |
| [Happy Number](https://leetcode.com/problems/happy-number/) | Easy | cycle in a number sequence |
| [Find the Duplicate Number](https://leetcode.com/problems/find-the-duplicate-number/) | Medium | array as a linked list |
| [Palindrome Linked List](https://leetcode.com/problems/palindrome-linked-list/) | Easy | middle + reverse (next session) |

```{raw} html
<p><a class="reference external" href="/prep/#pattern=fast-and-slow-pointer"><strong>Open the Fast and Slow Pointer problems in the tracker →</strong></a></p>
```
