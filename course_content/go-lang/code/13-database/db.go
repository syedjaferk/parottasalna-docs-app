package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "modernc.org/sqlite" // driver, registered by its import side effect
)

type Todo struct {
	ID        int
	Title     string
	Completed bool
}

func main() {
	// With Postgres you would write sql.Open("postgres", connStr) and import github.com/lib/pq.
	// Everything below this line stays the same.
	db, err := sql.Open("sqlite", ":memory:")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()
	if err := db.Ping(); err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec(`CREATE TABLE todos (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		title TEXT NOT NULL,
		completed BOOLEAN NOT NULL DEFAULT 0)`)
	if err != nil {
		log.Fatal(err)
	}

	// placeholders (?) keep user input out of the SQL text: no SQL injection
	for _, title := range []string{"Learn Go", "Build an API", "Ship it"} {
		res, err := db.Exec("INSERT INTO todos (title) VALUES (?)", title)
		if err != nil {
			log.Fatal(err)
		}
		id, _ := res.LastInsertId()
		fmt.Println("inserted id", id)
	}

	db.Exec("UPDATE todos SET completed = 1 WHERE id = ?", 1)

	rows, err := db.Query("SELECT id, title, completed FROM todos ORDER BY id")
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()
	for rows.Next() {
		var t Todo
		if err := rows.Scan(&t.ID, &t.Title, &t.Completed); err != nil {
			log.Fatal(err)
		}
		fmt.Printf("%+v\n", t)
	}

	// QueryRow for exactly one row
	var title string
	err = db.QueryRow("SELECT title FROM todos WHERE id = ?", 2).Scan(&title)
	fmt.Println(title, err)

	err = db.QueryRow("SELECT title FROM todos WHERE id = ?", 99).Scan(&title)
	fmt.Println(err, err == sql.ErrNoRows)

	res, _ := db.Exec("DELETE FROM todos WHERE completed = 1")
	n, _ := res.RowsAffected()
	fmt.Println("deleted", n)
}
