# DSA Patterns for Coding Interviews

Most coding-interview problems are not new. Behind the thousands of questions there are only a few
**patterns**: reusable ideas like "two pointers", "sliding window" or "BFS". Learn the pattern once
and you can solve every problem that wears it as a costume.

This course teaches **23 patterns**, one session each. Every session follows the same shape, so you
always know where to look.

:::{note}
**What is a pattern, in one line?** A named way of thinking that turns a slow brute-force idea into
a fast one. Knowing the name helps you *recognise* the problem in the first minute of an interview.
:::

## How each session works

1. **The big idea**: the pattern explained with an everyday story, the way you would explain it to a child.
2. **Spot it when…**: the clues in a problem statement that point to this pattern.
3. **The picture**: a diagram of the idea.
4. **Step by step**: a full trace on a small example, so you see every move.
5. **The template**: short Python code you can adapt.
6. **Worked example**, **variations**, **common mistakes**.
7. **Practice**: problems to solve, and a link to open them in the tracker.

:::{tip}
Do the sessions in order. They start with array tricks, move through linked lists, searching,
trees and graphs, then finish with recursion-heavy and heap-based patterns.
:::

```{raw} html
<p>Practise each pattern in the <a class="reference external" href="/prep/"><strong>Interview prep tracker</strong></a>:
open a sheet or a company list, filter by <em>Pattern</em>, tick problems off and keep notes.</p>
```

:::{important}
**Don't memorise code, memorise the picture.** If you can redraw the diagram and say the flow in
your own words, the code writes itself. Always check the complexity out loud in an interview.
:::

```{toctree}
:maxdepth: 1
:caption: Arrays and strings

sessions/01-two-pointers
sessions/02-sliding-window
sessions/06-prefix-sum
sessions/07-hash-map
sessions/10-cyclic-sort
sessions/11-matrix
```

```{toctree}
:maxdepth: 1
:caption: Linked lists and searching

sessions/03-fast-and-slow-pointers
sessions/04-reverse-linked-list
sessions/05-binary-search
sessions/08-monotonic-stack
sessions/09-overlapping-intervals
```

```{toctree}
:maxdepth: 1
:caption: Trees and graphs

sessions/12-bfs
sessions/13-dfs
sessions/14-trees
sessions/15-graphs
```

```{toctree}
:maxdepth: 1
:caption: Recursion and optimisation

sessions/16-backtracking
sessions/17-greedy
sessions/18-dynamic-programming
sessions/19-bitwise-xor
```

```{toctree}
:maxdepth: 1
:caption: Heaps and design

sessions/20-top-k-elements
sessions/21-k-way-merge
sessions/22-two-heaps
sessions/23-design-data-structures
```
