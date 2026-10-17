# Session 15 · WaitGroup: waiting for goroutines

## The big idea

Starting goroutines is easy. Knowing when they are *all done* is the hard part. A
`sync.WaitGroup` is a counter built for that. You add one for every goroutine you start, each one
subtracts one when it finishes, and `Wait()` pauses until the counter hits zero.

**Everyday example:** a group trip. The guide counts 3 people onto the bus and will not drive off
until all 3 have checked back in. No guessing "they've probably finished by now".

:::{admonition} In plain words
:class: tip
`wg.Add(1)` before `go`, `defer wg.Done()` first thing inside the goroutine, `wg.Wait()` where you
need all of them finished. Pass the group **by pointer**.

**Reach for it when:**

- you start several goroutines and need all of them before continuing
- you fetch several URLs or process several files in parallel
- you replace a `time.Sleep` guess with something exact
:::

```{raw} html
:file: ../diagrams/waitgroup-counter.html
```

## Three workers

`workers.go`: the course's three workers, with each finishing at a different time.

```{literalinclude} ../code/15-waitgroup/workers.go
:language: go
```

```{literalinclude} ../code/15-waitgroup/workers.out
:language: text
```

`main` blocks at `wg.Wait()` until the counter is zero, and only then prints the last line. There is
no `Sleep` guess anywhere.

## Collecting results safely

`results.go`: each goroutine writes only its own slot of a pre-sized slice, so they never collide.

```{literalinclude} ../code/15-waitgroup/results.go
:language: go
```

```{literalinclude} ../code/15-waitgroup/results.out
:language: text
```

The order of the *work* is unpredictable, but the order of the *results* is fixed because each goroutine
owns one index. In Go 1.22 and newer, `i` and `w` are fresh on every loop turn, so the closure can use them directly.

## Common mistakes

- **Passing the `WaitGroup` by value.** The goroutine then decrements a copy and `Wait` never returns (a deadlock). Pass `&wg`.
- **Calling `Add` inside the goroutine.** `Wait` might run first and see zero. Call `Add` before `go`.
- **Forgetting `Done`.** `Wait` blocks forever. `defer wg.Done()` guarantees it even on early return or panic.
- **Too many `Done` calls.** The counter goes negative and the program panics.
- **Appending to one shared slice from many goroutines.** That is a race. Use indexed slots, a channel, or a mutex.

## Hands-on exercises

**Exercise 1 · Fan out.** Start 5 goroutines, each squaring its own number into its own slot of a result slice, then print the slice.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"sync"
)

func main() {
	squares := make([]int, 5)
	var wg sync.WaitGroup
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			squares[i] = i * i
		}()
	}
	wg.Wait()
	fmt.Println(squares)
}
```

```text
[0 1 4 9 16]
```

</details>

**Exercise 2 · Parallel "downloads".** Simulate three downloads of 100 ms each. Show that the total time is close to 100 ms, not 300 ms.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"sync"
	"time"
)

func download(name string, wg *sync.WaitGroup) {
	defer wg.Done()
	time.Sleep(100 * time.Millisecond)
}

func main() {
	start := time.Now()
	var wg sync.WaitGroup
	for _, f := range []string{"a.zip", "b.zip", "c.zip"} {
		wg.Add(1)
		go download(f, &wg)
	}
	wg.Wait()
	elapsed := time.Since(start)
	fmt.Println("under 200ms:", elapsed < 200*time.Millisecond)
}
```

```text
under 200ms: true
```

</details>

**Exercise 3 · Find the bug.** This program deadlocks (running it prints `working` and then `fatal error: all goroutines are asleep - deadlock!`). Explain why, then fix it.

<!-- no-run -->
```go
package main

import (
	"fmt"
	"sync"
)

func work(wg sync.WaitGroup) {
	defer wg.Done()
	fmt.Println("working")
}

func main() {
	var wg sync.WaitGroup
	wg.Add(1)
	go work(wg)
	wg.Wait()
}
```

<details class="solution"><summary>Solution</summary>

`work` received a **copy** of the `WaitGroup`, so its `Done()` lowered the copy's counter and the real counter stayed at 1: `Wait()` never returned. The fix is to pass a pointer:

```go
package main

import (
	"fmt"
	"sync"
)

func work(wg *sync.WaitGroup) {
	defer wg.Done()
	fmt.Println("working")
}

func main() {
	var wg sync.WaitGroup
	wg.Add(1)
	go work(&wg)
	wg.Wait()
	fmt.Println("done")
}
```

```text
working
done
```

`go vet` reports the original mistake as "passes lock by value".

</details>
