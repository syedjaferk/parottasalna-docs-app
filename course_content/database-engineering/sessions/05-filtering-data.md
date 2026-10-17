# Session 5 · Filtering rows with WHERE

## The big idea

A table can have millions of rows and you usually want a few. `WHERE` keeps only the rows that
match a condition. You build conditions with comparisons (`=`, `>`), logic (`AND`, `OR`, `NOT`) and
helpers (`IN`, `BETWEEN`, `LIKE`, `IS NULL`). `LIMIT` then trims how many come back.

**Everyday example:** a shop's search page. "Phones, under 20,000, brand Samsung or Redmi." Each
filter you tick throws away products until a short list is left. SQL filters do exactly this.

```{raw} html
:file: ../diagrams/filter-funnel.html
```

## The queries

All of these ran against the practice database. Read the SQL, then the output below it.

```{literalinclude} ../code/05-filter.sql
:language: sql
```

```{literalinclude} ../code/05-filter.out
:language: text
```

## What to notice

- **`AND` narrows, `OR` widens.** Four Action movies; adding `year > 2000` leaves three.
- **`IN (1995, 2021)`** is shorthand for `year = 1995 OR year = 2021`.
- **`BETWEEN 8.0 AND 8.5` includes both ends.** Karnan (8.0) and Thalapathi (8.5) are in the result.
- **`LIKE 'S%'`**: `%` means "any characters", `_` means exactly one. `LIKE` is case-sensitive;
  `ILIKE` is not, which is why `ILIKE '%pottru'` matched "Soorarai Pottru".
- **`= NULL` returns nothing, even though a row has NULL.** `NULL` means "unknown", and "unknown
  equals unknown" is not true. Use `IS NULL` / `IS NOT NULL`.
- **`LIMIT 3`** gives the top three; `OFFSET 3 FETCH FIRST 2 ROWS ONLY` skips three and takes the
  next two (the standard SQL spelling of `LIMIT 2 OFFSET 3`). Always pair them with `ORDER BY`.
- **`AND` is evaluated before `OR`.** The last two queries use the same words but return 6 and 5
  rows. In the first, Thalapathi (a 1991 drama) sneaks in because it only had to satisfy
  `genre = 'Drama'`. Parentheses make your intent explicit.

## A mental model for conditions

Think of `WHERE` as a test the database runs on **each row, one at a time**. The row either passes
(the condition is true) and goes into the result, or it fails and is skipped. Three outcomes are
possible, not two: *true*, *false*, and *unknown*. A comparison with `NULL` is unknown, and `WHERE`
only keeps rows where the answer is **true**. That is the whole reason `genre = NULL` returns nothing
and why `NOT IN` misbehaves around `NULL`.

When a query gives surprising rows, test the pieces. Run `SELECT title, genre, year FROM movies`
first, look at the data, then add one condition at a time and watch how the row count shrinks (11,
then 4, then 3 in the diagram above). Building filters step by step is quicker than guessing.

## Common mistakes

- **`WHERE genre = NULL`.** Always empty. Use `IS NULL`.
- **Forgetting parentheses around mixed `AND`/`OR`**, as the last two queries show.
- **`LIKE '%word'` on a huge table.** A leading `%` cannot use a normal index and is slow.
- **Using double quotes for text.** `WHERE genre = "Action"` fails; text values use single quotes.
- **`LIMIT` without `ORDER BY`.** You get *some* rows, not the top ones.
- **Using `NOT IN` with a NULL in the list.** The result is empty. Prefer `NOT EXISTS`.

## Hands-on exercises

**Exercise 1.** Find movies from before 2000 that are not Drama.

<details class="solution"><summary>Solution</summary>

```sql
SELECT title, genre, year FROM movies WHERE year < 2000 AND genre <> 'Drama' ORDER BY year;
```

Expected rows: Nayakan (Crime), Baasha (Action) and Muthu (Comedy).

</details>

**Exercise 2.** Find every movie whose title contains the letters `ra` anywhere, ignoring case.

<details class="solution"><summary>Solution</summary>

```sql
SELECT title FROM movies WHERE title ILIKE '%ra%' ORDER BY title;
```

`%ra%` matches "ra" at any position. It returns two rows: Soorarai Pottru and Vikram.

</details>

**Exercise 3.** Show the third and fourth best rated movies.

<details class="solution"><summary>Solution</summary>

```sql
SELECT title, rating FROM movies
WHERE rating IS NOT NULL
ORDER BY rating DESC
OFFSET 2 FETCH FIRST 2 ROWS ONLY;
```

Skip two rows, take two: Soorarai Pottru (8.6) and Thalapathi (8.5). The `IS NOT NULL` filter keeps the unrated movie out of the ranking.

</details>

## Practice

Take the **Session 5 quiz**. For more operators (`SIMILAR TO`, `ESCAPE`) see the reference pages
under *Filtering Data*.
