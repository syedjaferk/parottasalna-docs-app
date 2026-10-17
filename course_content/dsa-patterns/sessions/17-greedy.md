# Session 17 · Greedy

## The big idea

You must pay **63 rupees** and want to use as **few coins** as possible. You have coins of 1, 2, 5, 10,
20 and 50. What do you do? You grab the **biggest coin that still fits** (50), then again (10), then 2,
then 1: `50 + 10 + 2 + 1`. You never take a coin back.

That is **greedy**: at every step, take the **best-looking choice right now** and never reconsider it.
It is fast and simple, but it only works when **a locally best choice can never ruin the global answer**.
(With coins of 1, 3, 4 and a target of 6, greedy picks `4 + 1 + 1` = 3 coins, but `3 + 3` = 2 coins is
better. So greedy fails there and you need dynamic programming.)

:::{admonition} In plain words
:class: tip
1. Find a **rule** for "the best choice now" (earliest finish, largest ratio, smallest gap).
2. Often **sort** (or use a heap) so the best choice is always next.
3. Take it if allowed, update the state, repeat.
4. **Convince yourself** the rule is safe: try to find a counter-example, or argue that swapping any
   other choice for yours never makes things worse (the *exchange argument*).

**Reach for it when:** the problem asks for a min/max/count, choices look "independent", and a sort makes the
decision obvious: interval scheduling, jump game, gas station, assigning cookies, task scheduling.
:::

## The picture

```{raw} html
:file: ../diagrams/greedy.html
```

**Why earliest end time?** The activity that finishes first leaves the **most room** for the others. Any
solution that starts with a later-ending activity can swap it for the earliest-ending one without
losing anything.

## Example 1 · Maximum activities (interval scheduling)

```python
def max_activities(intervals):
    intervals.sort(key=lambda x: x[1])       # earliest end first
    count, last_end = 0, float("-inf")
    for s, e in intervals:
        if s >= last_end:                    # fits after the last chosen one
            count += 1
            last_end = e
    return count

print(max_activities([(1, 3), (2, 5), (4, 6), (6, 9), (5, 8)]))
```

**Output:**

```text
3
```

The same idea gives **non-overlapping intervals**: the minimum removals = `n − max_activities`.

## Example 2 · Jump game

Each number is the maximum jump length from that position. Can you reach the last index? Track the
**furthest index you can reach**. If you ever stand on a position beyond it, you are stuck.

```python
def can_jump(nums):
    reach = 0
    for i, jump in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + jump)
    return True

print(can_jump([2, 3, 1, 1, 4]), can_jump([3, 2, 1, 0, 4]))
```

**Output:**

```text
True False
```

## Example 3 · Gas station

`gas[i]` is fuel you gain at station `i`, `cost[i]` is the fuel to reach the next one. Find a start from
which you can complete the circle. If the **total** gas is at least the total cost, an answer exists, and
it starts right after the point where the running tank was the lowest, so reset the start whenever the tank goes negative.

```python
def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    tank = start = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:               # can't get here from `start`: restart after i
            start, tank = i + 1, 0
    return start

print(can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]))
```

**Output:**

```text
3
```

## Example 4 · Task scheduler with a heap

Many greedy problems need "the best item right now" from a **changing** set: a **heap** (session 20)
supplies it. *Connect ropes with minimum cost*: always join the two **shortest** ropes.

```python
import heapq

def connect_ropes(ropes):
    heapq.heapify(ropes)
    cost = 0
    while len(ropes) > 1:
        a, b = heapq.heappop(ropes), heapq.heappop(ropes)
        cost += a + b
        heapq.heappush(ropes, a + b)
    return cost

print(connect_ropes([4, 3, 2, 6]))
```

**Output:**

```text
29
```

## Greedy or dynamic programming?

| signal | likely |
|---|---|
| a simple local rule + a sort, and you can argue it | **greedy** |
| a counter-example appears for the rule (like coins 1, 3, 4) | **dynamic programming** |
| "count the number of ways" | **dynamic programming** (greedy cannot count) |
| need *every* valid answer | **backtracking** |

## Common mistakes

:::{warning}
- **Assuming greedy works without checking.** Always try a small counter-example, or find the exchange argument.
- **Sorting by the wrong key** (start vs end time, ratio vs value).
- **Ties:** decide a second sorting key if two items look equal.
- **Using greedy for 0/1 knapsack or coin change with odd coins**: those need DP.
:::

## Practice

| Problem | Level | What to notice |
|---|---|---|
| [Assign Cookies](https://leetcode.com/problems/assign-cookies/) | Easy | sort both, two pointers |
| [Jump Game](https://leetcode.com/problems/jump-game/) | Medium | furthest reach |
| [Gas Station](https://leetcode.com/problems/gas-station/) | Medium | reset start |
| [Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/) | Medium | earliest end |
| [Partition Labels](https://leetcode.com/problems/partition-labels/) | Medium | last index of each letter |
| [Task Scheduler](https://leetcode.com/problems/task-scheduler/) | Medium | most frequent task decides |

```{raw} html
<p><a class="reference external" href="/prep/#pattern=greedy"><strong>Open the Greedy problems in the tracker →</strong></a></p>
```
