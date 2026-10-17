# Session 17 · Channels and select

## The big idea

Locks protect shared data. **Channels** avoid sharing in the first place: goroutines pass values to
each other through a pipe. One goroutine sends, another receives, and the pipe makes them meet at
exactly the right moment. This is Go's famous idea: *don't communicate by sharing memory; share
memory by communicating.*

**Everyday example:** a conveyor belt in a factory. One worker puts items on the belt, another takes
them off. They never touch each other's tools, and if the belt is full the first worker waits.

:::{admonition} In plain words
:class: tip
`ch := make(chan int)` makes a channel. `ch <- 5` sends, `v := <-ch` receives. An unbuffered channel
makes sender and receiver wait for each other; `make(chan int, 3)` is a **buffered** channel that
holds 3 values before a sender has to wait. `close(ch)` says "no more values". `select` waits on
several channels at once.

**Reach for it when:**

- goroutines hand work or results to each other (pipelines, worker pools)
- you need a timeout or cancel signal
- you want to wait for the first of several things
:::

```{raw} html
:file: ../diagrams/channel-pool.html
```

## Send and receive

`basics.go`

```{literalinclude} ../code/17-channels/basics.go
:language: go
```

```{literalinclude} ../code/17-channels/basics.out
:language: text
```

The unbuffered send `ch <- "ping"` could only finish when `main` was ready to receive. That meeting
is called a **handshake**. The buffered channel took two values with nobody receiving.

## A pipeline

`pipeline.go`: one stage generates numbers, the next squares them. Each stage closes its output when done.

```{literalinclude} ../code/17-channels/pipeline.go
:language: go
```

```{literalinclude} ../code/17-channels/pipeline.out
:language: text
```

- `for n := range ch` receives until the channel is **closed**, then stops.
- Only the **sender** should close a channel. Sending on a closed channel panics.
- `<-chan int` means receive-only, `chan<- int` send-only. The compiler enforces the direction.

## A worker pool

`workerpool.go`: three workers share one `jobs` queue and report on a `results` channel. This is the
usual way to limit how much runs at once.

```{literalinclude} ../code/17-channels/workerpool.go
:language: go
```

```{literalinclude} ../code/17-channels/workerpool.out
:language: text
```

Which worker takes which job changes from run to run, so the program collects the lines and sorts them
before printing. That keeps the output stable.

## select: waiting on many things

`select.go`: take whichever channel is ready first, with a timeout and a "don't wait" case.

```{literalinclude} ../code/17-channels/select.go
:language: go
```

```{literalinclude} ../code/17-channels/select.out
:language: text
```

The first loop turn gets the fast answer at 50 ms. The second turn waits for either the slow answer
(due at 400 ms) or the 200 ms timer, and the timer wins. `default` makes `select` non-blocking.

## When it goes wrong: deadlock

`deadlock.go`

```{literalinclude} ../code/17-channels/deadlock.go
:language: go
```

```{literalinclude} ../code/17-channels/deadlock.out
:language: text
```

Nobody could ever receive, so Go detects that every goroutine is stuck and stops with a clear message.
The line `[chan send]` tells you what `main` was waiting on.

## Common mistakes

- **Sending on an unbuffered channel with no receiver.** Deadlock.
- **Forgetting to `close`.** A `range` over the channel never ends.
- **Closing from the receiver side,** or closing twice. Both panic.
- **Goroutine leaks.** A goroutine blocked on a channel nobody reads lives forever.
- **Using a channel where a mutex is simpler.** A single counter needs an atomic or a lock, not a goroutine.
- **Assuming result order.** Workers finish in any order; sort or index results.

## Hands-on exercises

**Exercise 1 · Ping-pong.** One goroutine receives a number on `ping`, prints it and replies on `pong` with the number plus one. `main` sends 1, 3 and 5 and prints each reply.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

func main() {
	ping := make(chan int)
	pong := make(chan int)

	go func() {
		for n := range ping {
			fmt.Println("pong", n)
			pong <- n + 1
		}
	}()

	for n := 1; n <= 5; n += 2 {
		ping <- n
		fmt.Println("reply", <-pong)
	}
	close(ping) // lets the goroutine's range loop end
}
```

```text
pong 1
reply 2
pong 3
reply 4
pong 5
reply 6
```

Each send waits for the receiver and each receive waits for the sender, so the order is fixed.

</details>

**Exercise 2 · Sum with a channel.** Split `[1..10]` into two halves, sum each in a goroutine, and send the partial sums to a channel. Print the total.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

func sum(nums []int, out chan<- int) {
	total := 0
	for _, n := range nums {
		total += n
	}
	out <- total
}

func main() {
	nums := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
	out := make(chan int)
	go sum(nums[:5], out)
	go sum(nums[5:], out)
	a, b := <-out, <-out
	fmt.Println(a+b, "(addition does not care which half arrived first)")
}
```

```text
55 (addition does not care which half arrived first)
```

</details>

**Exercise 3 · Timeout.** Wait up to 100 ms for a slow operation (300 ms). Print `timed out` if it takes too long.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"time"
)

func slow() <-chan string {
	ch := make(chan string, 1) // buffered, so the sender never blocks forever
	go func() {
		time.Sleep(300 * time.Millisecond)
		ch <- "finished"
	}()
	return ch
}

func main() {
	select {
	case r := <-slow():
		fmt.Println(r)
	case <-time.After(100 * time.Millisecond):
		fmt.Println("timed out")
	}
}
```

```text
timed out
```

For real cancellation across many goroutines, look at `context.WithTimeout`.

</details>
