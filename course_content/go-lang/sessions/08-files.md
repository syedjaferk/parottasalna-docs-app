# Session 8 · Working with files and folders

## The big idea

Programs forget everything when they stop, unless they write it to a **file**. Go's `os` package
lets you create, read, append to and list files and folders. The pattern is always the same: open,
check the error, use it, close it.

**Everyday example:** a notebook. You open it to a page, read or write, and close it. If you forget
to close the cupboard door (a file you never close), eventually nothing else fits in.

:::{admonition} In plain words
:class: tip
Small file? `os.ReadFile` and `os.WriteFile` do it in one line. Big file or line by line? `os.Open`
with a `bufio.Scanner`. Adding to the end? `os.OpenFile` with `os.O_APPEND`. Always
`defer file.Close()` straight after a successful open.

**Reach for it when:**

- you save settings, notes or results between runs
- you process a log or a CSV
- you build file tools: copy, search, count words, print a folder tree
:::

```{raw} html
:file: ../diagrams/file-modes.html
```

## Create and write

`create_write.go`

```{literalinclude} ../code/08-files/create_write.go
:language: go
```

```{literalinclude} ../code/08-files/create_write.out
:language: text
```

`os.Create` makes the file, or **empties it** if it already exists. `os.WriteFile` also replaces the
whole content. The `0644` is the Unix permission (owner reads and writes, others read).

## Read, append and scan

`read_append.go`

```{literalinclude} ../code/08-files/read_append.go
:language: go
```

```{literalinclude} ../code/08-files/read_append.out
:language: text
```

- `os.ReadFile` gives you **bytes**. Printing them raw shows numbers (`[108 105 110 101]` is "line");
  convert with `string(data)`.
- `os.OpenFile(name, os.O_APPEND|os.O_WRONLY, 0644)` adds to the end instead of replacing. The `|`
  joins flags.
- `bufio.Scanner` reads one line per `Scan()`, so a huge file never has to fit in memory.
- A missing file is an error value, not a crash. `os.IsNotExist(err)` recognises it.

## Folders

`dirs.go`

```{literalinclude} ../code/08-files/dirs.go
:language: go
```

```{literalinclude} ../code/08-files/dirs.out
:language: text
```

`os.MkdirAll` creates nested folders in one call. `os.ReadDir` lists one folder; `filepath.WalkDir`
visits every file below it, which is the heart of "tree", "search" and "word count" tools. Build
paths with `filepath.Join`, not string `+`, so it works on Windows too.

## Common mistakes

- **Forgetting `Close()`.** Leaks file handles; `defer` it.
- **Using `os.Create` to "add" to a file.** It wipes the file first. Use `O_APPEND`.
- **Ignoring the error after `Open`.** A nil file then panics on the next line.
- **Reading a huge file with `ReadFile`.** Use a scanner for big inputs.
- **Hard-coding `/` or `\`.** Use `filepath.Join`.
- **Deferring `Close()` before checking `err`.** If `Open` failed, there is nothing to close.

## Hands-on exercises

**Exercise 1 · Line counter.** Write three lines to `data.txt`, then read it back and print how many lines it has.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"os"
	"strings"
)

func main() {
	os.WriteFile("data.txt", []byte("a\nb\nc\n"), 0644)
	data, err := os.ReadFile("data.txt")
	if err != nil {
		fmt.Println(err)
		return
	}
	lines := strings.Split(strings.TrimSpace(string(data)), "\n")
	fmt.Println(len(lines), "lines")
}
```

```text
3 lines
```

</details>

**Exercise 2 · Copy a file.** Write `copyFile(src, dst string) error` using `os.ReadFile` and `os.WriteFile`, and show the copy has the same text.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"os"
)

func copyFile(src, dst string) error {
	data, err := os.ReadFile(src)
	if err != nil {
		return err
	}
	return os.WriteFile(dst, data, 0644)
}

func main() {
	os.WriteFile("a.txt", []byte("hello"), 0644)
	if err := copyFile("a.txt", "b.txt"); err != nil {
		fmt.Println(err)
		return
	}
	b, _ := os.ReadFile("b.txt")
	fmt.Println(string(b))
	fmt.Println(copyFile("missing.txt", "c.txt"))
}
```

```text
hello
open missing.txt: no such file or directory
```

For huge files, `io.Copy` between an open source and destination streams instead of loading everything.

</details>

**Exercise 3 · Count by extension.** Create `x.go`, `y.go`, `z.txt` in a folder and print how many files have each extension (sorted).

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
)

func main() {
	os.MkdirAll("demo", 0755)
	for _, n := range []string{"x.go", "y.go", "z.txt"} {
		os.WriteFile(filepath.Join("demo", n), nil, 0644)
	}
	entries, _ := os.ReadDir("demo")
	counts := map[string]int{}
	for _, e := range entries {
		counts[filepath.Ext(e.Name())]++
	}
	exts := make([]string, 0)
	for ext := range counts {
		exts = append(exts, ext)
	}
	sort.Strings(exts)
	for _, ext := range exts {
		fmt.Println(ext, counts[ext])
	}
}
```

```text
.go 2
.txt 1
```

</details>
