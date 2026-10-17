# Session 13 · Databases with database/sql

## The big idea

An in-memory list disappears when the server restarts. A **database** keeps data safe on disk,
lets many programs share it and answers questions fast. Go talks to SQL databases through the
standard `database/sql` package; a small **driver** for your database does the translating.

**Everyday example:** a library. The librarian (the database) keeps the books in order and finds
one quickly. You (the program) hand over a request slip, and you never walk the shelves yourself.

:::{admonition} In plain words
:class: tip
`db, err := sql.Open(driver, connString)`, then `db.Exec` for statements that change data,
`db.Query` for many rows, `db.QueryRow` for one. Pass values as **placeholders**, never glued into the SQL text.

**Reach for it when:**

- data must survive restarts
- several services or users need the same data
- you need filtering, sorting and counting that would be tedious by hand
:::

```{raw} html
:file: ../diagrams/sql-flow.html
```

## Connect, create, insert, query

The course project connects to PostgreSQL with `github.com/lib/pq`. PostgreSQL needs a running server,
so the runnable example here uses **SQLite** in memory (`modernc.org/sqlite`, pure Go, no setup). Only
the `sql.Open` line and the placeholders change between databases: PostgreSQL writes `$1, $2`
instead of `?`.

`db.go`

```{literalinclude} ../code/13-database/db.go
:language: go
```

```{literalinclude} ../code/13-database/db.out
:language: text
```

- `import _ "modernc.org/sqlite"` (the blank `_`) runs the driver's `init`, which registers it with `database/sql`.
- `sql.Open` does **not** connect; `db.Ping()` proves the connection works.
- `Exec` returns a result: `LastInsertId()` and `RowsAffected()`.
- `rows.Next()` loops, `rows.Scan(&a, &b)` copies the columns into variables **in order**. Always `defer rows.Close()`.
- `QueryRow(...).Scan(...)` gives `sql.ErrNoRows` when nothing matches. That is a normal outcome (a 404), not a crash.

For PostgreSQL the connection part from the course looks like this (needs a database server, so not run here):

```go
// no-run: needs a PostgreSQL server
import _ "github.com/lib/pq"

connStr := "host=localhost port=5432 user=app password=... dbname=todo_db sslmode=disable"
db, err := sql.Open("postgres", connStr)
```

:::{warning}
Do not put a real password in source code, as in the original demo. Read it from an environment
variable or a config file that is not committed to git.
:::

## Plugging it into the API

In the `todo_db` project, the storage layer from Session 12 is replaced by SQL: the `POST` handler
calls `INSERT ... RETURNING id`, and `GET` runs `SELECT`. The handlers barely change, because they
only used the storage's methods. That is the payoff of keeping layers separate.

## Common mistakes

- **Building SQL with `+` or `fmt.Sprintf`.** That is SQL injection. Use placeholders.
- **Forgetting `rows.Close()`.** The connection stays busy and the pool runs out.
- **Ignoring `rows.Err()`.** Check it after the loop for errors that ended the iteration.
- **Scanning into the wrong types or order.** The columns must match your variables.
- **Treating `ErrNoRows` as a failure.** It means "not found".
- **`log.Fatal` in library code.** Fine in `main`, but a library should return the error.
- **Committing the password.**

## Hands-on exercises

The solutions use the in-memory SQLite database so you can run them anywhere.

**Exercise 1 · Count rows.** Create a `books(title TEXT)` table, insert two rows and print the count with `QueryRow`.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "modernc.org/sqlite"
)

func main() {
	db, err := sql.Open("sqlite", ":memory:")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	db.Exec("CREATE TABLE books (title TEXT)")
	db.Exec("INSERT INTO books VALUES (?)", "Go in Action")
	db.Exec("INSERT INTO books VALUES (?)", "The Go Programming Language")

	var n int
	db.QueryRow("SELECT COUNT(*) FROM books").Scan(&n)
	fmt.Println(n, "books")
}
```

```text
2 books
```

</details>

**Exercise 2 · Not found.** Write `getTitle(db, id)` that returns the title or `"not found"` when `ErrNoRows` happens.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"database/sql"
	"errors"
	"fmt"
	"log"

	_ "modernc.org/sqlite"
)

func getTitle(db *sql.DB, id int) string {
	var title string
	err := db.QueryRow("SELECT title FROM books WHERE id = ?", id).Scan(&title)
	if errors.Is(err, sql.ErrNoRows) {
		return "not found"
	}
	if err != nil {
		return "error: " + err.Error()
	}
	return title
}

func main() {
	db, err := sql.Open("sqlite", ":memory:")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()
	db.Exec("CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT)")
	db.Exec("INSERT INTO books (title) VALUES (?)", "Go in Action")

	fmt.Println(getTitle(db, 1))
	fmt.Println(getTitle(db, 5))
}
```

```text
Go in Action
not found
```

</details>

**Exercise 3 · Transaction.** Insert two rows inside a transaction, then roll it back, and show the table is still empty.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "modernc.org/sqlite"
)

func main() {
	db, err := sql.Open("sqlite", ":memory:")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()
	db.SetMaxOpenConns(1) // an in-memory SQLite database lives per connection
	db.Exec("CREATE TABLE items (name TEXT)")

	tx, err := db.Begin()
	if err != nil {
		log.Fatal(err)
	}
	tx.Exec("INSERT INTO items VALUES (?)", "a")
	tx.Exec("INSERT INTO items VALUES (?)", "b")
	tx.Rollback() // use tx.Commit() to keep the changes

	var n int
	db.QueryRow("SELECT COUNT(*) FROM items").Scan(&n)
	fmt.Println("rows after rollback:", n)
}
```

```text
rows after rollback: 0
```

A transaction makes several statements succeed or fail **together**, for example moving money between accounts.

</details>
