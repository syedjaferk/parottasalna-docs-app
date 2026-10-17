# Session 14 · Trees

## The big idea

A **family tree** has one grandparent at the top, children below, grandchildren below them. Most tree
questions can be answered by **asking each child the same question** and then combining the answers.

> "How tall is your branch?" 
> Each child answers with the height of *their* branch. You say: "mine is **the tallest child's
> height plus one**."

You never need to understand the whole tree. You only trust that the **children answered correctly**
(recursion) and do **one small step** to combine. The bottom of the tree (an empty child, `None`)
answers with a simple, known value: height 0.

:::{admonition} In plain words
:class: tip
Every tree function has three parts:
**1. base case** (empty node) → **2. ask left and right** → **3. combine and return**.

**Reach for it when:**

- binary tree / BST problems: height, diameter, balanced, same tree, symmetric
- paths and sums: path sum, max path sum, lowest common ancestor
- a BST question: use "left < node < right" to skip half the tree
:::

## The picture

```{raw} html
:file: ../diagrams/trees.html
```

## The template

```python
class Node:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def height(node):
    if not node:                       # 1. base case
        return 0
    left = height(node.left)           # 2. ask the children
    right = height(node.right)
    return 1 + max(left, right)        # 3. combine

root = Node(1, Node(2, Node(4), Node(5)), Node(3))
print(height(root))
```

**Output:**

```text
3
```

Time **O(n)** (each node once), space **O(h)** for the recursion stack (`h` = height; O(n) for a skewed tree).

## The three walk orders

```python
def inorder(n):   return inorder(n.left) + [n.val] + inorder(n.right) if n else []
def preorder(n):  return [n.val] + preorder(n.left) + preorder(n.right) if n else []
def postorder(n): return postorder(n.left) + postorder(n.right) + [n.val] if n else []

print(inorder(root), preorder(root), postorder(root))
```

**Output:**

```text
[4, 2, 5, 1, 3] [1, 2, 4, 5, 3] [4, 5, 2, 3, 1]
```

| order | when | typical use |
|---|---|---|
| **pre**order (node, left, right) | you need the parent before children | copy / serialise a tree |
| **in**order (left, node, right) | | on a **BST** gives sorted order |
| **post**order (left, right, node) | you need children's answers first | height, delete, diameter |

## Two answers: "what I return" vs "what I record"

**Diameter** is the longest path between any two nodes. At each node the best path *through it* is
`left_height + right_height`, but the function must **return** only one branch's height to its parent
(a path cannot fork upwards). So you keep a global best and return the height.

```python
def diameter(root):
    best = 0

    def depth(n):
        nonlocal best
        if not n:
            return 0
        l, r = depth(n.left), depth(n.right)
        best = max(best, l + r)        # record: path through this node
        return 1 + max(l, r)           # return: one branch only

    depth(root)
    return best

print(diameter(root))
```

**Output:**

```text
3
```

This "return one thing, record another" idea also solves *binary tree maximum path sum*.

## Binary search trees

In a BST every value in the left subtree is smaller, and in the right subtree larger. So search and
validation can **skip half** of the tree.

```python
def search_bst(n, target):
    while n and n.val != target:
        n = n.left if target < n.val else n.right
    return n

def is_valid_bst(n, lo=float("-inf"), hi=float("inf")):
    if not n:
        return True
    if not lo < n.val < hi:            # must stay inside the allowed window
        return False
    return is_valid_bst(n.left, lo, n.val) and is_valid_bst(n.right, n.val, hi)

bst = Node(5, Node(3, Node(2), Node(4)), Node(8))
print(search_bst(bst, 4).val, is_valid_bst(bst), is_valid_bst(Node(5, Node(6))))
```

**Output:**

```text
4 True False
```

Checking only `left.val < node.val < right.val` is a classic bug: a node deep in the left subtree can
still be bigger than an ancestor. Pass the **allowed window** down instead.

## Lowest common ancestor

If the current node is one of the two targets, return it. Otherwise ask both sides: if **both** return
something, the current node is the answer; if only one does, pass that one up.

```python
def lca(n, p, q):
    if not n or n is p or n is q:
        return n
    l, r = lca(n.left, p, q), lca(n.right, p, q)
    return n if l and r else (l or r)
```

## Common mistakes

:::{warning}
- **Missing the `None` base case**: `AttributeError: 'NoneType' object has no attribute 'left'`.
- **Mixing return value and recorded answer** (diameter, max path sum).
- **Validating a BST with only parent–child comparisons.** Pass the `(lo, hi)` window.
- **Forgetting recursion depth** for skewed trees with 10⁵ nodes: use an iterative version.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Maximum Depth of Binary Tree](https://leetcode.com/problems/maximum-depth-of-binary-tree/) | Easy | the template |
| [Invert Binary Tree](https://leetcode.com/problems/invert-binary-tree/) | Easy | swap children, recurse |
| [Diameter of Binary Tree](https://leetcode.com/problems/diameter-of-binary-tree/) | Easy | record vs return |
| [Validate Binary Search Tree](https://leetcode.com/problems/validate-binary-search-tree/) | Medium | the window |
| [Lowest Common Ancestor of a Binary Tree](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/) | Medium | both sides answer |
| [Binary Tree Maximum Path Sum](https://leetcode.com/problems/binary-tree-maximum-path-sum/) | Hard | ignore negative branches |

```{raw} html
<p><a class="reference external" href="/prep/practice/#pattern=trees"><strong>Open the Trees problems in the tracker →</strong></a></p>
```
