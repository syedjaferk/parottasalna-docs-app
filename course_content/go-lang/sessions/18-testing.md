# Session 18 · Testing your Go code

## The big idea

A **test** is a small program that calls your code with known input and checks the answer. Run
the tests after every change and you find out within a second if you broke something. Go has
testing built in: no extra library, just a file ending in `_test.go` and the command `go test`.

**Everyday example:** a taste test before a dish leaves the kitchen. The cook tastes it, compares it
with what it should taste like, and fixes it if it is off. Automatic tests do that tasting for every
dish, every time, in milliseconds.

:::{admonition} In plain words
:class: tip
Put `x_test.go` next to `x.go`. Write `func TestSomething(t *testing.T)`. Call your function, compare
with what you expect, and call `t.Errorf(...)` when they differ. List many cases in a table and run each
as a subtest with `t.Run`.

**Reach for it when:**

- you fix a bug (write a test that fails first, so it can never come back)
- you refactor and want proof that nothing changed
- the code has edge cases: empty input, zero, negative, huge
:::

```{raw} html
:file: ../diagrams/table-test.html
```

## The code under test

A small package, `textx`, with two functions.

```{literalinclude} ../code/18-testing/textx/textx.go
:language: go
```

## The tests

```{literalinclude} ../code/18-testing/textx/textx_test.go
:language: go
```

Run them with `go test -v` inside the package folder:

```{literalinclude} ../code/18-testing/test_v.out
:language: text
```

- A test function starts with `Test` and takes `*testing.T`.
- `t.Errorf` records a failure and **continues**; `t.Fatalf` stops this test at once. Use `Fatalf`
  when later lines would be meaningless (for example after an unexpected error).
- The **table-driven** style (`TestIsPalindrome`) is the Go standard: add a case by adding a line.
- `t.Run(name, ...)` creates a named subtest, so a failure points at the exact case.
- Files named `_test.go` are never part of your built program.

## When a test fails

If someone breaks the function (here: the code stops ignoring spaces), the failing case is named
for you, with the input, the result and the expectation:

```{literalinclude} ../code/18-testing/fail.out
:language: text
```

The message `IsPalindrome("Never Odd Or Even") = false, want true` is good because it tells you
the input, the actual and the wanted value. Write failure messages that way.

## Coverage and benchmarks

```{literalinclude} ../code/18-testing/cover.out
:language: text
```

`go test -cover` shows what percentage of statements the tests ran. 100 % does not mean "no bugs",
but a low number points at untested code. `go test -coverprofile=c.out` plus `go tool cover -html=c.out`
shows the missed lines in colour.

A **benchmark** measures speed. It runs the code `b.N` times, and Go picks `b.N` until the timing is stable:

```{literalinclude} ../code/18-testing/bench.out
:language: text
```

(The timing is from my machine; yours will differ.) Run benchmarks with `go test -bench=.`.

## Testing HTTP handlers

You already know the trick from Session 11: `httptest.NewRecorder()` and `httptest.NewRequest()` let
you call a handler directly and look at the status and body, with no real network. Combine it with the
table-driven pattern and you can test every route of the Todo API in a few lines.

## A command checklist

| Command | What it does |
|---|---|
| `go test ./...` | run every test in every package |
| `go test -race ./...` | also look for data races (Sessions 14 to 17) |
| `go test -run TestWordCount` | run one test by name |
| `go vet ./...` | catch suspicious code, like a copied `WaitGroup` |
| `go fmt ./...` | format everything the standard way |

:::{important}
Run `go test -race ./...` in CI. Concurrency bugs are the ones you never find by reading the code.
:::

## Common mistakes

- **Testing only the happy path.** Add empty input, zero, negative, a missing file, very large input.
- **Tests that depend on each other or on order.** Each test should set up what it needs.
- **Tests that depend on real time, the network or a live database.** They become flaky. Use `httptest`, in-memory databases or fakes.
- **Using `t.Fatal` in a goroutine.** It must be called from the test's own goroutine; send an error through a channel instead.
- **Comparing maps or slices with `==`.** It will not compile; use `reflect.DeepEqual` or `slices.Equal`.
- **Vague messages like `"failed"`.** Include input, got and want.
- **Forgetting the capital letter.** `testFoo` is not a test, so `go test` ignores it silently.

## Hands-on exercises

The test files are not `package main` programs, so the snippets below are complete files you place
in a folder with a `go.mod`. I ran each one with `go test` and the result is shown.

**Exercise 1 · Test a function.** Given `Abs(n int) int`, write a table-driven test with positive, negative and zero.

<details class="solution"><summary>Solution</summary>

`abs.go`

```go
package mathx

func Abs(n int) int {
	if n < 0 {
		return -n
	}
	return n
}
```

`abs_test.go`

```go
package mathx

import "testing"

func TestAbs(t *testing.T) {
	tests := []struct {
		name string
		in   int
		want int
	}{
		{"positive", 5, 5},
		{"negative", -5, 5},
		{"zero", 0, 0},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			if got := Abs(tc.in); got != tc.want {
				t.Errorf("Abs(%d) = %d, want %d", tc.in, got, tc.want)
			}
		})
	}
}
```

```text
ok  	exercise/mathx	0.003s
```

</details>

**Exercise 2 · Test the error path.** Given `Divide(a, b int) (int, error)` that returns `ErrDivideByZero`, test both a normal division and a zero divisor with `errors.Is`.

<details class="solution"><summary>Solution</summary>

`div.go`

```go
package mathx

import "errors"

var ErrDivideByZero = errors.New("divide by zero")

func Divide(a, b int) (int, error) {
	if b == 0 {
		return 0, ErrDivideByZero
	}
	return a / b, nil
}
```

`div_test.go`

```go
package mathx

import (
	"errors"
	"testing"
)

func TestDivide(t *testing.T) {
	got, err := Divide(10, 2)
	if err != nil || got != 5 {
		t.Fatalf("Divide(10, 2) = %d, %v; want 5, nil", got, err)
	}
	_, err = Divide(1, 0)
	if !errors.Is(err, ErrDivideByZero) {
		t.Errorf("err = %v, want ErrDivideByZero", err)
	}
}
```

```text
ok  	exercise/mathx	0.003s
```

</details>

**Exercise 3 · Test for a race.** Write a test that increments a shared counter from 100 goroutines under a mutex and run it with `go test -race`.

<details class="solution"><summary>Solution</summary>

`counter_test.go`

```go
package mathx

import (
	"sync"
	"testing"
)

func TestCounterRace(t *testing.T) {
	var (
		mu sync.Mutex
		n  int
		wg sync.WaitGroup
	)
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			mu.Lock()
			n++
			mu.Unlock()
		}()
	}
	wg.Wait()
	if n != 100 {
		t.Errorf("n = %d, want 100", n)
	}
}
```

```text
ok  	exercise/mathx	1.012s
```

Remove the `mu.Lock()` and `mu.Unlock()` lines and run `go test -race` again to watch the detector fail the test.

</details>

## What's next

You have now covered the same ground as the 40-day course's projects and the syllabus topics around
them. Good next steps: rebuild the file tools and the Todo API from scratch without looking, add
`context.Context` for cancellation, try a router such as `chi`, and deploy one of your tools as a single
binary.
