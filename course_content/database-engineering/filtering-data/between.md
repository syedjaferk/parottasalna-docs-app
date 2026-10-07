# BETWEEN

### Introduction to the PostgreSQL BETWEEN operator

The `BETWEEN` operator allows you to check if a value falls within a range of values.

The basic syntax of the `BETWEEN` operator is as follows

```sql
value BETWEEN low AND high;
```

If the `value` is greater than or equal to the `low` value and less than or equal to the `high` value, the `BETWEEN` operator returns `true`; otherwise, it returns `false`.

You can rewrite the `BETWEEN` operator by using the greater than or equal ( `>=`) and less than or equal to ( `<=`) operators and the logical AND operator.

```sql
value >= low AND value <= high
```

If you want to check if a value is outside a specific range, you can use the `NOT BETWEEN` operator as follows,

```sql
value NOT BETWEEN low AND high
```

The following expression is equivalent to the expression that uses the `NOT BETWEEN` operators

```sql
value < low OR value > high
```

## PostgreSQL BETWEEN operator examples

Let’s take a look at the `payment`table in the [dvdrental](../sample-databases/dvd-rental-database.md)

### 1) Using the PostgreSQL BETWEEN operator with numbers

The following query uses the `BETWEEN` operator to retrieve payments with `payment_id` is between `17503` and `17505`

```sql
SELECT
  payment_id,
  amount
FROM
  payment
WHERE
  payment_id BETWEEN 17503 AND 17505
ORDER BY
  payment_id;
```

Output:

```
payment_id | amount
------------+--------
      17503 |   7.99
      17504 |   1.99
      17505 |   7.99
(3 rows)
```

### 2) Using the PostgreSQL NOT BETWEEN example

The following example uses the `NOT BETWEEN` operator to find payments with the `payment_id` not between `17503` and `17505`

```sql
SELECT
  payment_id,
  amount
FROM
  payment
WHERE
  payment_id NOT BETWEEN 17503 AND 17505
ORDER BY
  payment_id;
```

Output:&#x20;

```
payment_id | amount
------------+--------
      17506 |   2.99
      17507 |   7.99
      17508 |   5.99
      17509 |   5.99
      17510 |   5.99
...
```

### 3) Using the PostgreSQL BETWEEN with a date range

If you want to check a value against a date range, you use the literal date in ISO 8601 format, which is `YYYY-MM-DD`.

The following example uses the `BETWEEN` operator to find payments whose payment dates are between `2007-02-15` and `2007-02-20` and amount more than 10.

```sql
SELECT
  payment_id,
  amount,
  payment_date
FROM
  payment
WHERE
  payment_date BETWEEN '2007-02-15' AND '2007-02-20'
  AND amount > 10
ORDER BY
  payment_date
LIMIT
  5;
```


![](/_assets/image-28.png)
