# SELECT DISTINCT

> 📌 Note: This tutorial uses the dvdrental database. If you dont have the dvdrental, please go through this [https://courses.parottasalna.com/database-engineering/sample-databases/dvd-rental-database](https://courses.parottasalna.com/database-engineering/sample-databases/dvd-rental-database)

The `SELECT DISTINCT` removes duplicate rows from a result set. The `SELECT DISTINCT` clause retains one row for each group of duplicates.

The `SELECT DISTINCT` clause can be applied to one or more columns in the select list of the [`SELECT`](https://neon.tech/postgresql/postgresql-tutorial/postgresql-select) statement.

The following illustrates the syntax of the `DISTINCT` clause.

```sql
SELECT
  DISTINCT column1
FROM
  table_name;
```

In this syntax, the `SELECT DISTINCT` uses the values in the `column1` column to evaluate the duplicate.

If you specify multiple columns, the `SELECT DISTINCT` clause will evaluate the duplicate based on the combination of values in these columns. For example,

```sql
SELECT
   DISTINCT column1, column2
FROM
   table_name;
```

In this syntax, the `SELECT DISTINCT` uses the combination of values in both `column1` and `column2` columns for evaluating the duplicate.



### PostgreSQL SELECT DISTINCT examples

Let's create a new table for practice the `SELECT DISTINCT` clause.

First, create the `colors` table that has three columns: `id`, `bcolor` and `fcolor` using the following `CREATE TABLE` statement,

```sql
CREATE TABLE colors(
  id SERIAL PRIMARY KEY,
  bcolor VARCHAR,
  fcolor VARCHAR
);
```

Let's insert some data into it,&#x20;

```sql
INSERT INTO
  colors (bcolor, fcolor)
VALUES
  ('red', 'red'),
  ('red', 'red'),
  ('red', NULL),
  (NULL, 'red'),
  (NULL, NULL),
  ('green', 'green'),
  ('blue', 'blue'),
  ('blue', 'blue');
```

Third, retrieve the data from the `colors` table using the SELECT statement.&#x20;

```sql
SELECT
  id,
  bcolor,
  fcolor
FROM
  colors;
```

```
id | bcolor | fcolor
----+--------+--------
  1 | red    | red
  2 | red    | red
  3 | red    | null
  4 | null   | red
  5 | null   | null
  6 | green  | green
  7 | blue   | blue
  8 | blue   | blue
(8 rows)
```



### 1. PostgreSQL SELECT DISTINCT one column example

The following statement selects unique values from the `bcolor` column of the `t1` table and sorts the result set in alphabetical order by using the ORDER BY clause.

```sql
SELECT
  DISTINCT bcolor
FROM
  colors
ORDER BY
  bcolor;
```

Output:

```
bcolor
--------
 blue
 green
 red
 null
(4 rows)
```

The `bcolor` column has 3 red values, two NULL, 1 green value, and two blue values. The `DISTINCT` removes two red values, 1 NULL, and one blue.

Note that PostgreSQL treats `NULL`s as duplicates so that it keeps one `NULL` for all `NULL`s when you apply the `SELECT DISTINCT` clause.

### 2. SELECT DISTINCT on multiple columns

The following statement applies the `SELECT DISTINCT` clause to both `bcolor` and `fcolor` columns

```sql
SELECT
  DISTINCT bcolor, fcolor
FROM
  colors
ORDER BY
  bcolor,
  fcolor;
```

Output,&#x20;

```
bcolor | fcolor
--------+--------
 blue   | blue
 green  | green
 red    | red
 red    | null
 null   | red
 null   | null
(6 rows)
```

In this example, the query uses the values from both `bcolor` and `fcolor` columns to evaluate the uniqueness of rows.

### 3. Using the SELECT DISTINCT clause in practice

In practice, you often use the `SELECT DISTINCT` clause to analyze the uniqueness of values in a column.

For example, you may want to know how many rental rates for films from the `film` table,

To achieve this, you can specify the `rental_rate` column in the `SELECT DISTINCT` clause as follows,


```sql
SELECT DISTINCT
  rental_rate
FROM
  film
ORDER BY
  rental_rate;
```



![](/_assets/image-46.png)


The output indicates that there are only three distinct rental rates 0.99, 2.99, and 4.99.
