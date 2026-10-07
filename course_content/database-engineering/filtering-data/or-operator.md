# OR Operator

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

### Postgres OR Operator Query Results

<table><thead><tr><th width="620"></th><th></th></tr></thead><tbody><tr><td>SELECT true OR true AS result;</td><td>true</td></tr><tr><td>SELECT true OR false AS result;</td><td>t</td></tr><tr><td>SELECT true OR null AS result;</td><td>t</td></tr><tr><td>SELECT false OR false AS result;</td><td>f</td></tr><tr><td>SELECT false OR null AS result;</td><td>null</td></tr><tr><td>SELECT false OR false AS result;</td><td>f</td></tr><tr><td>SELECT null OR null AS result;</td><td>null</td></tr></tbody></table>

### Using the OR operator in the WHERE clause

The following example uses the `OR` operator in the `WHERE` clause to find the films that have a rental rate is `0.99` or `2.99`

```sql
SELECT
  title,
  rental_rate
FROM
  film
WHERE
  rental_rate = 0.99 OR
  rental_rate = 2.99;
```

Output:

```
title            | rental_rate
-----------------------------+-------------
 Academy Dinosaur            |        0.99
 Adaptation Holes            |        2.99
 Affair Prejudice            |        2.99
 African Egg                 |        2.99
...
```
