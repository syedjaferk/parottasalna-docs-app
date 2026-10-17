# Session 15 · Graphs

## The big idea

Picture a playground. Some children **hold hands**. A **graph** is just the list of who is connected
to whom. Questions you might ask:

- Can a message travel from Asha to Ravi through friends? (**connectivity**)
- Is there a circle of friends where everyone waits for the next one? (**cycle**)
- You must put on socks *before* shoes, and shoes *before* tying laces. In what order do you do things? (**topological sort**)
- Which road network connects all villages with the least road? (**minimum spanning tree**)

BFS and DFS (sessions 12–13) are the walking tools. This session adds how to **model** the problem and
two more tools: **topological sort** and **union-find**.

:::{admonition} In plain words
:class: tip
1. **Model**: decide what the *nodes* are and what an *edge* means.
2. **Build an adjacency list** (`node → list of neighbours`).
3. **Pick the tool**: BFS (fewest steps), DFS (explore / cycles), topological sort (dependencies),
   union-find (merge groups), Dijkstra (weighted shortest path).

**Reach for it when:** you see prerequisites, networks, "connected", "reachable", routes, or relations between pairs.
:::

## The picture

```{raw} html
:file: ../diagrams/topo.html
```

## Building the graph

```python
from collections import defaultdict

edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
graph = defaultdict(list)
for a, b in edges:
    graph[a].append(b)          # directed: a -> b
    # graph[b].append(a)        # add this line for an undirected graph
print(dict(graph))
```

**Output:**

```text
{0: [1, 2], 1: [3], 2: [3]}
```

## Topological sort (Kahn's algorithm)

For a **directed acyclic graph** (DAG) of tasks with prerequisites, produce an order where every task
comes after its prerequisites.

1. Compute each node's **in-degree** (how many prerequisites it still has).
2. Put all nodes with in-degree **0** in a queue.
3. Pop a node, add it to the answer, and **reduce** the in-degree of its neighbours. Any neighbour
   reaching 0 joins the queue.
4. If the answer has all `n` nodes, it is a valid order. If not, there is a **cycle**.

```python
from collections import deque, defaultdict

def course_order(n, prereqs):                 # prereqs: (course, needs_first)
    graph, indeg = defaultdict(list), [0] * n
    for course, first in prereqs:
        graph[first].append(course)
        indeg[course] += 1
    q = deque(i for i in range(n) if indeg[i] == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in graph[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == n else []   # [] means a cycle

print(course_order(4, [(1, 0), (2, 0), (3, 1), (3, 2)]))
print(course_order(2, [(0, 1), (1, 0)]))
```

**Output:**

```text
[0, 1, 2, 3]
[]
```

Time **O(V + E)**.

## Union-Find (disjoint set)

Keeps **groups** and answers "are these two in the same group?" and "merge these two groups" in
almost **O(1)**. Each group has a **leader**; `find(x)` walks up to the leader.

```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]   # path compression
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False               # already connected: this edge makes a cycle
        self.parent[ra] = rb
        return True

d = DSU(5)
print([d.union(a, b) for a, b in [(0, 1), (1, 2), (0, 2), (3, 4)]])
```

**Output:**

```text
[True, True, False, True]
```

The third edge `(0, 2)` returns `False`: 0 and 2 were already connected through 1. This is how you
detect a **redundant connection** or count **connected components**.

## Weighted shortest path: Dijkstra

When edges have different costs, BFS fails. Use a **min-heap** of `(distance, node)`: always expand the
nearest unfinished node. (Only valid for **non-negative** weights.)

```python
import heapq

def dijkstra(graph, src):                      # graph[u] = [(v, weight), ...]
    dist = {src: 0}
    heap = [(0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, float("inf")):
            continue                           # a stale entry
        for v, w in graph.get(u, []):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist

g = {"A": [("B", 4), ("C", 1)], "C": [("B", 2), ("D", 7)], "B": [("D", 1)]}
print(dijkstra(g, "A"))
```

**Output:**

```text
{'A': 0, 'B': 3, 'C': 1, 'D': 4}
```

Time **O((V + E) log V)**.

## Which tool?

| question | tool |
|---|---|
| fewest edges between two nodes | BFS |
| is everything connected / count groups / islands | DFS, BFS or union-find |
| order with prerequisites / does a cycle exist (directed) | topological sort |
| cheapest path with weights | Dijkstra |
| redundant edge / merge accounts | union-find |

## Common mistakes

:::{warning}
- **Directed vs undirected**: forgetting to add the edge in both directions (or adding both for a directed graph).
- **Starting from one node** in a **disconnected** graph. Loop over all nodes.
- **Dijkstra with negative edges** gives wrong answers (use Bellman-Ford).
- **Not checking `len(order) == n`** in topological sort: that is how you detect a cycle.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Number of Provinces](https://leetcode.com/problems/number-of-provinces/) | Medium | components |
| [Course Schedule](https://leetcode.com/problems/course-schedule/) | Medium | cycle = impossible |
| [Course Schedule II](https://leetcode.com/problems/course-schedule-ii/) | Medium | return the order |
| [Redundant Connection](https://leetcode.com/problems/redundant-connection/) | Medium | union-find |
| [Network Delay Time](https://leetcode.com/problems/network-delay-time/) | Medium | Dijkstra |
| [Alien Dictionary](https://leetcode.com/problems/alien-dictionary/) | Hard | build edges from word pairs |

```{raw} html
<p><a class="reference external" href="/prep/#pattern=graphs"><strong>Open the Graph problems in the tracker →</strong></a></p>
```
