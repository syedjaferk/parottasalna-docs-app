# Session 3 · The relational model

## The big idea

In the relational model all data lives in **tables**. A table has **columns** (what you know about
each thing) and **rows** (one thing each). Tables are linked by **keys**: a **primary key** identifies
a row, and a **foreign key** is a column that stores another table's primary key. Rules called
**integrity constraints** make sure the data stays correct.

**Everyday example:** a library again. The `books` shelf is a table; each book is a row; the ISBN is
its primary key. A borrowing slip says "ISBN 978-..., member card 42". The slip does not copy the
book's title or the member's address; it points to them. If the ISBN or card did not exist, the
librarian would refuse the slip. That refusal is referential integrity.

```{raw} html
:file: ../diagrams/relational-keys.html
```

## Tables, rows, columns, keys

| Idea | Library | In our database |
|---|---|---|
| Table | A bookshelf | `movies`, `directors` |
| Row | One book | `Nayakan, 1987, Crime` |
| Column | A field on the card | `title`, `year` |
| Primary key | ISBN | `movie_id` |
| Foreign key | A reference to another book | `movies.director_id` |

A good primary key never repeats and is never empty. `SERIAL` in PostgreSQL gives a counter that
fills it for you.

## The four kinds of integrity, tried for real

`code/03-integrity.sql` tries to break each rule on purpose. PostgreSQL refuses every bad row.

```{literalinclude} ../code/03-integrity.sql
:language: sql
```

```{literalinclude} ../code/03-integrity.out
:language: text
```

Match each error to its kind:

- **Entity integrity**: duplicate primary key `1` was refused. Every row must be unique and findable.
- **Referential integrity**: director `99` does not exist, so a movie cannot point at it. The last
  delete is the reverse: Mani Ratnam is still referenced by two movies, so he cannot be removed.
- **Domain integrity**: `year` must pass `CHECK (year > 1900)`, and `title` is `NOT NULL`.
- **User-defined rules** are just constraints you write yourself, like that `CHECK`.

One surprise in the output: the valid insert got `movie_id` 15, not 12. Each failed attempt used up
a number from the `SERIAL` counter. Gaps in ids are normal and harmless; never rely on them being
continuous.

## Normalisation in one paragraph

Notice we did not put the director's name in `movies`. We stored it once in `directors` and pointed
to it. Splitting data so each fact is stored once is called **normalisation**. It stops the "rename
in two thousand places" problem from Session 1.

## Common mistakes

- **Using a person's name as the primary key.** Names repeat and change. Use a plain id.
- **Skipping the foreign key.** Without `REFERENCES`, nothing stops `director_id = 99`. The column
  would be a number the database does not understand.
- **Storing the same fact twice** (director name inside `movies` as well). One of the copies will
  eventually be out of date.
- **Expecting ids with no gaps.** Rolled-back or failed inserts consume numbers.
- **Treating `NULL` as zero or empty text.** `NULL` means "unknown"; it behaves differently (Session 5).

## Hands-on exercises

**Exercise 1 · Pick keys.** For a `students` table with `roll_no`, `name`, `email`, which column
should be the primary key and why?

<details class="solution"><summary>Solution</summary>

`roll_no`, if the school guarantees it is unique and never reused. `name` repeats; `email` can
change. If you cannot guarantee a natural key, add a `student_id SERIAL` instead.

</details>

**Exercise 2 · Break a rule.** Try to insert an actor with no name into the practice database. Which
error do you get?

<details class="solution"><summary>Solution</summary>

```sql
INSERT INTO actors (name) VALUES (NULL);
```

PostgreSQL answers with a "null value in column "name" ... violates not-null constraint" error,
because `actors.name` was declared `NOT NULL`.

</details>

**Exercise 3 · Design.** Write the `CREATE TABLE` for a `reviews` table: each review belongs to one
movie, has a score from 1 to 10 and optional text.

<details class="solution"><summary>Solution</summary>

```sql
CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    movie_id  INT NOT NULL REFERENCES movies(movie_id),
    score     INT NOT NULL CHECK (score BETWEEN 1 AND 10),
    comment   TEXT
);
```

The foreign key ties each review to a real movie; the `CHECK` keeps scores in range.

</details>

## Practice

Take the **Session 3 quiz**: keys and the four kinds of integrity.
