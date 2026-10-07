# IN

### Introduction to PostgreSQL IN operator

The `IN` operator allows you to check whether a value matches any value in a list of values.

Here’s the basic syntax of the `IN` operator

```sql
value IN (value1,value2,...)
```

The `IN` operator returns true if the `value` is equal to any value in the list such as `value1` and `value2`. The list of values can be a list of literal values including numbers and strings.

### Using the PostgreSQL IN operator with a list of numbers

The following example uses the `IN` operator to retrieve information about the film with id 1, 2, and 3

```sql
SELECT film_id, title
FROM film
WHERE film_id in (1, 2, 3);
```


![](/_assets/image-25.png)


The following statement uses the equal (`=`) and `OR` operators instead of the `IN` operator, which is equivalent to the query above.

```sql
SELECT film_id, title
FROM film
WHERE 
  film_id = 1
  OR film_id = 2
  OR film_id = 3;
```

The query that uses the `IN` operator is shorter and more readable than the query that uses equal (`=`) and `OR` operators. Additionally, PostgreSQL executes the query with the `IN` operator much faster than the same query that uses a list of `OR` operators.

### Using the PostgreSQL IN operator with a list of strings

The following example uses the `IN` operator to find the actors who have the last name in the list `'Allen'`, `'Chase'`, and `'Davis'`

```sql
SELECT first_name, last_name
FROM actor
WHERE last_name IN ('Allen', 'Chase', 'Davis')
ORDER BY last_name;
```


![](/_assets/image-26.png)


### Using the PostgreSQL IN operator with a list of dates

The following statement uses the IN operator to find payments whose payment dates are in a list of dates: `2007-02-15` and `2007-02-16`


```sql
SELECT payment_id, amount, payment_date
FROM payment
WHERE payment_date::date IN ('2007-02-15', '2007-02-16');
```



![](/_assets/image-27.png)


### PostgreSQL NOT IN operator

To negate the `IN` operator, you use the `NOT IN` operator. Here’s the basic syntax of the `NOT IN` operator

```sql
value NOT IN (value1, value2, ...)
```

The `NOT IN` operator returns `true` if the `value` is not equal to any value in the list such as `value1` and `value2`; otherwise, the `NOT IN` operator returns `false`.

The `NOT IN` operator is equivalent to a combination of multiple boolean expressions with the [AND operators](and-operator.md)

```sql
value <> value1 AND value <> value2 AND ...
```

The following example uses the `NOT IN` operator to retrieve films whose id is not 1, 2, or 3,

```sql
SELECT
  film_id,
  title
FROM
  film
WHERE
  film_id NOT IN (1, 2, 3)
ORDER BY
  film_id;
```

Output:&#x20;

```
film_id |            title
---------+-----------------------------
       4 | Affair Prejudice
       5 | African Egg
       6 | Agent Truman
       7 | Airplane Sierra
       8 | Airport Pollock
...
```

The following query retrieves the same set of data but uses the not-equal (`<>`) and `AND` operators

```sql
SELECT
  film_id,
  title
FROM
  film
WHERE
  film_id <> 1
  AND film_id <> 2
  AND film_id <> 3
ORDER BY
  film_id;
```
