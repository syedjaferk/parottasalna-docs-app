# FETCH

### Introduction to PostgreSQL FETCH clause

To skip a certain number of rows and retrieve a specific number of rows, you often use the [`LIMIT`](https://neon.tech/postgresql/postgresql-tutorial/postgresql-limit) clause in the `SELECT` statement.

The `LIMIT` clause is widely used by many Relational Database Management Systems such as MySQL, H2, and HSQLDB. However, the `LIMIT` clause is not a SQL standard.

To conform with the SQL standard, PostgreSQL supports the `FETCH` clause to skip a certain number of rows and then fetch a specific number of rows.

> Note that the `FETCH` clause was introduced as a part of the SQL standard in SQL:2008.

The following illustrates the syntax of the PostgreSQL `FETCH` clause

```sql
OFFSET row_to_skip { ROW | ROWS }
FETCH { FIRST | NEXT } [ row_count ] { ROW | ROWS } ONLY
```

1. **Skipping Rows (OFFSET):**
   * The `OFFSET` keyword tells the database how many rows to skip before it starts showing results.
   * The number you provide (`row_to_skip`) must be a whole number (0 or more).
   * If you don’t provide a number, it will default to 0, meaning no rows will be skipped.
   * **Example:** If there are 10 rows and you skip 15, you’ll see no rows because you’ve skipped past all the data.
2. **Getting Rows (FETCH):**
   * The `FETCH` keyword tells the database how many rows to return after skipping.
   * The number (`row_count`) must be 1 or more, and it defaults to 1 if you don’t provide it.
   * You can use `FIRST` or `NEXT` with `ROW` or `ROWS` (e.g., `FETCH FIRST 3 ROWS` is the same as `FETCH NEXT 3 ROWS`).
3. **Ordering Rows (ORDER BY):**
   * Tables don’t store rows in a specific order, so results without an `ORDER BY` clause can appear in a random order.
   * Always use `ORDER BY` with `FETCH` to control which rows you get.
4. **Order of Clauses:**
   * In SQL standards (like SQL:2008), `OFFSET` comes before `FETCH`.
   * PostgreSQL is flexible and allows you to write them in any order.

#### Example

```sql
SELECT * FROM employees
ORDER BY salary DESC
OFFSET 5 FETCH NEXT 3 ROWS;
```

* **Step 1:** Sort employees by highest to lowest salary.
* **Step 2:** Skip the first 5 employees.
* **Step 3:** Show the next 3 employees.

If you skip `ORDER BY`, you might get a random set of rows, which could be confusing.
