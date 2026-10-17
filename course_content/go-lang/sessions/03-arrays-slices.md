# Session 3 · Arrays and slices

## The big idea

You often need an ordered list of things. Go gives you two: the **array**, which has a fixed size
that is part of its type, and the **slice**, a flexible window onto an array that can grow. In
real Go code you will use slices about 99 % of the time. You still need to understand arrays,
because slices are built on top of them.

**Everyday example:** an egg carton versus a window. The carton holds exactly 12 eggs; that is an
array. A slice is like a window cut into the carton wall: it shows eggs 3 to 6 and nothing else,
and if someone moves an egg you see the change too, because the window and the carton are the same
eggs.

:::{admonition} In plain words
:class: tip
`[3]int` is a fixed row of three ints. `[]int` is a slice: a length, a capacity and a pointer to
an array underneath. `append` adds to a slice and may move it to a bigger array.

**Reach for it when:**

- you have a list whose size changes: use a slice
- you have a fixed, tiny shape such as `[2]int` coordinates: an array is fine
- you want to share or cut up data without copying: slice it, but remember the sharing
:::

## Arrays

`arrays.go`

```{literalinclude} ../code/03-slices/arrays.go
:language: go
```

```{literalinclude} ../code/03-slices/arrays.out
:language: text
```

The size is part of the type, so `[3]int` and `[4]int` are different types. Assigning an array
**copies** it, which is why `b[0] = 99` left `a` alone. `[...]string{...}` lets the compiler count.

## Slices

`slices.go`

```{literalinclude} ../code/03-slices/slices.go
:language: go
```

```{literalinclude} ../code/03-slices/slices.out
:language: text
```

```{raw} html
:file: ../diagrams/slice-header.html
```

- `len` is how many elements you can see; `cap` is how many fit before Go must find a bigger array.
- `s[1:3]` includes index 1 and **stops before** 3.
- A sub-slice **shares** the same array. Writing through `window` changed `s`.
- `copy(dst, src)` makes an independent copy. `append(s[:1], s[2:]...)` deletes one element.
- `make([]int, 2, 10)` makes a slice with length 2 and room for 10.

## How a slice grows

`growth.go` prints every time the capacity changes while we append 20 numbers.

```{literalinclude} ../code/03-slices/growth.go
:language: go
```

```{literalinclude} ../code/03-slices/growth.out
:language: text
```

Go doubles the capacity as the slice grows, so adding items stays cheap. The exact numbers depend
on the Go version, so never rely on them; rely on `len`.

## Common mistakes

- **Always using the return value of `append`.** Writing `append(s, 1)` on its own line does
  nothing useful. Write `s = append(s, 1)`.
- **Surprise sharing.** Two slices of one array change together. Use `copy` when you need your own
  data.
- **Index out of range.** `s[5]` on a 3-element slice panics. Check `len(s)` first.
- **Using an array when you wanted a slice.** Arrays are copied on every function call, which is
  slow for big ones and does not let the function change your data.
- **`for i, v := range s` and changing `v`.** `v` is a copy of the element. Change `s[i]`.

## Hands-on exercises

**Exercise 1 · Reverse.** Write `reverse(s []int)` that reverses a slice in place.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

func reverse(s []int) {
	for i, j := 0, len(s)-1; i < j; i, j = i+1, j-1 {
		s[i], s[j] = s[j], s[i]
	}
}

func main() {
	nums := []int{1, 2, 3, 4, 5}
	reverse(nums)
	fmt.Println(nums)
}
```

```text
[5 4 3 2 1]
```

Because a slice shares its array, the function changes the caller's data without returning anything.

</details>

**Exercise 2 · Filter.** Write `evens(nums []int) []int` that returns only the even numbers.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

func evens(nums []int) []int {
	var out []int
	for _, n := range nums {
		if n%2 == 0 {
			out = append(out, n)
		}
	}
	return out
}

func main() {
	fmt.Println(evens([]int{1, 2, 3, 4, 5, 6}))
	fmt.Println(evens([]int{1, 3}) == nil)
}
```

```text
[2 4 6]
true
```

A `nil` slice is a perfectly good empty slice: you can `append` to it and loop over it.

</details>

**Exercise 3 · Break the sharing.** Make `b` a slice with the same numbers as `a` but changing `b[0]`
must not change `a`.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

func main() {
	a := []int{1, 2, 3}
	b := make([]int, len(a))
	copy(b, a)
	b[0] = 100
	fmt.Println(a, b)
}
```

```text
[1 2 3] [100 2 3]
```

</details>
