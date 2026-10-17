# Session 1 · Hello, Go and the basics

## Watch the class

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/3ofJp54f-Tk"
  title="Learn Go from Scratch | Ep 1 | Need of Golang + Hello World in Go" loading="lazy" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/LkJVJFxcehI"
  title="Learn Go from Scratch | Ep 2 | Variables, Conditions, Loops + Taking Input" loading="lazy" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

## The big idea

Go is a small, fast language made at Google for building servers and command-line tools. It is
**compiled**: you write text files, the compiler checks them, and you get one native program that
runs anywhere with no extras to install. It is also **statically typed**: every variable has a
type that is fixed and checked before the program ever runs, so a whole class of typos never reach
your users.

**Everyday example:** a recipe card. The card says exactly what each ingredient is ("200 g flour",
"2 eggs"). A cook who reads "2 flour" is stopped at once, before anything goes in the oven. That
early stop is what the Go compiler does with your types.

:::{admonition} In plain words
:class: tip
A Go program is a file that says `package main`, imports what it needs, and has a function called
`main`. Go starts there. Variables have types, loops are all spelled `for`, and the compiler will
not let you leave a variable or import unused.

**Reach for Go when:**

- you want one small, fast program to copy to a server
- you are writing a web API, a CLI tool or something that does many things at once
- you like a language that is easy to read in a year's time
:::

```{raw} html
:file: ../diagrams/run-pipeline.html
```

## Hello, Go

`hello.go`: the smallest useful program, plus formatted printing.

```{literalinclude} ../code/01-basics/hello.go
:language: go
```

```{literalinclude} ../code/01-basics/hello.out
:language: text
```

- `package main` marks a program (not a library). `func main()` is where it starts.
- `fmt.Println` prints and adds a newline; `fmt.Print` does not.
- `fmt.Printf` fills in **verbs**: `%s` for a string, `%d` for an integer, `%v` for "anything",
  `%T` for the type, `%+v` for a struct with field names.

Run it with `go run hello.go`. To keep the program as a file, use `go build hello.go` and run
`./hello`.

## Variables, constants and types

`variables.go`: three ways to make a variable, and what you get if you give it no value.

```{literalinclude} ../code/01-basics/variables.go
:language: go
```

```{literalinclude} ../code/01-basics/variables.out
:language: text
```

- `var name type = value` is the full form. Leave out the type and Go works it out.
- `name := value` is the short form you will use most. It only works **inside functions**.
- `const` values never change.
- A variable you declare but do not set gets its **zero value**: `0`, `false`, `""`, `nil`. There
  is no "undefined" in Go.
- Go never converts numbers quietly. `7/2` is `3` because both are integers. Say
  `float64(a)/float64(b)` when you want `3.5`.

## Decisions and loops

`flow.go`: `if`, `for` (the only loop), and `switch`.

```{literalinclude} ../code/01-basics/flow.go
:language: go
```

```{literalinclude} ../code/01-basics/flow.out
:language: text
```

- No brackets around conditions, but braces are required.
- `for` does the job of `for`, `while` and `do-while`. `for {}` loops forever until you `break`.
- A `switch` case stops by itself; there is no fall-through, and one case can list several values.
- `if square := age * age; square > 200 {` declares a variable that lives only inside that `if`.

:::{note}
`gofmt` (run by `go fmt` or your editor on save) lays out your code in the one standard style.
Do not argue about tabs and braces; let the tool decide.
:::

## Common mistakes

- **Unused variable or import.** `x declared and not used` is a compile error, not a warning. Use
  the value, or write `_ = x` while experimenting.
- **`:=` outside a function.** At the top of a file use `var`.
- **Expecting `7/2` to be 3.5.** Integer division drops the fraction.
- **`:=` shadowing.** In `x := 1` inside an inner block you create a *new* `x`; the outer one is
  unchanged.
- **Thinking a `switch` falls through** like C or Java. It does not.

## Hands-on exercises

Try each one before opening the solution.

**Exercise 1 · Greeter.** Declare `name` and `age` with `:=` and print `Hi, I am Asha and I am 28.`
using `Printf`.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

func main() {
	name := "Asha"
	age := 28
	fmt.Printf("Hi, I am %s and I am %d.\n", name, age)
}
```

```text
Hi, I am Asha and I am 28.
```

</details>

**Exercise 2 · FizzBuzz.** For 1 to 15 print `Fizz` for multiples of 3, `Buzz` for multiples
of 5, `FizzBuzz` for both, otherwise the number.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

func main() {
	for i := 1; i <= 15; i++ {
		switch {
		case i%15 == 0:
			fmt.Println("FizzBuzz")
		case i%3 == 0:
			fmt.Println("Fizz")
		case i%5 == 0:
			fmt.Println("Buzz")
		default:
			fmt.Println(i)
		}
	}
}
```

```text
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
```

A `switch` with no value after it is a tidy `if / else if` chain: the first true case wins.

</details>

**Exercise 3 · Celsius table.** Print a table from 0 to 40 °C in steps of 10 with the Fahrenheit
value (`c*9/5 + 32`) to one decimal place.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

func main() {
	for c := 0; c <= 40; c += 10 {
		f := float64(c)*9/5 + 32
		fmt.Printf("%2d C = %.1f F\n", c, f)
	}
}
```

```text
 0 C = 32.0 F
10 C = 50.0 F
20 C = 68.0 F
30 C = 86.0 F
40 C = 104.0 F
```

Convert `c` to `float64` first; mixing an `int` and a `float64` in one expression will not compile.

</details>

<details class="source">
<summary>Source files for this session</summary>

{download}`hello.go <../code/01-basics/hello.go>` ·
{download}`variables.go <../code/01-basics/variables.go>` ·
{download}`flow.go <../code/01-basics/flow.go>`

</details>
