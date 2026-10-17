# Session 14 · Goroutines

## The big idea

Normally a program does one thing at a time. A **goroutine** is a function that runs *alongside*
the rest of your program. You start one by putting the word `go` in front of a call. Goroutines are
so light (a few kilobytes) that a program can run hundreds of thousands of them.

**Everyday example:** a kitchen. One cook doing everything in order boils the rice, *then* chops
vegetables, *then* fries. Two cooks start both at once, and dinner is ready in half the time.

:::{admonition} In plain words
:class: tip
`go doWork()` starts `doWork` in the background and your code carries on **immediately**. When
`main` returns the whole program ends, even if goroutines are still running.

**Reach for it when:**

- you wait on slow things: network calls, disks, timers
- the work splits into independent pieces (many files, many URLs)
- you serve many users at once (every HTTP request already runs in its own goroutine)
:::

```{raw} html
:file: ../diagrams/timeline.html
```

## One after another

`sequential.go`: the course's `task1(); task2()` example, shortened.

```{literalinclude} ../code/14-goroutines/sequential.go
:language: go
```

```{literalinclude} ../code/14-goroutines/sequential.out
:language: text
```

Task 2 waits for Task 1 to finish completely. 6 steps × 100 ms ≈ 600 ms.

## At the same time

`concurrent.go`: both tasks start with `go`. They use different delays so you can see them interleave.

```{literalinclude} ../code/14-goroutines/concurrent.go
:language: go
```

```{literalinclude} ../code/14-goroutines/concurrent.out
:language: text
```

The "fast" task prints three lines in 140 ms while the "slow" task prints three in 400 ms, and the
lines mix. The total is about the slowest task, not the sum. Your exact interleaving can differ a little
from run to run, because the scheduler decides.

The `time.Sleep(700 * time.Millisecond)` in `main` is a **cheat**: it just gives the goroutines time to
finish. It breaks if they are slower than you guessed. The next session shows the right way.

## main does not wait

`main_exits.go`

```{literalinclude} ../code/14-goroutines/main_exits.go
:language: go
```

```{literalinclude} ../code/14-goroutines/main_exits.out
:language: text
```

`main` finished before the goroutine got a turn, so the greeting usually never appears. (Run it a few
times; the result is not guaranteed either way, which is exactly the problem.)

## Common mistakes

- **Starting a goroutine and returning at once.** The program exits and kills it.
- **Using `time.Sleep` to wait.** It is a guess. Use a `WaitGroup` or a channel.
- **Assuming an order.** Goroutines run in whatever order the scheduler picks. Never rely on it.
- **Sharing variables without protection.** Two goroutines writing the same variable is a data race (Session 16).
- **Leaking goroutines.** One that waits forever on a channel nobody uses lives until the program ends.
- **Capturing the loop variable** in Go before 1.22 gave every goroutine the same value. Modern Go gives each iteration its own copy, but older code may still pass it as an argument.

## Hands-on exercises

**Exercise 1 · Two greeters.** Start two goroutines that each print a greeting after different sleeps (10 ms and 50 ms) and wait 100 ms in `main`. Predict which prints first.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"time"
)

func greet(name string, d time.Duration) {
	time.Sleep(d)
	fmt.Println("hello from", name)
}

func main() {
	go greet("slow", 50*time.Millisecond)
	go greet("quick", 10*time.Millisecond)
	time.Sleep(100 * time.Millisecond)
}
```

```text
hello from quick
hello from slow
```

The one with the shorter sleep wins, regardless of the order they were started.

</details>

**Exercise 2 · Anonymous goroutine.** Start a goroutine with a function literal that prints a message passed in as an argument.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	msg := "from a closure"
	go func(m string) {
		fmt.Println("hello", m)
	}(msg) // the () at the end calls the function right away
	time.Sleep(50 * time.Millisecond)
}
```

```text
hello from a closure
```

</details>

**Exercise 3 · How many?** Start 1,000 goroutines that each add 1 to an atomic counter, wait, and print the total. (Atomics are explained in Session 16.)

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"sync"
	"sync/atomic"
)

func main() {
	var total atomic.Int64
	var wg sync.WaitGroup
	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			total.Add(1)
		}()
	}
	wg.Wait()
	fmt.Println(total.Load())
}
```

```text
1000
```

A thousand goroutines is nothing for Go; try a hundred thousand.

</details>
