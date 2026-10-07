# AND Operator

In PostgreSQL, a boolean value can have one of three values: `true`, `false`, and null.

|         | Result |
| ------- | ------ |
| true    | true   |
| t       | true   |
| 'true'  | true   |
| 'y'     | true   |
| 'yes'   | true   |
| '1'     | true   |
| false   | false  |
| f       | false  |
| 'false' | false  |
| 'n'     | false  |
| 'no'    | false  |
| '0'     | false  |

A boolean expression is an expression that evaluates to a boolean value. For example, the expression `1=1` is a boolean expression that evaluates to `true`

```sql
SELECT 1 = 1 AS result;
```

```
 result 
--------
 t
(1 row)

```

The letter `t` in the output indicates the value of `true`. The `AND` operator is a logical operator that combines two boolean expressions.&#x20;

### Basic PostgreSQL AND operator examples

1. The following example uses the `AND` operator to combine two true values, which returns true

```sql
SELECT true AND true AS result;
```

```
result
--------
 t
(1 row)
```

2. The following statement uses the `AND` operator to combine true with false, which returns false

```sql
SELECT true AND false AS result;
```

```
result
--------
 f
(1 row)
```

3. The following example uses the `AND` operator to combine true with null, which returns null

```sql
SELECT true AND null AS result;
```

```
result
--------
 null
(1 row)
```

4. The following example uses the `AND` operator to combine false with false, which returns false

```sql
SELECT false AND false AS result;
```

```
result
--------
 f
(1 row)
```

5. The following example uses the `AND` operator to combine false with null, which returns false

```sql
SELECT false AND null AS result;
```

```
result
--------
 f
(1 row)
```

### Using the AND operator in the WHERE clause

The following example uses the `AND` operator in the `WHERE` clause to find the films that have a length greater than 180 and a rental rate less than 1.

```sql
SELECT
  title,
  length,
  rental_rate
FROM
  film
WHERE
  length > 180
  AND rental_rate < 1;
```

```
title        | length | rental_rate
--------------------+--------+-------------
 Catch Amistad      |    183 |        0.99
 Haunting Pianist   |    181 |        0.99
 Intrigue Worst     |    181 |        0.99
 Love Suicides      |    181 |        0.99
 Runaway Tenenbaums |    181 |        0.99
 Smoochy Control    |    184 |        0.99
 Sorority Queen     |    184 |        0.99
 Theory Mermaid     |    184 |        0.99
 Wild Apollo        |    181 |        0.99
 Young Language     |    183 |        0.99
(10 rows)
```
