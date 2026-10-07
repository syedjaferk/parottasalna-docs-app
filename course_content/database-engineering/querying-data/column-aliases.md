# Column Aliases

> 📌 Note: This tutorial uses the dvdrental database. If you dont have the dvdrental, please go through this [https://courses.parottasalna.com/database-engineering/sample-databases/dvd-rental-database](https://courses.parottasalna.com/database-engineering/sample-databases/dvd-rental-database)

### What are Column Aliases ?

A column alias allows you to assign a column or an expression in the select list of a `SELECT` statement a temporary name. The column alias exists temporarily during the execution of the query.

The following illustrates the syntax of using a column alias

```sql
SELECT column_name AS alias_name
FROM table_name;
```

In this syntax, the `column_name` is assigned an alias `alias_name`. The `AS` keyword is optional so you can omit it like this,

```sql
SELECT column_name alias_name
FROM table_name;
```

The main purpose of column aliases is to make the headings of the output of a query more meaningful.

### 1. Assigning a column alias to a column example

The following query returns the first names and last names of first 5 customers from the `customer` table

```sql
SELECT first_name, last_name FROM customer LIMIT 5;
```


![](/_assets/image-37.png)


If you want to rename the `last_name` heading, you can assign it a new name using a column alias like this

```sql
SELECT first_name, last_name AS surname FROM customer LIMIT 5;
```


![](/_assets/image-38.png)


This query assigned the `surname` as the alias of the `last_name` column

Or you can make it shorter by removing the `AS` keyword as follows,

```sql
SELECT first_name, last_name surname FROM customer LIMIT 5;
```


![](/_assets/image-39.png)


### 2. Assigning a column alias to an expression example

The following query returns the full names of first 5 customers. It constructs the full name by concatenating the first name, space, and the last name

```sql
SELECT
   first_name || ' ' || last_name
FROM
   customer LIMIT 5;
```

Note that in PostgreSQL, you use the `||` as the concatenating operator that concatenates one or more strings into a single string.


![](/_assets/image-40.png)


As you can see clearly from the output, the heading of the column is not meaningful `?column?` . To fix this, you can assign the expression `first_name || ' ' || last_name` a column alias e.g., `full_name`

```sql
SELECT
    first_name || ' ' || last_name AS full_name
FROM
    customer LIMIT 5;
```


![](/_assets/image-41.png)


### 3. Column aliases that contain spaces

If a column alias contains one or more spaces, you need to surround it with double quotes like this

```sql
column_name AS "column alias"
```

For example,

```sql
SELECT
    first_name || ' ' || last_name "full name"
FROM
    customer LIMIT 5;
```


![](/_assets/image-42.png)
