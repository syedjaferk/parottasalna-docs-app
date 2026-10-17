# Session 2 · Database and DBMS

## The big idea

A **database** is the organised collection of data. A **DBMS** (Database Management System) is the
software that looks after it: it stores the data on disk, answers questions, enforces rules and lets
many people use it at once. PostgreSQL is a DBMS. The data you create inside it is the database.

**Everyday example:** a library. The books on the shelves and the catalogue are the *database*. The
librarian who finds books, checks them out and makes sure they come back is the *DBMS*. You never walk
into the store room and rearrange the shelves yourself; you ask the librarian.

```{raw} html
:file: ../diagrams/dbms-layers.html
```

## Many programs, one librarian

Your web app, a report script and an admin tool can all use the same data because they all go
through the DBMS. They speak **SQL** (Structured Query Language), and the DBMS decides how to read
and write the files safely. This is why two users can book the last cinema seat at the same moment
and only one succeeds.

## Types of database models

How a DBMS arranges data is called its **model**. Four ideas cover most of what you will meet:

| Model | Shape | Example | Weak point |
|---|---|---|---|
| Hierarchical | A tree: one parent, many children | Folders and files | A book in two genres must be copied |
| Network | A web of links | Social graphs, old mainframes | Gets tangled as links grow |
| **Relational** | Tables linked by keys | PostgreSQL, MySQL, SQLite | Needs planning of tables |
| Document / key-value | JSON blobs or key to value | MongoDB, Redis | Cross-record rules are weaker |

The relational model won for business data because it is flexible and well understood, and it is
what this course teaches.

## See it in a real PostgreSQL

The practice database for the course has four tables. Create it with `code/00-setup.sql`, then ask
PostgreSQL what it holds. `\dt` lists tables, `\d movies` shows a table's columns and rules.

```{literalinclude} ../code/02-explore.sql
:language: sql
```

```{literalinclude} ../code/02-explore.out
:language: text
```

Notice that the DBMS *knows* the shape of your data: column types, which column is the primary key,
which one points at another table. That is the difference from a text file.

## Common mistakes

- **Mixing up "database" and "DBMS".** "PostgreSQL" is the DBMS. `course` (the thing we created) is a
  database. One DBMS can hold many databases.
- **Thinking a model is a product.** "Relational" is an idea; PostgreSQL is one product built on it.
- **Choosing a model by fashion.** If your data has clear relationships (customers have orders), start
  relational. Pick a different model when you have a concrete reason, such as caching with Redis.
- **Editing the database files directly.** Always go through the DBMS. Opening its files in an editor
  can corrupt them.

## Hands-on exercises

**Exercise 1 · Name it.** For each item, say whether it is a database, a DBMS, or neither: PostgreSQL,
the `movies` table, `psql`, the `course` database.

<details class="solution"><summary>Solution</summary>

PostgreSQL is a DBMS. The `movies` table is part of a database (neither on its own). `psql` is a
client program that talks to the DBMS (neither). `course` is a database.

</details>

**Exercise 2 · Choose a model.** A school wants to store students, subjects and marks. Which model
fits best, and why? Draw it as three tables.

<details class="solution"><summary>Solution</summary>

Relational. A student has many marks, a subject has many marks, so use `students(student_id, name)`,
`subjects(subject_id, title)` and `marks(student_id, subject_id, score)`. The `marks` table links the
other two, just like `movie_cast` links movies and actors.

</details>

**Exercise 3 · Explore.** In `psql`, connect to the practice database and find out which column of
`movie_cast` is the primary key and how many rows the table has.

<details class="solution"><summary>Solution</summary>

```sql
\d movie_cast
SELECT count(*) FROM movie_cast;
```

`\d movie_cast` shows a primary key made of two columns, `movie_id` and `actor_id`. The row count is
14 with the setup data (the `02-explore.out` above shows it).

</details>

## Practice

Take the **Session 2 quiz**: database versus DBMS, and the four models.
