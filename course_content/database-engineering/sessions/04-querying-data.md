# Session 4 · Querying data with SELECT

## The big idea

`SELECT` is how you ask the database a question. You say **which columns** you want and **which
table** to read them from. You can rename columns, calculate new ones, sort the result and remove
repeats. The table itself is never changed: SELECT only reads.

**Everyday example:** a railway enquiry counter. You do not carry the whole timetable home. You ask
"trains from Chennai, show name and departure time, earliest first," and the clerk reads out just that.
`SELECT name, departure FROM trains ORDER BY departure` is the same request in SQL.

```{raw} html
:file: ../diagrams/select-flow.html
```

## The practice queries

Each query below was run against the movie database from `code/00-setup.sql`. The `\echo` lines just
print a label so you can match each result to its query.

```{literalinclude} ../code/04-select.sql
:language: sql
```

## Real output

```{literalinclude} ../code/04-select.out
:language: text
```

## What each part did

- **`SELECT title FROM movies`** returns one column from every row. `SELECT *` returns all columns;
  it is handy in a console but in application code list the columns you need, so a new column added
  later cannot break your program.
- **`AS`** gives a column a nicer name in the result (`film`, `released`). The stored column is not
  renamed.
- **Calculated columns**: `2026 - year AS age_in_years` is computed for each row on the fly.
- **`ORDER BY year DESC, title ASC`** sorts by year first, then breaks ties by title. Without
  `ORDER BY` the order of rows is **not guaranteed**.
- **`SELECT DISTINCT genre`** shows each genre once. `DISTINCT` on two columns removes duplicate
  *pairs*; the last query shows Comedy and Action for 1995, each once.

Read the diagram above as the order the database *thinks* in: table first, then rows, then columns,
then sorting. That is why an alias defined in `SELECT` can be used in `ORDER BY` but not in `WHERE`.

## Common mistakes

- **Forgetting the semicolon in `psql`.** The prompt changes to `course-#` and waits for more. Type
  `;` and Enter.
- **Trusting row order without `ORDER BY`.** It looks sorted on your laptop and changes in production.
- **Using `SELECT *` in application code.** You pull unneeded data, and your code breaks when the
  table changes.
- **Single versus double quotes.** `'Action'` is a text value; `"Action"` is an identifier (a column
  name). Mixing them gives "column does not exist".
- **Thinking `DISTINCT` applies to one column.** It applies to the whole row you selected.

## Hands-on exercises

**Exercise 1.** Show every movie's `title` and `rating`, best rated first. What happens to the movie
that has no rating?

<details class="solution"><summary>Solution</summary>

```sql
SELECT title, rating FROM movies ORDER BY rating DESC;
```

In PostgreSQL `NULL` sorts **first** in a descending sort, so "Untitled Project" appears at the top, then Nayakan (9.0).
Use `ORDER BY rating DESC NULLS LAST` to push it to the bottom.

</details>

**Exercise 2.** List the different release years once each, oldest first.

<details class="solution"><summary>Solution</summary>

```sql
SELECT DISTINCT year FROM movies ORDER BY year;
```

1995 appears once even though two movies came out that year.

</details>

**Exercise 3.** Show `title` as `film` and a new column `decade` that is the year rounded down to
the decade (1987 gives 1980).

<details class="solution"><summary>Solution</summary>

```sql
SELECT title AS film, (year / 10) * 10 AS decade FROM movies ORDER BY decade, film;
```

Both numbers are integers, so `year / 10` drops the fraction (198.7 becomes 198), and `* 10` brings
it back to 1980.

</details>

## Practice

Take the **Session 4 quiz** (SELECT, aliases, ORDER BY, DISTINCT). The original DB-TASK-001 on the
DVD Rental database is in the reference section of the course.
