# Session 11 · Matrix Manipulation

## The big idea

A chocolate bar is a **grid of squares**. Two things you may want to do with it:

- **Eat it in a spiral:** along the top row, down the right edge, back along the bottom, up the left
  edge, and then do the same on the smaller bar that is left.
- **Turn a photo by 90°:** instead of making a new photo, you can first **flip it over its diagonal**
  (rows become columns), then **mirror each row**.

Matrix problems look scary, but they are all about keeping **four boundaries** straight, or knowing
one or two index tricks.

:::{admonition} In plain words
:class: tip
Treat a matrix as **layers** (rings) or as **rows and columns you can swap**. Keep `top, bottom, left,
right` boundaries and shrink them, or use transpose + reverse.

**Reach for it when:**

- "spiral order", "rotate image", "set matrix zeroes", "search a 2D matrix"
- you must modify the matrix **in place** (O(1) extra space)
:::

## The picture

```{raw} html
:file: ../diagrams/matrix.html
```

## Spiral order

Four boundaries shrink after each side is walked.

```python
def spiral(m):
    out = []
    top, bottom, left, right = 0, len(m) - 1, 0, len(m[0]) - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):           # → along the top
            out.append(m[top][c])
        top += 1
        for r in range(top, bottom + 1):           # ↓ down the right
            out.append(m[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):   # ← along the bottom
                out.append(m[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):   # ↑ up the left
                out.append(m[r][left])
            left += 1
    return out

print(spiral([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
```

**Output:**

```text
[1, 2, 3, 6, 9, 8, 7, 4, 5]
```

The two `if` checks stop the walk from going over a single row or single column twice. Time **O(m·n)**.

## Rotate image 90° clockwise, in place

Two steps: **transpose** (swap `m[i][j]` with `m[j][i]`), then **reverse every row**.

```python
def rotate(m):
    n = len(m)
    for i in range(n):
        for j in range(i + 1, n):
            m[i][j], m[j][i] = m[j][i], m[i][j]
    for row in m:
        row.reverse()
    return m

print(rotate([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
```

**Output:**

```text
[[7, 4, 1], [8, 5, 2], [9, 6, 3]]
```

For **counter-clockwise**, transpose and then reverse the **columns** (or reverse the rows first, then transpose).

## Set matrix zeroes in O(1) space

If a cell is 0, its whole row and column become 0. Using extra arrays costs O(m+n). The trick is to
**store the flags inside the matrix itself**: use the first row and the first column as markers.

1. Remember separately whether the first row / first column already contained a 0.
2. For every other cell that is 0, mark `m[i][0] = 0` and `m[0][j] = 0`.
3. Zero all inner cells whose row marker or column marker is 0.
4. Finally zero the first row / first column if step 1 said so.

## Useful index tricks

| idea | formula |
|---|---|
| the 4 neighbours of `(r, c)` | `(r±1, c)`, `(r, c±1)` via `dirs = [(1,0),(-1,0),(0,1),(0,-1)]` |
| flatten a cell to a number | `id = r * cols + c` and back: `r, c = divmod(id, cols)` |
| diagonals | cells on the same `\` diagonal share `r - c`; on the same `/` diagonal share `r + c` |
| staying inside the grid | `0 <= r < rows and 0 <= c < cols` |

## Common mistakes

:::{warning}
- **Walking the middle row or column twice** in a spiral (forgetting the two `if` guards).
- **Overwriting a value you still need** while rotating in place.
- **Swapping both `m[i][j]` and `m[j][i]` for all `j`** in the transpose (you undo the work). Use `j > i`.
- **Mixing up `rows` and `cols`** for non-square matrices.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Spiral Matrix](https://leetcode.com/problems/spiral-matrix/) | Medium | four boundaries |
| [Rotate Image](https://leetcode.com/problems/rotate-image/) | Medium | transpose + reverse |
| [Set Matrix Zeroes](https://leetcode.com/problems/set-matrix-zeroes/) | Medium | markers in the first row/column |
| [Search a 2D Matrix](https://leetcode.com/problems/search-a-2d-matrix/) | Medium | binary search on `r*cols + c` |
| [Diagonal Traverse](https://leetcode.com/problems/diagonal-traverse/) | Medium | `r + c` groups |
| [Game of Life](https://leetcode.com/problems/game-of-life/) | Medium | encode old and new state in one cell |

```{raw} html
<p><a class="reference external" href="/prep/#pattern=matrix-manipulation"><strong>Open the Matrix Manipulation problems in the tracker →</strong></a></p>
```
