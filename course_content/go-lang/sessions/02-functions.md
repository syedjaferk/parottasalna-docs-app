# Session 2 · Functions, closures and defer

## The big idea

A function packages a few lines of code under a name so you can use it again. Go functions have two
habits that surprise people coming from other languages: they can **return more than one value**,
and they can **defer** a clean-up step so it runs no matter how the function ends.

**Everyday example:** a vending machine. You press a button (the call), it hands back your snack
*and* your change (two return values). Whatever happens inside, the machine always locks its door
again at the end (a deferred clean-up).

:::{admonition} In plain words
:class: tip
`func name(inputs) outputs { ... }`. Return several things at once, usually "the answer, and
whether it worked". Use `defer` right after you open something, so you cannot forget to close it.

**Reach for it when:**

- a function can fail and the caller must know (return a value and an `error` or `ok`)
- you want to run clean-up on every exit path
- you need a small piece of state hidden inside a function (a closure)
:::

## Functions

`funcs.go`: parameters, multiple results, named results and variadic arguments.

```{literalinclude} ../code/02-functions/funcs.go
:language: go
```

```{literalinclude} ../code/02-functions/funcs.out
:language: text
```

- Same-typed parameters can share a type: `a, b int`.
- `(float64, bool)` returns two values. The caller takes both, or ignores one with `_`.
- **Named results** (`min, max int`) are variables you can fill in; a bare `return` sends them back.
  Use them for short functions where the names document the result.
- `nums ...int` accepts any number of ints and arrives as a slice. Pass an existing slice with
  `xs...`.

## Closures and defer

`closures_defer.go`: a function that remembers, and clean-up that runs at the end.

```{literalinclude} ../code/02-functions/closures_defer.go
:language: go
```

```{literalinclude} ../code/02-functions/closures_defer.out
:language: text
```

```{raw} html
:file: ../diagrams/defer-stack.html
```

- A **closure** is a function that captures variables from where it was written. Each call to
  `counter()` makes a fresh `n` that only the returned function can see.
- `defer` waits until the surrounding function returns. Several defers run **last in, first out**,
  like a stack of plates.
- Deferred call arguments are worked out **immediately**: `defer fmt.Println("deferred", i)` saves
  the current `i` right now.

:::{note}
Functions are values in Go. You can store one in a variable, pass it to another function and return
it, which is exactly how `counter` works.
:::

## Common mistakes

- **Ignoring the second result.** `result, _ := divide(1, 0)` throws away the "did it work" signal.
- **`defer` inside a long loop.** Deferred calls only run when the *function* ends, so a loop that
  opens 10,000 files with `defer f.Close()` keeps them all open. Close inside a helper function.
- **Overusing named results.** In a long function a bare `return` hides what is being returned.
- **Mixing up `...` on both sides.** `nums ...int` declares; `xs...` unpacks a slice at the call.

## Hands-on exercises

**Exercise 1 · Stats.** Write `average(nums ...float64) (float64, bool)` that returns `false` when
called with no numbers.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

func average(nums ...float64) (float64, bool) {
	if len(nums) == 0 {
		return 0, false
	}
	total := 0.0
	for _, n := range nums {
		total += n
	}
	return total / float64(len(nums)), true
}

func main() {
	fmt.Println(average(2, 4, 9))
	fmt.Println(average())
}
```

```text
5 true
0 false
```

</details>

**Exercise 2 · Adder factory.** Write `makeAdder(n int) func(int) int` so that `add5 := makeAdder(5)`
gives `add5(3) == 8`.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

func makeAdder(n int) func(int) int {
	return func(x int) int { return x + n }
}

func main() {
	add5 := makeAdder(5)
	add10 := makeAdder(10)
	fmt.Println(add5(3), add10(3))
}
```

```text
8 13
```

Each adder remembers its own `n`.

</details>

**Exercise 3 · Timer with defer.** Write `slowJob()` that prints `start`, then `end` from a deferred
call, and in between prints `working`. Predict the order before running.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

func slowJob() {
	fmt.Println("start")
	defer fmt.Println("end")
	fmt.Println("working")
}

func main() {
	slowJob()
}
```

```text
start
working
end
```

`defer` registers the call when it is reached, but runs it as the function returns.

</details>
