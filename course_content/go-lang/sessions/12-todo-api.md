# Session 12 · Project: a Todo REST API

## Watch the class

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/NJ7Xd6rgpH8"
  title="Day 15 | Learn Go by Building | TODO API with net/http &amp; In-Memory Storage" loading="lazy" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

## The big idea

A **REST API** is a set of URLs where the *verb* says what to do and the *noun* (the URL) says what
to do it to: `GET /todos` lists, `POST /todos` creates. Data goes in and out as JSON. This session
puts together everything so far (structs, JSON, slices, errors, HTTP) into a small but real service.

**Everyday example:** a shared shopping list on the fridge. Anyone can read it (GET) or add a line
(POST). The list lives in one place, and everyone sees the same version.

:::{admonition} In plain words
:class: tip
Split the program by job: **models** (the shapes of the data), **storage** (where it lives),
**handlers** (translate HTTP to storage calls), **main** (wire the routes). Each handler: decode
the request, do the work, encode the response with the right status code.

**Reach for it when:**

- a front-end, mobile app or script needs your data
- you want a clean split so storage can change later (memory → database)
:::

```{raw} html
:file: ../diagrams/todo-layers.html
```

## The whole API in one file

The course project spreads this over `models.go`, `storage.go`, `handles.go` and `main.go`. Here it is
in a single runnable file so you can read it top to bottom; the sections are marked and split the same way.
It starts a test server and calls it, so the output is real.

`todo.go`

```{literalinclude} ../code/12-todo-api/todo.go
:language: go
```

```{literalinclude} ../code/12-todo-api/todo.out
:language: text
```

What to notice:

- `POST` answers **201 Created** and returns the new item including its server-chosen `id`.
- A `{}` body gives **400** because the title is missing. Validate before you store.
- An unknown path gives **404**. The `"/"` route is a catch-all, so `Home` checks `r.URL.Path`.
- The original code keeps `todos` and `nextID` as **global variables**. Here they live inside a
  `Store` struct protected by a `sync.Mutex`: a server handles many requests at once, so unprotected
  shared data would be a race (Session 16).
- `writeJSON` is a tiny helper so every handler sets the header and status the same way.

To run it as a real service, replace `httptest.NewServer(mux)` with
`http.ListenAndServe(":8081", mux)` and use `curl`:

```bash
curl -X POST -d '{"title":"Learn Go"}' localhost:8081/todos
curl localhost:8081/todos
```

## Where to go next

The course continues by adding `PUT /todos/{id}` and `DELETE /todos/{id}`. Since Go 1.22 the router
understands patterns like these directly:

```go
// no-run: fragment, not a full program
mux.HandleFunc("GET /todos/{id}", api.GetOne)   // r.PathValue("id")
mux.HandleFunc("DELETE /todos/{id}", api.Delete)
```

## Common mistakes

- **Returning 200 for everything.** Clients rely on 201, 400, 404.
- **Nil slice encodes as `null`.** That is why `NewStore` starts with `[]Todo{}`: the first `GET` returns `[]`.
- **Sharing the internal slice.** `List` returns a copy so callers cannot change the store behind its lock.
- **Global state.** Fine in a demo, painful in tests. A `Store` struct can be created fresh per test.
- **Ignoring `Content-Type`.** Clients may not parse the body.
- **IDs from `len(todos)+1`.** They repeat after a delete; keep a counter.

## Hands-on exercises

**Exercise 1 · Mark complete.** Add a `Complete(id int) bool` method to a store that sets `Completed` to true and reports whether the id existed.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

type Todo struct {
	ID        int
	Title     string
	Completed bool
}

type Store struct{ todos []Todo }

func (s *Store) Complete(id int) bool {
	for i := range s.todos {
		if s.todos[i].ID == id {
			s.todos[i].Completed = true
			return true
		}
	}
	return false
}

func main() {
	s := &Store{todos: []Todo{{1, "Learn Go", false}, {2, "Relax", false}}}
	fmt.Println(s.Complete(2), s.Complete(9))
	fmt.Printf("%+v\n", s.todos)
}
```

```text
true false
[{ID:1 Title:Learn Go Completed:false} {ID:2 Title:Relax Completed:true}]
```

Index with `s.todos[i]`, not the `range` copy, or the change would be lost.

</details>

**Exercise 2 · Delete.** Add `Delete(id int) bool` that removes an item from the slice.

<details class="solution"><summary>Solution</summary>

```go
package main

import "fmt"

type Todo struct {
	ID    int
	Title string
}

type Store struct{ todos []Todo }

func (s *Store) Delete(id int) bool {
	for i, t := range s.todos {
		if t.ID == id {
			s.todos = append(s.todos[:i], s.todos[i+1:]...)
			return true
		}
	}
	return false
}

func main() {
	s := &Store{todos: []Todo{{1, "a"}, {2, "b"}, {3, "c"}}}
	fmt.Println(s.Delete(2), s.Delete(7))
	fmt.Println(s.todos)
}
```

```text
true false
[{1 a} {3 c}]
```

</details>

**Exercise 3 · Test a handler.** Using `httptest`, send `POST /todos` with an empty title to a handler and check that the status is 400.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
)

func create(w http.ResponseWriter, r *http.Request) {
	var req struct{ Title string }
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.Title == "" {
		http.Error(w, "title is required", http.StatusBadRequest)
		return
	}
	w.WriteHeader(http.StatusCreated)
}

func main() {
	for _, body := range []string{`{"title":""}`, `{"Title":"Learn Go"}`} {
		rec := httptest.NewRecorder()
		create(rec, httptest.NewRequest("POST", "/todos", strings.NewReader(body)))
		fmt.Println(rec.Code)
	}
}
```

```text
400
201
```

</details>
