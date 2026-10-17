# Session 13 · Depth-First Search (DFS)

## The big idea

You are in a maze holding a **ball of string**. You walk down one corridor as far as it goes. At a dead
end you follow the string **back to the last fork** and try the next corridor. You finish *everything*
behind one door before you try the next door.

That is **DFS**: go **deep first**, then **backtrack**. Where BFS spreads out like ripples, DFS dives
like a diver.

:::{admonition} In plain words
:class: tip
Visit a node, then **recursively visit each unvisited neighbour**. The function call stack remembers
the way back (the "string"). Mark nodes **visited** so you never loop.

**Reach for it when:**

- you must **explore everything** reachable: connected components, number of islands, flood fill
- you need to find **any path**, detect a **cycle**, or check "is X reachable from Y?"
- the problem has a natural **recursive** structure (trees, nested data)
:::

## The picture

```{raw} html
:file: ../diagrams/dfs.html
```

## Step by step

Tree: `A` has children `B, C`; `B` has `D, E`; `C` has `F`. The numbers in the picture are the visit order.

| call | action |
|---|---|
| `dfs(A)` | visit A, go to first child B |
| `dfs(B)` | visit B, go to D |
| `dfs(D)` | visit D, no children, **return to B** |
| `dfs(E)` | visit E, return to B, B is done, **return to A** |
| `dfs(C)` | visit C, go to F |
| `dfs(F)` | visit F, return, return |

## The template (graph)

```python
def dfs(graph, node, visited):
    visited.add(node)
    for nb in graph[node]:
        if nb not in visited:
            dfs(graph, nb, visited)

def count_components(n, edges):
    graph = {i: [] for i in range(n)}
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)
    visited, count = set(), 0
    for node in range(n):
        if node not in visited:         # a new, unexplored piece
            dfs(graph, node, visited)
            count += 1
    return count

print(count_components(5, [[0, 1], [1, 2], [3, 4]]))
```

**Output:**

```text
2
```

Time **O(V + E)**, space **O(V)** for the visited set plus the recursion depth.

## The template (grid): number of islands

An island is a group of `1`s connected up/down/left/right. Every time we find an unvisited `1`, we have
discovered a new island; DFS then **sinks** it (marks all its cells) so we don't count it twice.

```python
def num_islands(grid):
    R, C = len(grid), len(grid[0])

    def sink(r, c):
        if not (0 <= r < R and 0 <= c < C) or grid[r][c] != "1":
            return
        grid[r][c] = "0"                      # mark visited by changing the cell
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sink(r + dr, c + dc)

    islands = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == "1":
                islands += 1
                sink(r, c)
    return islands

print(num_islands([list("11000"), list("11000"), list("00100"), list("00011")]))
```

**Output:**

```text
3
```

## Path finding and cycle detection

For a **directed** graph, a cycle exists if DFS reaches a node that is **still on the current path**.
Use three states: *unvisited*, *in progress* (on the current path), *done*.

```python
def has_cycle(n, edges):
    graph = {i: [] for i in range(n)}
    for a, b in edges:
        graph[a].append(b)
    state = [0] * n                          # 0 new, 1 in progress, 2 done

    def visit(u):
        state[u] = 1
        for v in graph[u]:
            if state[v] == 1:
                return True                  # back to a node on the current path
            if state[v] == 0 and visit(v):
                return True
        state[u] = 2
        return False

    return any(state[u] == 0 and visit(u) for u in range(n))

print(has_cycle(3, [[0, 1], [1, 2], [2, 0]]), has_cycle(3, [[0, 1], [1, 2]]))
```

**Output:**

```text
True False
```

## DFS or BFS?

| need | pick |
|---|---|
| **shortest path** (unweighted) | BFS |
| explore all / connected components / islands | DFS (or BFS, either works) |
| detect cycles, topological order, backtracking | DFS |
| very deep graph (recursion limit) | iterative DFS with an explicit stack |

An iterative DFS replaces recursion with a list used as a stack (`stack.append`, `stack.pop()`), which
avoids Python's recursion limit of about 1000.

## Common mistakes

:::{warning}
- **Forgetting to mark visited**: infinite recursion on a graph with a cycle.
- **Using "visited" for cycle detection in a directed graph.** Visited alone cannot tell the difference between "seen on another branch" and "on my path". Use three states.
- **Recursion depth** on a 10⁵-node chain: use an explicit stack.
- **Mutating the input grid** when the caller needs it afterwards. Copy it or use a `visited` set.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Number of Islands](https://leetcode.com/problems/number-of-islands/) | Medium | flood fill |
| [Flood Fill](https://leetcode.com/problems/flood-fill/) | Easy | the basic grid DFS |
| [Max Area of Island](https://leetcode.com/problems/max-area-of-island/) | Medium | return the size from DFS |
| [Surrounded Regions](https://leetcode.com/problems/surrounded-regions/) | Medium | DFS from the border |
| [Clone Graph](https://leetcode.com/problems/clone-graph/) | Medium | map old → new node |
| [Pacific Atlantic Water Flow](https://leetcode.com/problems/pacific-atlantic-water-flow/) | Medium | reverse the direction |

```{raw} html
<p><a class="reference external" href="/prep/#pattern=depth-first-search-dfs"><strong>Open the Depth First Search problems in the tracker →</strong></a></p>
```
