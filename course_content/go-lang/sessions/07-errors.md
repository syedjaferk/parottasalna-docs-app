# Session 7 · Errors, panics and retry

## The big idea

Go has no exceptions for ordinary problems. A function that can fail simply **returns an `error`
as its last result**, and the caller decides what to do. It feels repetitive at first, but it makes
every failure visible right where it can happen.

**Everyday example:** a courier. When the parcel cannot be delivered, they do not shout down the
street; they hand you a slip that says why ("no one home") and you decide: try again, call, or
give up.

:::{admonition} In plain words
:class: tip
`value, err := doThing()`, then `if err != nil { ... }`. Add context as the error travels up with
`fmt.Errorf("what I was doing: %w", err)`. Test for a specific cause with `errors.Is`, or pull
out a custom type with `errors.As`.

**Reach for it when:**

- anything touches files, the network, user input or a database
- you want a clear message that says *what* failed and *why*
- a flaky call deserves a limited retry
:::

```{raw} html
:file: ../diagrams/error-chain.html
```

## Returning and wrapping errors

`basics.go`

```{literalinclude} ../code/07-errors/basics.go
:language: go
```

```{literalinclude} ../code/07-errors/basics.out
:language: text
```

- `errors.New` makes a simple error. A package-level `var ErrNegative = errors.New(...)` is a
  **sentinel** callers can compare against.
- `%w` in `fmt.Errorf` wraps the original so it is still reachable. `%v` would flatten it into text.
- `errors.Is(err, ErrNegative)` looks through all the layers.

## Custom error types

`custom.go`

```{literalinclude} ../code/07-errors/custom.go
:language: go
```

```{literalinclude} ../code/07-errors/custom.out
:language: text
```

Any type with an `Error() string` method is an error. Use `errors.As` when the caller needs the
extra fields (here, which field was wrong).

## Retry with back-off

The syllabus ends with "retry logic and robustness". Here is the standard shape: try, wait, try
again with a longer wait, and finally give up with all the errors attached.

`retry.go`

```{literalinclude} ../code/07-errors/retry.go
:language: go
```

```{literalinclude} ../code/07-errors/retry.out
:language: text
```

`errors.Join` (Go 1.20+) bundles several errors into one. Only retry errors that are **temporary**
(network timeout, 503). Retrying "invalid password" just repeats the mistake.

## Panic and recover

A `panic` is for bugs that should never happen (index out of range, nil pointer). It unwinds the
stack running deferred functions, and `recover()` inside a deferred function can catch it.

`panic.go`

```{literalinclude} ../code/07-errors/panic.go
:language: go
```

```{literalinclude} ../code/07-errors/panic.out
:language: text
```

:::{important}
Use `error` for things that can reasonably go wrong, `panic` only for programmer mistakes. A web
server often uses `recover` once at the top so one bad request does not kill the whole process.
:::

## Common mistakes

- **Ignoring errors with `_`.** `data, _ := os.ReadFile(f)` hides the reason it failed.
- **Returning a non-nil error and a good value, or the reverse, inconsistently.** Convention: if `err != nil`, ignore the other results.
- **Wrapping with `%v` instead of `%w`.** `errors.Is` then cannot find the cause.
- **Comparing errors with `==` on wrapped errors.** Use `errors.Is`.
- **Retrying forever.** Always cap attempts and add a delay.
- **Using `panic` for normal control flow.**

## Hands-on exercises

**Exercise 1 · Safe square root.** Write `sqrt(x float64) (float64, error)` that returns an error for
negative input, using `math.Sqrt`.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"math"
)

func sqrt(x float64) (float64, error) {
	if x < 0 {
		return 0, fmt.Errorf("sqrt of negative number %v", x)
	}
	return math.Sqrt(x), nil
}

func main() {
	fmt.Println(sqrt(16))
	fmt.Println(sqrt(-4))
}
```

```text
4 <nil>
0 sqrt of negative number -4
```

</details>

**Exercise 2 · Sentinel error.** Make `withdraw(balance, amount float64) (float64, error)` return a
package-level `ErrInsufficient` and check it with `errors.Is`, even after wrapping.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"errors"
	"fmt"
)

var ErrInsufficient = errors.New("insufficient funds")

func withdraw(balance, amount float64) (float64, error) {
	if amount > balance {
		return balance, fmt.Errorf("withdraw %.0f: %w", amount, ErrInsufficient)
	}
	return balance - amount, nil
}

func main() {
	_, err := withdraw(100, 250)
	fmt.Println(err)
	fmt.Println(errors.Is(err, ErrInsufficient))
}
```

```text
withdraw 250: insufficient funds
true
```

</details>

**Exercise 3 · Retry only the temporary.** Extend the retry idea: stop at once when the error is the
permanent `ErrBadInput`, but retry others.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"errors"
	"fmt"
)

var ErrBadInput = errors.New("bad input")

func retry(attempts int, fn func(int) error) error {
	var err error
	for i := 1; i <= attempts; i++ {
		if err = fn(i); err == nil {
			return nil
		}
		fmt.Println("attempt", i, "failed:", err)
		if errors.Is(err, ErrBadInput) {
			return err // permanent: retrying will not help
		}
	}
	return fmt.Errorf("gave up: %w", err)
}

func main() {
	fmt.Println(retry(3, func(n int) error { return errors.New("timeout") }))
	fmt.Println(retry(3, func(n int) error { return ErrBadInput }))
}
```

```text
attempt 1 failed: timeout
attempt 2 failed: timeout
attempt 3 failed: timeout
gave up: timeout
attempt 1 failed: bad input
bad input
```

</details>
