# Session 9 · Command-line tools: args and flags

## The big idea

A command-line tool is a program you run by typing its name and some **options**: `ls -l /tmp`.
Go makes these tools easy to build and ship, because the result is one file with no runtime. Your
program gets the typed words from `os.Args`, and the `flag` package turns `-name=value` options into
ready-to-use variables, with a free `-h` help page.

**Everyday example:** ordering coffee. "Latte, large, no sugar" is the command and its options. The
barista (your program) must cope with a missing size or an unknown drink by asking, not by
throwing the cup.

:::{admonition} In plain words
:class: tip
`os.Args` is the raw list of words (`Args[0]` is the program). For named options use `flag`:
declare each one, call `flag.Parse()`, then check them. Print a usage message and `os.Exit(1)`
for bad input.

**Reach for it when:**

- you are building utilities: backup, file finder, log parser
- the same program should behave differently without editing code
- scripts and cron jobs must be able to call your tool
:::

```{raw} html
:file: ../diagrams/cli-parts.html
```

## Raw arguments

`args.go`: run with no argument, then with `Asha`.

```{literalinclude} ../code/09-cli/args.go
:language: go
```

```{literalinclude} ../code/09-cli/args.out
:language: text
```

With the argument `Asha`:

```{literalinclude} ../code/09-cli/args.asha.out
:language: text
```

## Named flags

`flags.go` declares four options and a custom usage message. First with no flags, then with
`-dir=./src -ext=.go -verbose -limit=5 extra`.

```{literalinclude} ../code/09-cli/flags.go
:language: go
```

```{literalinclude} ../code/09-cli/flags.missing.out
:language: text
```

```{literalinclude} ../code/09-cli/flags.out
:language: text
```

- `flag.StringVar(&dir, "dir", "", "help text")` ties the option to your variable with a default.
- **All flags must come before positional words.** After the first non-flag word, parsing stops;
  the rest are in `flag.Args()`.
- `-verbose` alone means `true` for a bool flag. `-limit=5` and `-limit 5` both work for ints.
- Without `flag.Parse()` nothing is read. Forgetting it is the classic bug.

## Worked example: a file finder

The course project combines flags with the folder walk from Session 8.

`finder.go` (run twice: with a valid folder, then a bad one)

```{literalinclude} ../code/09-cli/finder.go
:language: go
```

```{literalinclude} ../code/09-cli/finder.out
:language: text
```

```{literalinclude} ../code/09-cli/finder.bad.out
:language: text
```

`filepath.SkipAll` stops the walk early once the limit is reached. The error path ends with
`os.Exit(1)`: a non-zero **exit code** tells scripts the tool failed.

## Common mistakes

- **Forgetting `flag.Parse()`.**
- **Putting options after the positional words.** `tool file.txt -v` leaves `-v` unparsed.
- **Dereferencing at the wrong time.** `flag.String` returns a pointer; read `*name` only after `Parse()`.
- **Printing errors to stdout and exiting 0.** Use `fmt.Fprintln(os.Stderr, ...)` and `os.Exit(1)`.
- **Trusting input.** Check that the path exists and is a directory before walking it.

## Hands-on exercises

**Exercise 1 · Greeter flags.** Define `-name` (default `Guest`) and `-times` (default 1). Print the greeting that many times. (Parse a fixed slice so the example is repeatable.)

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"flag"
	"fmt"
)

func main() {
	name := flag.String("name", "Guest", "who to greet")
	times := flag.Int("times", 1, "how many times")
	flag.CommandLine.Parse([]string{"-name=Asha", "-times=2"}) // normally flag.Parse()

	for i := 0; i < *times; i++ {
		fmt.Println("Hello,", *name)
	}
}
```

```text
Hello, Asha
Hello, Asha
```

In a real tool, replace the `Parse([]string{…})` line with `flag.Parse()`.

</details>

**Exercise 2 · Sum the args.** Treat leftover arguments as integers and print their total, skipping anything that is not a number with a message.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	args := []string{"10", "x", "5"} // normally os.Args[1:]
	total := 0
	for _, a := range args {
		n, err := strconv.Atoi(a)
		if err != nil {
			fmt.Println("skipping", a)
			continue
		}
		total += n
	}
	fmt.Println("total:", total)
}
```

```text
skipping x
total: 15
```

</details>

**Exercise 3 · Required flag.** Print an error and exit with status 1 if `-file` is empty. Show what happens with `-file=notes.txt`.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"flag"
	"fmt"
)

func main() {
	file := flag.String("file", "", "file to process (required)")
	flag.CommandLine.Parse([]string{"-file=notes.txt"})

	if *file == "" {
		fmt.Println("Error: -file is required")
		flag.PrintDefaults()
		return // a real tool would call os.Exit(1)
	}
	fmt.Println("processing", *file)
}
```

```text
processing notes.txt
```

</details>
