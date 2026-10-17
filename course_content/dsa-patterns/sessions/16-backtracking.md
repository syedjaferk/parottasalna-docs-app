# Session 16 · Backtracking

## The big idea

You are choosing an **outfit**: a shirt, then trousers, then shoes. You put on the shirt, then the
trousers, then the shoes. The shoes clash! You don't throw away the whole outfit and start over. You
**take the shoes off** and try other shoes. If none work, you take the trousers off and try different
trousers.

**Choose → explore → un-choose.** Try something, see where it leads, and **undo it** so you can try the
next option. Backtracking is just a careful, organised **try-everything** that stops early when a
choice can't possibly work.

:::{admonition} In plain words
:class: tip
Build the answer **one decision at a time**. After each decision, recurse. When the recursion returns,
**undo** the decision (`pop`) and try the next one. Add **pruning**: stop as soon as a partial answer
is already invalid.

**Reach for it when:**

- "generate **all** subsets / permutations / combinations / arrangements"
- "find **all** valid ways" (N-Queens, Sudoku, word search, parentheses)
- n is small (up to about 15–20): the answer count is exponential
:::

## The picture

```{raw} html
:file: ../diagrams/backtracking.html
```

Each level of the tree is **one decision**; each leaf is a complete answer.

## The universal template

```python
def backtrack(state):
    if is_complete(state):
        answers.append(copy_of(state))       # copy! the state keeps changing
        return
    for choice in choices(state):
        if not is_valid(state, choice):      # pruning
            continue
        make(state, choice)                  # 1. choose
        backtrack(state)                     # 2. explore
        undo(state, choice)                  # 3. un-choose
```

## Subsets

For each number: add it to the current path, recurse on the numbers after it, then pop.

```python
def subsets(nums):
    out = []

    def go(start, path):
        out.append(path[:])                  # every path is a valid subset
        for i in range(start, len(nums)):
            path.append(nums[i])             # choose
            go(i + 1, path)                  # explore (only numbers to the right)
            path.pop()                       # un-choose

    go(0, [])
    return out

print(subsets([1, 2, 3]))
```

**Output:**

```text
[[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
```

## Permutations

Every arrangement. Track which items are already used.

```python
def permutations(nums):
    out, used, path = [], [False] * len(nums), []

    def go():
        if len(path) == len(nums):
            out.append(path[:])
            return
        for i, x in enumerate(nums):
            if used[i]:
                continue
            used[i] = True; path.append(x)
            go()
            path.pop(); used[i] = False

    go()
    return out

print(permutations([1, 2, 3]))
```

**Output:**

```text
[[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
```

## Combination sum (with pruning)

Pick numbers (reusing allowed) that add up to the target. **Prune** when the running sum exceeds the
target; sorting makes the pruning stop the loop early.

```python
def combination_sum(candidates, target):
    candidates.sort()
    out = []

    def go(start, path, remain):
        if remain == 0:
            out.append(path[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remain:
                break                        # prune: all later numbers are bigger
            path.append(candidates[i])
            go(i, path, remain - candidates[i])      # i, not i+1: reuse allowed
            path.pop()

    go(0, [], target)
    return out

print(combination_sum([2, 3, 6, 7], 7))
```

**Output:**

```text
[[2, 2, 3], [7]]
```

## Grid example: word search

At each cell, try the four neighbours; mark the cell as used on the way in and **restore it on the way out**.

```python
def exist(board, word):
    R, C = len(board), len(board[0])

    def go(r, c, i):
        if i == len(word):
            return True
        if not (0 <= r < R and 0 <= c < C) or board[r][c] != word[i]:
            return False
        keep, board[r][c] = board[r][c], "#"          # choose (mark)
        found = any(go(r + dr, c + dc, i + 1) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        board[r][c] = keep                             # un-choose
        return found

    return any(go(r, c, 0) for r in range(R) for c in range(C))

b = [list("ABCE"), list("SFCS"), list("ADEE")]
print(exist(b, "ABCCED"), exist(b, "ABCB"))
```

**Output:**

```text
True False
```

## Complexity

Backtracking is exponential: subsets **O(2ⁿ · n)**, permutations **O(n! · n)**. Pruning does not change
the worst case but often makes it fast in practice. If the same sub-problem repeats, switch to
**dynamic programming** (session 18).

## Common mistakes

:::{warning}
- **Appending `path` itself** instead of a **copy** (`path[:]`): all answers end up equal to the final, empty path.
- **Forgetting to undo** (`pop`, un-mark): earlier choices leak into later branches.
- **Duplicates in the input:** sort and skip `if i > start and nums[i] == nums[i-1]` to avoid duplicate answers.
- **No pruning**, so it times out on inputs it could handle.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Subsets](https://leetcode.com/problems/subsets/) | Medium | the template |
| [Permutations](https://leetcode.com/problems/permutations/) | Medium | `used` array |
| [Combination Sum](https://leetcode.com/problems/combination-sum/) | Medium | reuse + prune |
| [Generate Parentheses](https://leetcode.com/problems/generate-parentheses/) | Medium | only add valid characters |
| [Word Search](https://leetcode.com/problems/word-search/) | Medium | mark and restore |
| [N-Queens](https://leetcode.com/problems/n-queens/) | Hard | column / diagonal sets |

```{raw} html
<p><a class="reference external" href="/prep/#pattern=backtracking"><strong>Open the Backtracking problems in the tracker →</strong></a></p>
```
