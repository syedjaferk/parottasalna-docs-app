# ESCAPE

## **What is the ESCAPE Clause in SQL?**

The **ESCAPE** clause in SQL is used to define an **escape character** in a query. This allows you to escape special characters (like `%`, `_`, `'`, and others) that are typically used for pattern matching or other special functions. By using ESCAPE, you can indicate that certain characters in your pattern should be treated **literally**, rather than having their special meaning in SQL queries.

In pattern matching, particularly with `LIKE` and `SIMILAR TO`, certain characters are treated as **wildcards** or **operators**. However, when you need those characters to be part of your search term rather than their wildcard behavior, the ESCAPE clause ensures that the database treats them as regular text.

## **Common Characters You Need to Escape in SQL**

### **1. Single Quote (`'`)**

The single quote is one of the most common characters that you need to escape. In SQL, single quotes are used to delimit string literals. To include a single quote inside a string, you need to escape it by doubling it.

* **Why**: Single quotes mark the start and end of a string literal. To include a literal single quote, you must "escape" it by doubling it.
* **Example**:\
  To represent the string `It's a movie`, you would write

```sql
'It''s a movie'
```

### **2. Backslash (`\`)**

The backslash is often used as an **escape character** itself, which means it needs to be handled with care when included in a string or pattern. In databases like PostgreSQL, the backslash needs to be **doubled** (`\\`) to be treated as a literal backslash.

* **Example**:\
  To include a backslash in a string, you would write

```sql
SELECT 'This is a backslash: \\';
```

In this case, the `\\` ensures that the database treats the backslash as a character, rather than interpreting it as an escape character.

### **3. Percent Sign (`%`)**

The percent sign is a wildcard character in SQL's `LIKE` pattern matching, representing **zero or more characters**. If you want to match a literal `%`, you need to escape it.

* **How to Escape**: You can use the `ESCAPE` clause to define an escape character. For example, you might use an exclamation mark (`!`) as your escape character.
* **Example**

```sql
SELECT title
FROM film
WHERE title LIKE '%!%%' ESCAPE '!';

```

Here, the exclamation mark (`!`) tells SQL to treat the `%` as a literal character, rather than its wildcard meaning.

### **4. Underscore (`_`)**

The underscore (`_`) is another wildcard in SQL’s `LIKE` pattern, but it matches **exactly one character**. To use an underscore literally (i.e., if you’re searching for an actual underscore in your data), you need to escape it.

* **How to Escape**: Similar to the percent sign, you can use the `ESCAPE` clause to define an escape character.
* **Example**

```sql
SELECT title
FROM film
WHERE title LIKE '%!_%' ESCAPE '!';
```

In this case, `!` tells SQL to treat `_` as a literal underscore.

### **5. Square Brackets (`[]`)**

In some SQL dialects (e.g., SQL Server), square brackets are used for pattern matching to define character ranges. If you need square brackets as literals, you must escape them.

* **How to Escape**: In SQL Server, you would use the `ESCAPE` clause or escape brackets by placing a `!` in front of them.
* **Example**

```sql
SELECT title
FROM film
WHERE title LIKE '%[[]%' ESCAPE '!';
```

This will match movie titles that contain the literal square bracket (`[`).

#### **Using the ESCAPE Clause in SQL Queries**

The **ESCAPE clause** allows you to specify a character that will be used to escape special characters in a `LIKE` pattern. This escape character tells SQL that the next character should be treated literally, and not as part of the SQL pattern matching.

**Syntax of the ESCAPE Clause**

```sql
SELECT column_name
FROM table_name
WHERE column_name LIKE 'pattern' ESCAPE 'escape_character';
```

In this syntax

* `pattern` is the search pattern you are using with `LIKE`.
* `escape_character` is the character you define to treat special characters literally.

| Character              | Escape Required     | SQL Example                 |
| ---------------------- | ------------------- | --------------------------- |
| Single Quote (`'`)     | Yes                 | `'It''s a movie'`           |
| Percent Sign (`%`)     | Yes (with `ESCAPE`) | `LIKE '%!%%' ESCAPE '!'`    |
| Underscore (`_`)       | Yes (with `ESCAPE`) | `LIKE '%!_%' ESCAPE '!'`    |
| Backslash (`\`)        | Yes                 | `'This is a backslash: \\'` |
| Square Brackets (`[]`) | Yes (with `ESCAPE`) | `LIKE '%[[]%' ESCAPE '!'`   |

The ESCAPE clause is an essential tool for handling special characters in SQL queries, especially when working with pattern matching using `LIKE` or `SIMILAR TO`. By using ESCAPE, you can ensure that your queries are both precise and robust, allowing you to match patterns that include characters with special meanings, such as single quotes, percent signs, underscores, and others.
