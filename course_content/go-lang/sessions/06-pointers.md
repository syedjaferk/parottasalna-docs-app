# Session 6 · Pointers

## Watch the class

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/EMmurC5p5XI"
  title="Pointers in Go – Memory Management &amp; Efficient Data Handling | EP 7" loading="lazy" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

## The big idea

Every variable lives at an address in memory. A **pointer** is a variable that holds such an
address. Why care? Because Go **copies** values when you pass them to a function. If you want the
function to change the *original*, give it the address instead of a copy.

**Everyday example:** a document. Emailing a photocopy means edits stay on the copy. Sending the
*link* to the shared file means everyone edits the same document. A pointer is the link.

:::{admonition} In plain words
:class: tip
`&x` means "the address of `x`". `*p` means "the thing `p` points to". `*int` is the type "pointer
to an int". A pointer that points nowhere is `nil`.

**Reach for it when:**

- a function must change its argument
- a struct is large and copying it each call is wasteful
- you need "no value" (a nil pointer) as a possible answer
:::

```{raw} html
:file: ../diagrams/pointer-copy.html
```

## Address and value

`basics.go`

```{literalinclude} ../code/06-pointers/basics.go
:language: go
```

```{literalinclude} ../code/06-pointers/basics.out
:language: text
```

## Pointers and functions

`functions.go`

```{literalinclude} ../code/06-pointers/functions.go
:language: go
```

```{literalinclude} ../code/06-pointers/functions.out
:language: text
```

- `doubleCopy(n)` received its own `n`, so main's `n` stayed 5. `doubleOriginal(&n)` followed the address.
- For structs Go lets you write `u.Name` on a pointer; it means `(*u).Name` automatically.
- `new(int)` returns a pointer to a fresh zero `int`.
- Slices, maps and channels already contain a reference inside, so you rarely need a pointer to one.

## nil pointers

`nil_panic.go`

```{literalinclude} ../code/06-pointers/nil_panic.go
:language: go
```

```{literalinclude} ../code/06-pointers/nil_panic.out
:language: text
```

Reading through a nil pointer crashes the program. Check `if p == nil` before you use a pointer
you did not create yourself. The `recover()` here is only to show the message; normal code does not need it.

## Common mistakes

- **Dereferencing nil.** The classic "invalid memory address" panic.
- **Expecting a function to change a plain argument.** Without a pointer it works on a copy.
- **Pointers to everything.** Use pointers when you need to change something or to avoid copying big values; small values are fine to copy.
- **Returning a pointer to a loop variable** in old Go (before 1.22) shared one variable; modern Go makes a new one per iteration.
- **Confusing `*` in a type and `*` in an expression.** In `p *int` it builds a type; in `*p = 3` it follows the pointer.

## Hands-on exercises

**Exercise 1 · Swap.** Write `swap(a, b *int)` and use it on two variables.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

func swap(a, b *int) {
	*a, *b = *b, *a
}

func main() {
	x, y := 1, 2
	swap(&x, &y)
	fmt.Println(x, y)
}
```

```text
2 1
```

</details>

**Exercise 2 · Birthday.** Write `birthday(p *Person)` that adds one to `Age`.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

type Person struct {
	Name string
	Age  int
}

func birthday(p *Person) {
	p.Age++
}

func main() {
	p := Person{"Asha", 28}
	birthday(&p)
	birthday(&p)
	fmt.Println(p)
}
```

```text
{Asha 30}
```

</details>

**Exercise 3 · Optional value.** Write `find(names []string, target string) *string` that returns a
pointer to the matching element or `nil`, and print a message for both outcomes.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

func find(names []string, target string) *string {
	for i := range names {
		if names[i] == target {
			return &names[i]
		}
	}
	return nil
}

func main() {
	names := []string{"Asha", "Ravi"}
	for _, t := range []string{"Ravi", "Zoe"} {
		if p := find(names, t); p != nil {
			fmt.Println("found", *p)
		} else {
			fmt.Println(t, "not found")
		}
	}
}
```

```text
found Ravi
Zoe not found
```

Return `&names[i]`, not `&n` from a `range` loop copy.

</details>
