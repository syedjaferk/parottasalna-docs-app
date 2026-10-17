# Session 7 · Joins

## The big idea

Good design splits data across tables, so to answer real questions you **join** them back together.
A join matches rows from two tables using a condition (usually *foreign key = primary key*) and
returns them side by side. The kind of join decides what happens to rows that find no match.

**Everyday example:** a class register and a fee register. The register lists names; the fee register
lists payments by roll number. To see "name next to amount paid" you line them up by roll number.
Students who have not paid are the interesting case: do you still list them (with a blank amount) or
leave them out? That choice is `LEFT JOIN` versus `INNER JOIN`.

```{raw} html
:file: ../diagrams/join-types.html
```

## The queries

```{literalinclude} ../code/07-joins.sql
:language: sql
```

```{literalinclude} ../code/07-joins.out
:language: text
```

## Reading the results

- **`INNER JOIN ... ON d.director_id = m.director_id`** returned 10 rows. "Untitled Project" has no
  director and "Vetrimaaran" has no movie, so neither appears.
- **`LEFT JOIN`** keeps every row from the *left* table (`movies`). "Untitled Project" is still there,
  with an empty director (`NULL`).
- **Finding what is missing**: `LEFT JOIN ... WHERE m.movie_id IS NULL` lists directors with no
  movies. This "anti-join" pattern answers "who has never...?" questions.
- **Three tables** joined through the link table list Vikram's four actors.
- **`LEFT JOIN` plus `GROUP BY`** counts movies per director, including a zero for Vetrimaaran. Counting
  `m.movie_id` (not `*`) is what makes the zero correct.
- **The last two queries** show the most common bug. Without an `ON`, every movie pairs with every
  director: 11 x 8 = 88 rows. With the `ON`, 10.

## Aliases make joins readable

`movies m` and `directors d` are short names (aliases) for the tables. They save typing and are
required when the same table appears twice. Prefix columns with the alias (`m.title`) so the reader
and the database both know which table you mean.

## Common mistakes

- **Forgetting the `ON` condition.** You get a "cartesian product", every row paired with every row
  (88 here). If a result is suspiciously huge, check your joins first.
- **Using `INNER JOIN` when you needed to keep the unmatched rows.** Rows silently disappear.
- **Filtering a `LEFT JOIN` in `WHERE` on the right table**, e.g. `WHERE d.name = 'X'`, which turns it
  back into an inner join. Put such conditions in the `ON` clause instead.
- **Selecting a column that exists in both tables without a prefix.** PostgreSQL says "column
  reference is ambiguous".
- **`count(*)` after a left join.** It counts the NULL row as 1. Count a column from the right table.

## Hands-on exercises

**Exercise 1.** List every movie with its director's name, showing only movies released after 2018.

<details class="solution"><summary>Solution</summary>

```sql
SELECT m.title, d.name AS director, m.year
FROM movies m JOIN directors d ON d.director_id = m.director_id
WHERE m.year > 2018
ORDER BY m.year;
```

</details>

**Exercise 2.** Which actors have never been cast in a movie? (Hint: left join and look for NULL.)

<details class="solution"><summary>Solution</summary>

```sql
SELECT a.name
FROM actors a LEFT JOIN movie_cast mc ON mc.actor_id = a.actor_id
WHERE mc.movie_id IS NULL;
```

With the practice data every actor has at least one movie, so this returns no rows. Insert a new
actor first to see it work.

</details>

**Exercise 3.** Show each actor and how many movies they appear in, most first.

<details class="solution"><summary>Solution</summary>

```sql
SELECT a.name, count(mc.movie_id) AS movies
FROM actors a LEFT JOIN movie_cast mc ON mc.actor_id = a.actor_id
GROUP BY a.name
ORDER BY movies DESC, a.name;
```

Rajinikanth comes first with 4 movies.

</details>

## Practice

Take the **Session 7 quiz** on join types. Extra worked examples (employees and departments) are in
the reference section.
