# Session 12 · Breadth-First Search (BFS)

## The big idea

Drop a stone into a pond. The ripples spread **ring by ring**: first everything one step away, then
everything two steps away, then three. A ripple never reaches a far place before it has reached all
the nearer places.

**BFS explores exactly like that.** Because it visits places in order of **distance**, the **first time**
BFS reaches your target it has found the **shortest path** (when every step costs the same).

:::{admonition} In plain words
:class: tip
Use a **queue** (first in, first out). Put the start in, then repeat: take the front, and put all of
its **unvisited neighbours** at the back. Mark things **visited** so you never go in circles.

**Reach for it when:**

- "**shortest path** / minimum number of steps / moves" in an unweighted graph, grid or word ladder
- "process a tree **level by level**" (level-order traversal)
- something **spreads** from one or more sources (rotting oranges, fire, flood)
:::

## The picture

```{raw} html
:file: ../diagrams/bfs.html
```

## Step by step

Graph: `A–B, A–C, A–D, B–E, C–F, D–F`. Start at `A`.

| pop | queue after pushing its new neighbours | visited |
|---|---|---|
| A | B, C, D | A, B, C, D |
| B | C, D, E | + E |
| C | D, E, F | + F |
| D | E, F | (F already visited) |
| E | F | |
| F | – | done |

Notice the order `A, B, C, D, E, F`: all level-1 nodes come before any level-2 node.

## The template: shortest distance

```python
from collections import deque

def bfs_shortest(graph, start, goal):
    q = deque([start])
    visited = {start}
    steps = 0
    while q:
        for _ in range(len(q)):            # everything currently in the queue is one level
            node = q.popleft()
            if node == goal:
                return steps
            for nb in graph[node]:
                if nb not in visited:
                    visited.add(nb)        # mark when PUSHING, not when popping
                    q.append(nb)
        steps += 1
    return -1

g = {"A": "BCD", "B": "AE", "C": "AF", "D": "AF", "E": "B", "F": "CD"}
print(bfs_shortest(g, "A", "F"))
```

**Output:**

```text
2
```

Time **O(V + E)**, space **O(V)**.

## On a grid

Treat every cell as a node and its four neighbours as edges.

```python
from collections import deque

def shortest_path_grid(grid):          # 0 = free, 1 = wall; top-left to bottom-right
    R, C = len(grid), len(grid[0])
    if grid[0][0] or grid[R - 1][C - 1]:
        return -1
    q = deque([(0, 0, 1)])             # row, col, distance
    seen = {(0, 0)}
    while q:
        r, c, d = q.popleft()
        if (r, c) == (R - 1, C - 1):
            return d
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == 0 and (nr, nc) not in seen:
                seen.add((nr, nc))
                q.append((nr, nc, d + 1))
    return -1

print(shortest_path_grid([[0, 0, 0], [1, 1, 0], [0, 0, 0]]))
```

**Output:**

```text
5
```

## Multi-source BFS: rotting oranges

Many things spread at the same time. **Put all sources in the queue at the start**, then run the normal
level-by-level loop. The number of levels is the time taken.

```python
from collections import deque

def oranges_rotting(grid):
    R, C = len(grid), len(grid[0])
    q = deque((r, c) for r in range(R) for c in range(C) if grid[r][c] == 2)
    fresh = sum(row.count(1) for row in grid)
    minutes = 0
    while q and fresh:
        for _ in range(len(q)):
            r, c = q.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    q.append((nr, nc))
        minutes += 1
    return minutes if fresh == 0 else -1

print(oranges_rotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]))
```

**Output:**

```text
4
```

## Level-order traversal of a tree

The same loop works on a tree; there is no `visited` set because a tree has no cycles.

```python
from collections import deque

class T:
    def __init__(self, v, l=None, r=None):
        self.val, self.left, self.right = v, l, r

def level_order(root):
    out, q = [], deque([root] if root else [])
    while q:
        out.append([n.val for n in q])
        for _ in range(len(q)):
            n = q.popleft()
            q.extend(c for c in (n.left, n.right) if c)
    return out

print(level_order(T(3, T(9), T(20, T(15), T(7)))))
```

**Output:**

```text
[[3], [9, 20], [15, 7]]
```

## Common mistakes

:::{warning}
- **Marking visited when you pop** instead of when you push: the same node enters the queue many times.
- **Using a list with `pop(0)`** (O(n) each). Use `collections.deque`.
- **Using BFS for weighted edges.** BFS counts steps, not costs. Use Dijkstra there.
- **Forgetting the level loop** (`for _ in range(len(q))`) when you need the distance or the levels.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Binary Tree Level Order Traversal](https://leetcode.com/problems/binary-tree-level-order-traversal/) | Medium | level loop |
| [Rotting Oranges](https://leetcode.com/problems/rotting-oranges/) | Medium | multi-source |
| [Shortest Path in Binary Matrix](https://leetcode.com/problems/shortest-path-in-binary-matrix/) | Medium | 8 directions |
| [Word Ladder](https://leetcode.com/problems/word-ladder/) | Hard | words are nodes |
| [01 Matrix](https://leetcode.com/problems/01-matrix/) | Medium | multi-source from the zeros |
| [Open the Lock](https://leetcode.com/problems/open-the-lock/) | Medium | states are nodes |

```{raw} html
<p><a class="reference external" href="/prep/#pattern=breadth-first-search-bfs"><strong>Open the Breadth First Search problems in the tracker →</strong></a></p>
```
