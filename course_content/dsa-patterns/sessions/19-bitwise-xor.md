# Session 19 · Bitwise XOR

## The big idea

Think of a **light switch**. Flip it once: the light is on. Flip it again: off. **Flipping twice puts
things back exactly as they were.**

XOR (`^`) is that switch for bits. Suppose a room full of children each flips the same switch once,
but every child except one has a **twin** who flips it too. All the twins cancel each other out, and
the switch ends up showing only the effect of the **one child without a twin**.

Two facts do all the work:

- `a ^ a = 0`: a number XOR itself disappears.
- `a ^ 0 = a`: XOR with zero changes nothing.

And XOR doesn't care about **order** (`a ^ b ^ a = b`).

:::{admonition} In plain words
:class: tip
XOR all the numbers together: **pairs cancel, the odd one out remains**, in **O(n) time and O(1) space**.
XOR also lets you flip, test and clear single **bits**.

**Reach for it when:**

- "every number appears twice **except one**"
- "find the **missing** number" in 0..n
- you need to **swap, toggle or count bits**, or check powers of two
:::

## The picture

```{raw} html
:file: ../diagrams/xor.html
```

## The truth table

| a | b | a ^ b |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

Output is `1` when the bits are **different**.

## Single number

```python
def single_number(nums):
    result = 0
    for x in nums:
        result ^= x
    return result

print(single_number([4, 1, 2, 1, 2]))
```

**Output:**

```text
4
```

## Missing number

XOR the indexes `0..n` with the values. Everything that is present cancels; the missing one remains.

```python
def missing_number(nums):
    x = len(nums)
    for i, v in enumerate(nums):
        x ^= i ^ v
    return x

print(missing_number([3, 0, 1]))
```

**Output:**

```text
2
```

## Two singles (everyone else appears twice)

XOR of all numbers is `a ^ b` (the two singles). Since `a ≠ b`, at least one bit differs. Use that bit
to **split the numbers into two groups**, each containing one single and complete pairs. XOR each group.

```python
def two_singles(nums):
    xor_all = 0
    for x in nums:
        xor_all ^= x
    bit = xor_all & -xor_all                # the lowest set bit: a place where a and b differ
    a = b = 0
    for x in nums:
        if x & bit:
            a ^= x
        else:
            b ^= x
    return sorted([a, b])

print(two_singles([1, 2, 1, 3, 2, 5]))
```

**Output:**

```text
[3, 5]
```

## Handy bit tricks

| goal | expression |
|---|---|
| is bit `k` set? | `(n >> k) & 1` |
| set / clear / flip bit `k` | `n \| (1 << k)`, `n & ~(1 << k)`, `n ^ (1 << k)` |
| clear the lowest set bit | `n & (n - 1)` |
| isolate the lowest set bit | `n & -n` |
| is `n` a power of two? | `n > 0 and n & (n - 1) == 0` |
| swap without a temp | `a ^= b; b ^= a; a ^= b` |

```python
def count_bits(n):
    count = 0
    while n:
        n &= n - 1                 # remove the lowest set bit
        count += 1
    return count

print(count_bits(0b1011), 16 & 15 == 0)
```

**Output:**

```text
3 True
```

Brian Kernighan's loop runs once per **set** bit, not once per bit position.

## Common mistakes

:::{warning}
- **Operator precedence:** `n & 1 == 0` means `n & (1 == 0)`. Write `(n & 1) == 0`.
- **Negative numbers:** Python integers have unlimited width. Mask with `& 0xFFFFFFFF` when a problem assumes 32 bits.
- **Using XOR when a value appears three times** (or any odd count other than 1 for the odd one): the cancel-out trick needs **pairs**.
- **Confusing `^` (XOR) with `**` (power).**
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Single Number](https://leetcode.com/problems/single-number/) | Easy | pairs cancel |
| [Missing Number](https://leetcode.com/problems/missing-number/) | Easy | XOR indexes with values |
| [Number of 1 Bits](https://leetcode.com/problems/number-of-1-bits/) | Easy | `n & (n - 1)` |
| [Power of Two](https://leetcode.com/problems/power-of-two/) | Easy | one bit set |
| [Single Number III](https://leetcode.com/problems/single-number-iii/) | Medium | split by a differing bit |
| [Counting Bits](https://leetcode.com/problems/counting-bits/) | Easy | `dp[i] = dp[i >> 1] + (i & 1)` |

```{raw} html
<p><a class="reference external" href="/prep/#pattern=bitwise-xor"><strong>Open the Bitwise XOR problems in the tracker →</strong></a></p>
```
