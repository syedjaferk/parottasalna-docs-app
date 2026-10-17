# Session 16 · Mutex and data races

## The big idea

Goroutines run at the same time, and when two of them touch the **same variable** the result can
be wrong in ways that appear only sometimes. This is a **data race**. A `sync.Mutex` ("mutual
exclusion") is a lock that lets only one goroutine into a protected section at a time.

**Everyday example:** a single toilet with a lock on the door. Whoever gets in locks it, does their
business, unlocks it. Without the lock, two people walk in together and things go badly.

:::{admonition} In plain words
:class: tip
`mutex.Lock()` before touching shared data, `mutex.Unlock()` right after. Prefer
`defer mutex.Unlock()`. For one simple number, `sync/atomic` is lighter. Keep the lock held for as
little code as possible.

**Reach for it when:**

- several goroutines read and write the same variable, map or slice
- a counter, cache or in-memory store is shared by many HTTP requests
:::

```{raw} html
:file: ../diagrams/race-vs-lock.html
```

## The race

`counter++` looks like one step but is three: read the value, add one, write it back. Two goroutines
can both read 7 and both write 8, so one increment is lost.

`without_mutex.go`: two goroutines each add 1 a million times. The course used 10,000, which is too
small to show the bug on a fast machine, so we use a million. The three lines below are three separate runs:

```{literalinclude} ../code/16-mutex/without_mutex.go
:language: go
```

```text
expected 2000000, got 1052595
expected 2000000, got 1055568
expected 2000000, got 1092939
```

Every run gives a different wrong answer. Go can find these for you with the **race detector**:
`go run -race without_mutex.go` prints `WARNING: DATA RACE` with the exact lines that clash.
(When I ran it, it reported 2 races.)

## The fix

`with_mutex.go`

```{literalinclude} ../code/16-mutex/with_mutex.go
:language: go
```

```{literalinclude} ../code/16-mutex/with_mutex.out
:language: text
```

The result is correct every time. We also used a `WaitGroup` instead of the original `time.Sleep(time.Second)`,
so there is no guessing.

## A tidy shape: lock inside the type

`safe_counter.go`: keep the lock next to the data it guards, and expose methods that take it.
It also shows `atomic.Int64` for a plain counter.

```{literalinclude} ../code/16-mutex/safe_counter.go
:language: go
```

```{literalinclude} ../code/16-mutex/safe_counter.out
:language: text
```

- Callers of `Inc` never see the lock, so they cannot forget it.
- Use `sync.RWMutex` when reads are far more common than writes: many readers at once, one writer.
- Maps are **not** safe for concurrent writes: Go may crash with `fatal error: concurrent map writes`.

:::{important}
"Share memory by communicating" is Go's motto. Often a channel (next session) removes the need for a
lock: one goroutine owns the data and others send it requests.
:::

## Common mistakes

- **Forgetting to unlock.** The next `Lock` waits forever. Use `defer`.
- **Copying a struct that contains a mutex.** The copy has its own lock, so nothing is protected. Pass pointers.
- **Locking twice in a row** in one goroutine (for example a locked method calling another locked method) is a deadlock.
- **Holding the lock during slow work** such as a network call. Everyone else waits.
- **Protecting writes but not reads.** A read that overlaps a write is also a race.
- **Never running `go test -race` / `go run -race`.** It finds most of these.

## Hands-on exercises

**Exercise 1 · Safe bank balance.** Make 100 goroutines each deposit 10 into a shared balance using a mutex. Print the total.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"sync"
)

type Account struct {
	mu      sync.Mutex
	balance int
}

func (a *Account) Deposit(n int) {
	a.mu.Lock()
	defer a.mu.Unlock()
	a.balance += n
}

func main() {
	acc := &Account{}
	var wg sync.WaitGroup
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			acc.Deposit(10)
		}()
	}
	wg.Wait()
	fmt.Println(acc.balance)
}
```

```text
1000
```

</details>

**Exercise 2 · Safe map.** Many goroutines count words into one map. Protect it with a mutex and print the count for `"go"`.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"sync"
)

func main() {
	counts := map[string]int{}
	var mu sync.Mutex
	var wg sync.WaitGroup
	for i := 0; i < 50; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			mu.Lock()
			counts["go"]++
			mu.Unlock()
		}()
	}
	wg.Wait()
	fmt.Println(counts["go"])
}
```

```text
50
```

</details>

**Exercise 3 · Atomic.** Replace the mutex counter with `atomic.Int64` for two goroutines adding 1,000 each.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"sync"
	"sync/atomic"
)

func main() {
	var n atomic.Int64
	var wg sync.WaitGroup
	for g := 0; g < 2; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < 1000; i++ {
				n.Add(1)
			}
		}()
	}
	wg.Wait()
	fmt.Println(n.Load())
}
```

```text
2000
```

</details>
