# IS NULL

In the database world, NULL means missing information or not applicable. NULL is not a value, therefore, you cannot compare it with other values like numbers or strings.

The comparison of NULL with a value will always result in NULL. Additionally, NULL is not equal to NULL so the following expression returns NULL.

```sql
SELECT null = null AS result;
```

Output:

```
result
--------
 null
(1 row)
```

### IS NULL operator

To check if a value is NULL or not, you cannot use the equal to (`=`) or not equal to (`<>`) operators. Instead, you use the `IS NULL` operator.

Here’s the basic syntax of the `IS NULL` operator.

```sql
value IS NULL
```

The `IS NULL` operator returns true if the `value` is NULL or false otherwise. To negate the `IS NULL` operator, you use the `IS NOT NULL` operator.

```sql
value IS NOT NULL
```

The `IS NOT NULL` operator returns true if the value is not NULL or false otherwise.

### 1) Basic IS NULL operator example

The following example uses the `IS NULL` operator to find the addresses from the `address` table that the `address2` column contains `NULL`

```sql
SELECT address, address2
FROM address
WHERE address2 IS NULL;
```

### 2) Using the IS NOT NULL operator example

The following example uses the `IS NOT NULL` operator to retrieve the address that has the `address2` not NULL.

```sql
SELECT address, address2
FROM address
WHERE address2 IS NOT NULL;
```

Notice that the `address2` is empty, not NULL. This is a good example of **bad practice** when it comes to storing empty strings and NULL in the same column.
