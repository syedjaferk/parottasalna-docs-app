# Session 23 · Design Data Structures

## The big idea

You are building your own **toy box** with special rules, such as: *"the toy I played with last is the
easiest to grab, and when the box is full the toy I haven't touched for the longest time goes away."*
(That is an **LRU cache**.)

One plain box can't do both jobs quickly. A shelf with labels lets you **find** any toy at once, but
doesn't remember **order**. A line on the wall remembers **order**, but finding a toy means walking the
line. So you use **two simple tools together**, each doing what it is good at, and **tie them together**
with strings, so every action updates both.

:::{admonition} In plain words
:class: tip
List the operations and the **speed each must have** (usually O(1)). Choose **building blocks**: a
hash map (lookup), a doubly linked list (order, cheap insert/remove), a heap (min/max), an array
(random access). Make the blocks **point at each other** and keep them **consistent**.

**Reach for it when:** the problem says "design a class" with `get`, `put`, `push`, `pop`, `insert`,
`getRandom`, or "in O(1)".
:::

## The picture

```{raw} html
:file: ../diagrams/lru.html
```

## Example 1 · LRU cache (hash map + doubly linked list)

- `get(k)`: find the node in the **map**, move it to the **front** (most recent).
- `put(k, v)`: add or update at the front; if over capacity, remove the **back** node (least recent).

Python's `OrderedDict` is a hash map + linked list already. Interviewers often ask you to build it by hand:

```python
class Node:
    def __init__(self, key=0, val=0):
        self.key, self.val = key, val
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.map = {}
        self.head, self.tail = Node(), Node()        # dummy ends avoid edge cases
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, n):
        n.prev.next, n.next.prev = n.next, n.prev

    def _add_front(self, n):
        n.next, n.prev = self.head.next, self.head
        self.head.next.prev = n
        self.head.next = n

    def get(self, key):
        if key not in self.map:
            return -1
        n = self.map[key]
        self._remove(n); self._add_front(n)         # now the most recent
        return n.val

    def put(self, key, val):
        if key in self.map:
            self._remove(self.map[key])
        n = self.map[key] = Node(key, val)
        self._add_front(n)
        if len(self.map) > self.cap:
            lru = self.tail.prev                    # the least recently used
            self._remove(lru)
            del self.map[lru.key]

c = LRUCache(2)
c.put(1, 1); c.put(2, 2)
print(c.get(1))
c.put(3, 3)                                         # evicts key 2
print(c.get(2), c.get(3))
```

**Output:**

```text
1
-1 3
```

Both `get` and `put` are **O(1)**.

## Example 2 · Min stack (stack + helper stack)

`getMin()` in O(1): keep a second stack that stores the **minimum so far** at every level.

```python
class MinStack:
    def __init__(self):
        self.stack, self.mins = [], []

    def push(self, x):
        self.stack.append(x)
        self.mins.append(min(x, self.mins[-1]) if self.mins else x)

    def pop(self):
        self.mins.pop()
        return self.stack.pop()

    def get_min(self):
        return self.mins[-1]

s = MinStack()
for x in [5, 3, 7, 2]:
    s.push(x)
print(s.get_min(), end=" ")
s.pop()
print(s.get_min())
```

**Output:**

```text
2 3
```

## Example 3 · Insert / delete / getRandom in O(1) (array + hash map)

An **array** gives a random element in O(1). A **map from value to index** gives O(1) lookup. To delete in
O(1), **swap the element with the last one**, then pop.

```python
import random

class RandomizedSet:
    def __init__(self):
        self.items, self.pos = [], {}

    def insert(self, x):
        if x in self.pos:
            return False
        self.pos[x] = len(self.items)
        self.items.append(x)
        return True

    def remove(self, x):
        if x not in self.pos:
            return False
        i, last = self.pos[x], self.items[-1]
        self.items[i], self.pos[last] = last, i       # move the last item into the hole
        self.items.pop()
        del self.pos[x]
        return True

    def get_random(self):
        return random.choice(self.items)

r = RandomizedSet()
print(r.insert(1), r.insert(2), r.remove(1), r.insert(2), sorted(r.items))
```

**Output:**

```text
True True True False [2]
```

## Example 4 · Trie (prefix tree)

Each node is a letter; a path from the root spells a word. Search, insert and "starts with" cost
**O(length of the word)**, independent of how many words are stored.

```python
class Trie:
    def __init__(self):
        self.root = {}

    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node["$"] = True                       # marks the end of a word

    def _walk(self, s):
        node = self.root
        for ch in s:
            if ch not in node:
                return None
            node = node[ch]
        return node

    def search(self, word):
        node = self._walk(word)
        return bool(node and "$" in node)

    def starts_with(self, prefix):
        return self._walk(prefix) is not None

t = Trie()
t.insert("apple")
print(t.search("apple"), t.search("app"), t.starts_with("app"))
```

**Output:**

```text
True False True
```

## Choosing building blocks

| need | use |
|---|---|
| lookup by key in O(1) | hash map |
| order of use / insert and remove anywhere in O(1) | doubly linked list (with a map to its nodes) |
| smallest / largest quickly | heap |
| random access by index | array |
| prefix queries on strings | trie |
| min/max at every point of a stack | helper stack |

## Common mistakes

:::{warning}
- **Updating one structure and forgetting the other** (the map says the key exists but the list lost it).
- **Edge cases:** capacity 1, empty structure, duplicates, removing the last element.
- **Linked list pointers in the wrong order** when unlinking: draw the four pointers on paper.
- **Missing dummy head/tail nodes**, which forces many `if node is None` checks.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Min Stack](https://leetcode.com/problems/min-stack/) | Medium | helper stack |
| [Implement Queue using Stacks](https://leetcode.com/problems/implement-queue-using-stacks/) | Easy | two stacks |
| [LRU Cache](https://leetcode.com/problems/lru-cache/) | Medium | map + list |
| [Implement Trie (Prefix Tree)](https://leetcode.com/problems/implement-trie-prefix-tree/) | Medium | dict of dicts |
| [Insert Delete GetRandom O(1)](https://leetcode.com/problems/insert-delete-getrandom-o1/) | Medium | swap with last |
| [LFU Cache](https://leetcode.com/problems/lfu-cache/) | Hard | frequency buckets |

```{raw} html
<p><a class="reference external" href="/prep/#pattern=design-data-structure"><strong>Open the Design Data Structure problems in the tracker →</strong></a></p>
```
