# Session 5 · Structs, methods and JSON

## The big idea

A **struct** bundles related facts into one thing with named fields: a person is a name, an age
and an address, not three loose variables. Add **methods** and the struct can also *do* things.
Structs also map neatly onto **JSON**, the format almost every web API speaks.

**Everyday example:** a form with labelled boxes: Name, Age, Address. Each box has a name and
holds one kind of answer. Filling the form is creating a struct value.

:::{admonition} In plain words
:class: tip
`type Person struct { Name string; Age int }` defines the shape. `p := Person{Name: "Asha"}` makes
one. `func (p Person) Greet()` attaches a method. Put a tag like `` `json:"name"` `` after a field
to control its JSON name.

**Reach for it when:**

- several values always travel together
- you are reading or writing JSON
- you want behaviour next to the data it works on
:::

## Defining and using structs

`basic.go`

```{literalinclude} ../code/05-structs/basic.go
:language: go
```

```{literalinclude} ../code/05-structs/basic.out
:language: text
```

- Fields you do not set get their zero value (the last line).
- Structs can contain other structs; reach inside with `p.Address.City`.
- A method is a function with a **receiver** in front of the name: `(p Person)`.
- Fields and methods starting with a **capital letter** are visible to other packages; lowercase
  ones are private to the package.

## Value or pointer receiver?

`pointer_receiver.go`

```{literalinclude} ../code/05-structs/pointer_receiver.go
:language: go
```

```{literalinclude} ../code/05-structs/pointer_receiver.out
:language: text
```

A value receiver works on a **copy**, so `IncByValue` lost its change. A pointer receiver
(`*Counter`) changes the original. Rule of thumb: if any method needs to change the struct, use
pointer receivers for all of them. (Pointers get a whole session next.)

## Structs and JSON

```{raw} html
:file: ../diagrams/struct-json.html
```

`json.go`

```{literalinclude} ../code/05-structs/json.go
:language: go
```

```{literalinclude} ../code/05-structs/json.out
:language: text
```

- `json.Marshal` turns a struct into JSON bytes; `json.Unmarshal(data, &target)` fills a struct.
  Pass the **address** (`&u`) so Unmarshal can write into it.
- The `json:"name"` tag sets the key. `omitempty` leaves a field out when it is empty.
- Only **exported** (capitalised) fields appear in JSON, which is why `token` never shows.
- Always check the error: the last line shows what a type mismatch looks like.

## Common mistakes

- **Lowercase field names with JSON.** `name string` is invisible to the `json` package, so you get
  empty output and no error.
- **Forgetting `&` in `Unmarshal`.** Passing the struct instead of its address changes nothing (and returns an error).
- **Ignoring the error from `Unmarshal`.** Bad input silently leaves zero values.
- **Mixing value and pointer receivers** on one type; pick one style.
- **Comparing structs holding slices or maps with `==`.** It will not compile. Use `reflect.DeepEqual`.

## Hands-on exercises

**Exercise 1 · Rectangle.** Create `Rectangle{W, H float64}` with methods `Area()` and `Perimeter()`.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

type Rectangle struct{ W, H float64 }

func (r Rectangle) Area() float64      { return r.W * r.H }
func (r Rectangle) Perimeter() float64 { return 2 * (r.W + r.H) }

func main() {
	r := Rectangle{W: 3, H: 4}
	fmt.Println(r.Area(), r.Perimeter())
}
```

```text
12 14
```

</details>

**Exercise 2 · Bank account.** `Account` with `Balance`, and a pointer-receiver `Deposit(n)`. Show
that two deposits add up.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

type Account struct{ Balance float64 }

func (a *Account) Deposit(n float64) { a.Balance += n }

func main() {
	acc := Account{}
	acc.Deposit(100)
	acc.Deposit(50.5)
	fmt.Println(acc.Balance)
}
```

```text
150.5
```

Go takes the address of `acc` for you when you call a pointer method on a variable.

</details>

**Exercise 3 · Parse a list.** Decode `[{"title":"Learn Go","done":true},{"title":"Relax","done":false}]`
into `[]Task` and print how many are done.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"encoding/json"
	"fmt"
)

type Task struct {
	Title string `json:"title"`
	Done  bool   `json:"done"`
}

func main() {
	data := `[{"title":"Learn Go","done":true},{"title":"Relax","done":false}]`
	var tasks []Task
	if err := json.Unmarshal([]byte(data), &tasks); err != nil {
		fmt.Println(err)
		return
	}
	done := 0
	for _, t := range tasks {
		if t.Done {
			done++
		}
	}
	fmt.Println(len(tasks), "tasks,", done, "done")
}
```

```text
2 tasks, 1 done
```

</details>
