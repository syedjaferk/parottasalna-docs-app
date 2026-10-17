# Session 9 · Overlapping Intervals

## The big idea

Every child has a **play slot**: Asha 1pm–3pm, Ravi 2pm–6pm, Mei 8pm–10pm. If you write the slots on a
timeline, some bars **overlap** (Asha and Ravi share 2pm–3pm) and some stand alone (Mei).

To tidy the timeline you first **line the children up by start time**. Then you walk along: if the next
child starts **before the current slot ends**, the two slots overlap, so you **stretch** the current
slot to cover both. Otherwise you begin a new slot.

:::{admonition} In plain words
:class: tip
**Sort by start.** Then compare each interval with the last one you kept. Overlap ⇔ `start ≤ last_end`.

**Reach for it when:**

- the input is a list of `[start, end]` pairs (meetings, bookings, ranges)
- you merge, insert, or count overlaps, or find free gaps
- the problem asks for the **minimum number of rooms / platforms / arrows**
:::

## The picture

```{raw} html
:file: ../diagrams/intervals.html
```

## Three ways two intervals `a` and `b` (with `a.start ≤ b.start`) can relate

| picture | condition | merge result |
|---|---|---|
| `a` ends before `b` starts | `a.end < b.start` | separate |
| they overlap | `b.start ≤ a.end` | `[a.start, max(a.end, b.end)]` |
| `a` fully contains `b` | `b.end ≤ a.end` | `a` (still `max` handles it) |

The `max` is the important part: `[1, 10]` and `[2, 3]` must merge to `[1, 10]`, not `[1, 3]`.

## Merge intervals

```python
def merge(intervals):
    intervals.sort(key=lambda x: x[0])
    out = [intervals[0]]
    for start, end in intervals[1:]:
        last = out[-1]
        if start <= last[1]:                 # overlap
            last[1] = max(last[1], end)
        else:
            out.append([start, end])
    return out

print(merge([[1, 3], [8, 10], [2, 6], [15, 18]]))
```

**Output:**

```text
[[1, 6], [8, 10], [15, 18]]
```

Time **O(n log n)** (the sort), space O(n).

## Insert an interval into a sorted list

Three phases: copy everything that ends **before** the new one, **merge** everything that overlaps it,
copy the rest.

```python
def insert(intervals, new):
    out, i, n = [], 0, len(intervals)
    while i < n and intervals[i][1] < new[0]:          # entirely before
        out.append(intervals[i]); i += 1
    while i < n and intervals[i][0] <= new[1]:         # overlapping: grow `new`
        new = [min(new[0], intervals[i][0]), max(new[1], intervals[i][1])]
        i += 1
    out.append(new)
    out.extend(intervals[i:])                          # entirely after
    return out

print(insert([[1, 3], [6, 9]], [2, 5]))
```

**Output:**

```text
[[1, 5], [6, 9]]
```

## Counting how many meetings overlap at once (meeting rooms II)

Sort the **starts** and the **ends** separately. Walk through the starts: if the next start is before
the earliest unfinished end, we need a new room; otherwise a room frees up and is reused.

```python
def min_rooms(intervals):
    starts = sorted(s for s, _ in intervals)
    ends = sorted(e for _, e in intervals)
    rooms = j = 0
    for s in starts:
        if s < ends[j]:
            rooms += 1          # nobody has left yet: new room
        else:
            j += 1              # someone left: reuse their room
    return rooms

print(min_rooms([[0, 30], [5, 10], [15, 20]]))
```

**Output:**

```text
2
```

(A min-heap of end times gives the same answer; see session 20.)

## Common mistakes

:::{warning}
- **Not sorting first.** The whole algorithm depends on the order.
- **Using `last_end = end` instead of `max(last_end, end)`.**
- **`<` vs `<=`:** do intervals that only touch (`[1,2]` and `[2,3]`) count as overlapping? Read the problem and decide.
- **Mutating the input** when the caller does not expect it. Copy when needed.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Merge Intervals](https://leetcode.com/problems/merge-intervals/) | Medium | sort + merge |
| [Insert Interval](https://leetcode.com/problems/insert-interval/) | Medium | three phases |
| [Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/) | Medium | greedy by end time (session 17) |
| [Meeting Rooms](https://leetcode.com/problems/meeting-rooms/) | Easy | any overlap? |
| [Meeting Rooms II](https://leetcode.com/problems/meeting-rooms-ii/) | Medium | how many at once |
| [Interval List Intersections](https://leetcode.com/problems/interval-list-intersections/) | Medium | two pointers over two lists |

```{raw} html
<p><a class="reference external" href="/prep/#pattern=overlapping-intervals"><strong>Open the Overlapping Intervals problems in the tracker →</strong></a></p>
```
