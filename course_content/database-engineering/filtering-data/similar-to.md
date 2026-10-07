# SIMILAR TO

In SQL, when you need to perform pattern matching with more advanced capabilities than the **LIKE** operator, you can use the **SIMILAR TO** operator. The **SIMILAR TO** operator in PostgreSQL offers a way to search for patterns that follow regular expression rules.

Imagine you want to find customers in a database whose names contain a combination of specific characters.&#x20;

For example, you might remember that the customer names contain specific combinations of letters, but you don’t know the exact order. Instead of searching with multiple `LIKE` statements or using wildcard characters excessively, you can use the **SIMILAR TO** operator, which can provide much more powerful and flexible pattern matching.

## **How SIMILAR TO Works**

The **SIMILAR TO** operator allows you to match a pattern to a string using regular expression syntax, similar to **POSIX regular expressions**. The syntax for **SIMILAR TO** is

```sql
value SIMILAR TO pattern    
```

Where:

* `value` is the string or column to be matched.
* `pattern` is the regular expression pattern that you want to compare against.

The **SIMILAR TO** operator is used to check if the value matches the given regular expression pattern. If it does, the operator returns `TRUE`; otherwise, it returns `FALSE`.

## **Basic Syntax and Examples**

Let’s look at some basic examples of using the **SIMILAR TO** operator in PostgreSQL.

### **1) Basic SIMILAR TO Example**

Let’s say you want to find customers whose first names start with either "Jen", "Jon", or "Jan". Instead of writing multiple `LIKE` queries, you can use **SIMILAR TO** with a single pattern.

```sql
SELECT first_name, last_name
FROM customer
WHERE first_name SIMILAR TO 'J(e|o|a)n%';
```

In this example:

* The pattern `J(e|o|a)n%` matches any string that starts with "J" followed by either "e", "o", or "a", and then any sequence of characters (`%`).
* The `|` character is used to specify alternatives within the regular expression.

### **2) Using SIMILAR TO with Multiple Patterns**

If you want to match several different patterns, **SIMILAR TO** lets you combine them into one regular expression. For example, to find customer names that start with "A" or "B" and have two additional characters, you could use

```sql
SELECT first_name, last_name
FROM customer
WHERE first_name SIMILAR TO '[AB]__';
```

In this query:

* `[AB]` means the first character must be "A" or "B".
* `__` means there should be exactly two characters following it.

### **3) SIMILAR TO with Wildcards**

You can also use wildcards in the **SIMILAR TO** pattern. For instance, if you want to find any first name starting with "S" and followed by at least one character.

```sql
SELECT first_name, last_name
FROM customer
WHERE first_name SIMILAR TO 'S%';
```

Here, `%` is the wildcard matching any sequence of characters (just like in **LIKE**).
