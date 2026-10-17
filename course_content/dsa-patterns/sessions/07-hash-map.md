# Session 7 · Hash Map

## The big idea

At a cinema cloakroom you hand over your coat and get a **numbered ticket**. Later you show the
ticket and the attendant walks **straight to your coat**: no searching through every hook.

A **hash map** (a Python `dict`) is that ticket desk for your data. You give it a **key**, it returns
the **value** in (almost always) one step. In interviews it is the tool that turns "search the whole
list again and again" (**O(n²)**) into "ask the map" (**O(n)**).

:::{admonition} In plain words
:class: tip
Spend a little memory to **remember what you have already seen**, so you never search for it again.

**Reach for it when:**

- the question is "**have I seen this before?**" or "is there a **partner** for this value?"
- you need to **count** things (frequency)
- you must **group** items that share something (anagrams)
:::

## The picture

```{raw} html
:file: ../diagrams/hash-map.html
```

## Pattern 1 · Look for a partner (Two Sum)

*Given `nums` and a target, return the indexes of the two numbers that add up to it.*

Brute force checks every pair (O(n²)). With a map: for each `x`, ask "have I already seen
`target − x`?" and remember `x` for later numbers.

```python
def two_sum(nums, target):
    seen = {}                          # value -> index
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return [seen[need], i]
        seen[x] = i                    # store AFTER checking, so x can't pair with itself
    return []

print(two_sum([2, 7, 11, 15], 9))
```

**Output:**

```text
[0, 1]
```

## Pattern 2 · Count things

```python
from collections import Counter

def is_anagram(a, b):
    return Counter(a) == Counter(b)

def top_frequent(nums, k):
    return [x for x, _ in Counter(nums).most_common(k)]

print(is_anagram("listen", "silent"), top_frequent([1, 1, 1, 2, 2, 3], 2))
```

**Output:**

```text
True [1, 2]
```

## Pattern 3 · Group by a signature

All words that are anagrams of each other have the same **sorted letters**. Use that as the key.

```python
from collections import defaultdict

def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        groups["".join(sorted(w))].append(w)
    return list(groups.values())

print(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))
```

**Output:**

```text
[['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
```

## Pattern 4 · Prefix state + map

Combine a running value with a map to find a **subarray**: this is the prefix-sum trick of session 6.
Another example is the *longest consecutive sequence*: put all numbers in a **set**, and only start
counting from numbers that have no left neighbour.

```python
def longest_consecutive(nums):
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:             # x is the start of a run
            y = x
            while y + 1 in s:
                y += 1
            best = max(best, y - x + 1)
    return best

print(longest_consecutive([100, 4, 200, 1, 3, 2]))
```

**Output:**

```text
4
```

Each number is visited at most twice, so the time is **O(n)**.

## How fast is a hash map, really?

| operation | average | worst |
|---|---|---|
| insert / lookup / delete | **O(1)** | O(n) (many collisions, very rare) |
| memory | O(n) | |

The map computes `hash(key)` to find a **bucket**. Two different keys may land in the same bucket
(a *collision*); Python handles this internally, so you can treat each operation as O(1).

## Common mistakes

:::{warning}
- **Using a list as a key.** Lists are mutable and unhashable. Use a `tuple`.
- **Inserting before checking** in Two Sum: `target = 6, nums = [3]` would wrongly pair 3 with itself.
- **Forgetting `get(key, 0)`** when counting, which raises `KeyError`. `Counter` and `defaultdict` avoid it.
- **Thinking order matters.** Iterating a `set` gives no guaranteed order of meaning for the problem.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Two Sum](https://leetcode.com/problems/two-sum/) | Easy | partner lookup |
| [Valid Anagram](https://leetcode.com/problems/valid-anagram/) | Easy | counting |
| [Group Anagrams](https://leetcode.com/problems/group-anagrams/) | Medium | signature as key |
| [Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) | Medium | count, then heap or bucket |
| [Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/) | Medium | set + run starts |
| [Contains Duplicate](https://leetcode.com/problems/contains-duplicate/) | Easy | set |

```{raw} html
<p><a class="reference external" href="/prep/#pattern=hash-map"><strong>Open the Hash Map problems in the tracker →</strong></a></p>
```
