# Session 4 · Maps

## The big idea

A **map** stores pairs: look something up by a *key* and get its *value*. It answers "what is the
age of Jafer?" instantly, however many people are stored, without scanning a list.

**Everyday example:** a phone's contact list. You type a name and get a number. You do not read
every contact from the top.

:::{admonition} In plain words
:class: tip
`map[string]int` maps text keys to int values. Reading a key that is not there gives the zero value
(so you cannot tell "missing" from "zero"), unless you ask for the second result: `v, ok := m[k]`.

**Reach for it when:**

- you look things up by name or id (users by id, counts per word)
- you want to count or group things
- you need "have I seen this before?" (a map used as a set)
:::

```{raw} html
:file: ../diagrams/map-lookup.html
```

## The basics

`maps.go`

```{literalinclude} ../code/04-maps/maps.go
:language: go
```

```{literalinclude} ../code/04-maps/maps.out
:language: text
```

- Make one with `make(map[K]V)` or a literal `map[string]int{"a": 1}`.
- `v, ok := m[key]` is the **comma-ok** idiom. `ok` is `true` only if the key exists.
- `delete(m, key)` removes a key and does nothing if it is absent.
- **Iteration order is random on purpose.** To print in order, collect and sort the keys.
- Keys must be comparable: strings, numbers, bools, arrays and structs of those work; slices do not.

## Maps are shared, not copied

`references.go`

```{literalinclude} ../code/04-maps/references.go
:language: go
```

```{literalinclude} ../code/04-maps/references.out
:language: text
```

`m2 := m1` copies the *reference*, so both names edit the same map. A `nil` map can be read but
writing to it panics: always create it with `make` or a literal.

## Worked example: expense tracker

The original course builds an expense tracker with a map of ids to expenses. With a `struct` as the
value it becomes safer than a map of `interface{}`.

```{literalinclude} ../code/04-maps/expenses.go
:language: go
```

```{literalinclude} ../code/04-maps/expenses.out
:language: text
```

Notice `update`: `expenses[id]` returns a **copy** of the struct, so changing `e.Amount` is not
enough. You must store `e` back with `expenses[id] = e`.

## Common mistakes

- **Writing to a nil map.** `var m map[string]int; m["a"] = 1` panics. Use `make`.
- **Depending on iteration order.** It changes from run to run.
- **Reading a missing key and believing it.** `ages["x"]` is `0`, not an error. Use comma-ok.
- **Editing a struct value in the map directly.** `m[k].Field = 1` will not compile; copy, change, store back (or store pointers).
- **Sharing a map between goroutines without a lock.** Maps are not safe for concurrent writes (Session 16).

## Hands-on exercises

**Exercise 1 · Word counter.** Count how many times each word appears in `"to be or not to be"` and
print them sorted by word.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"sort"
	"strings"
)

func main() {
	counts := map[string]int{}
	for _, w := range strings.Fields("to be or not to be") {
		counts[w]++
	}
	words := make([]string, 0, len(counts))
	for w := range counts {
		words = append(words, w)
	}
	sort.Strings(words)
	for _, w := range words {
		fmt.Println(w, counts[w])
	}
}
```

```text
be 2
not 1
or 1
to 2
```

`counts[w]++` works even for a new word, because the missing key reads as `0`.

</details>

**Exercise 2 · Set of unique numbers.** Remove duplicates from `[3 1 3 2 1]` keeping first-seen order.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

func main() {
	input := []int{3, 1, 3, 2, 1}
	seen := map[int]bool{}
	var unique []int
	for _, n := range input {
		if !seen[n] {
			seen[n] = true
			unique = append(unique, n)
		}
	}
	fmt.Println(unique)
}
```

```text
[3 1 2]
```

`map[T]bool` is Go's everyday set.

</details>

**Exercise 3 · Group by length.** Group `["go", "is", "fun", "and", "fast"]` into a
`map[int][]string` by word length.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

func main() {
	groups := map[int][]string{}
	for _, w := range []string{"go", "is", "fun", "and", "fast"} {
		groups[len(w)] = append(groups[len(w)], w)
	}
	fmt.Println(groups) // fmt prints maps with sorted keys
}
```

```text
map[2:[go is] 3:[fun and] 4:[fast]]
```

`append` on a missing key starts from a `nil` slice, which is fine.

</details>
