# Order By

> 📌 Note: This tutorial uses the dvdrental database. If you dont have the dvdrental, please go through this [https://courses.parottasalna.com/database-engineering/sample-databases/dvd-rental-database](https://courses.parottasalna.com/database-engineering/sample-databases/dvd-rental-database)

When you query data from a table, the [`SELECT`](https://neon.tech/postgresql/postgresql-tutorial/postgresql-select) statement returns rows in an unspecified order. To sort the rows of the result set, you use the `ORDER BY` clause in the [`SELECT`](https://neon.tech/postgresql/postgresql-tutorial/postgresql-select) statement.

The `ORDER BY` clause allows you to sort rows returned by a `SELECT` clause in ascending or descending order based on a sort expression.

The following illustrates the syntax of the `ORDER BY` clause

```sql
SELECT
  select_list
FROM
  table_name
ORDER BY
  sort_expression1 [ASC | DESC],
  sort_expression2 [ASC | DESC],
  ...;
```

In this syntax:

* First, specify a sort expression, which can be a column or an expression, that you want to sort after the `ORDER BY` keywords. If you want to sort the result set based on multiple columns or expressions, you need to place a comma (`,`) between two columns or expressions to separate them.
* Second, you use the `ASC` option to sort rows in ascending order and the `DESC` option to sort rows in descending order. If you omit the `ASC` or `DESC` option, the `ORDER BY` uses `ASC` by default.

PostgreSQL evaluates the clauses in the `SELECT` statement in the following order: `FROM`, `SELECT`, and `ORDER BY.`

### 1. Using PostgreSQL ORDER BY clause to sort rows by one column

The following query uses the `ORDER BY` clause to sort customers by their first names in ascending order

```sql
SELECT
  first_name,
  last_name
FROM
  customer
ORDER BY
  first_name ASC LIMIT 5;
```


![](/_assets/image-43.png)


Since the `ASC` option is the default, you can omit it in the `ORDER BY` clause like this

```sql
SELECT
  first_name,
  last_name
FROM
  customer
ORDER BY
  first_name LIMIT 5;
```

### 2. Using PostgreSQL ORDER BY clause to sort rows by one column in descending order

The following statement selects the first name and last name from the `customer` table and sorts the rows by values in the last name column in descending order.

```sql
SELECT
  first_name,
  last_name
FROM
  customer
ORDER BY
  last_name DESC LIMIT 5;
```


![](/_assets/image-44.png)


### 3. Using PostgreSQL ORDER BY clause to sort rows by multiple columns

The following statement selects the first name and last name from the customer table and sorts the rows by the first name in ascending order and last name in descending order.

```
SELECT
  first_name,
  last_name
FROM
  customer
ORDER BY
  first_name ASC,
  last_name DESC;
```

In this example, the ORDER BY clause sorts rows by values in the first name column first. Then it sorts the sorted rows by values in the last name column.

### 4. Using PostgreSQL ORDER BY clause to sort rows by expressions

The [`LENGTH()`](https://neon.tech/postgresql/postgresql-string-functions/postgresql-length-function) function accepts a string and returns the length of that string.

The following statement selects the first names and their lengths. It sorts the rows by the lengths of the first names.

```sql
SELECT
  first_name,
  LENGTH(first_name) len
FROM
  customer
ORDER BY
  len DESC LIMIT 5;
```


![](/_assets/image-45.png)


Because the `ORDER BY` clause is evaluated after the `SELECT` clause, the column alias `len` is available and can be used in the `ORDER BY` clause.
