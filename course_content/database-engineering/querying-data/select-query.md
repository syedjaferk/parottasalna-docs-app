# SELECT Query

> 📌 Note: This tutorial uses the dvdrental database. If you dont have the dvdrental, please go through this [https://courses.parottasalna.com/database-engineering/sample-databases/dvd-rental-database](https://courses.parottasalna.com/database-engineering/sample-databases/dvd-rental-database)

The `SELECT` statement is one of the most fundamental SQL commands and is used to retrieve data from a PostgreSQL database. Let’s break it down with relatable examples to understand how it works.

### **1. Basic SELECT Statement**

To fetch data from a table, you use

```sql
SELECT column_name FROM table_name;
```

Example: Find the first names of all customers from the `customer` table:

```sql
SELECT first_name FROM customer;
```


![](/_assets/image-34.png)


Notice that we added a semicolon (`;`) at the end of the `SELECT` statement. The semicolon is not a part of the SQL statement; rather, it serves as a signal of PostgreSQL indicating the conclusion of an SQL statement. Additionally, semicolons are used to separate two or more SQL statements.

### 2. Using PostgreSQL SELECT statement to query data from multiple columns example

The following query uses the `SELECT` statement to retrieve first name, last name, and email of customers from the `customer` table.

```sql
SELECT
   first_name,
   last_name,
   email
FROM
   customer;
```


![](/_assets/image-35.png)


### 3. Using PostgreSQL SELECT statement to query data from all columns of a table example

The following query uses the `SELECT *` statement to retrieve data from all columns of the `customer` table

```sql
SELECT * FROM customer;
```


![](/_assets/image-36.png)


### 4. Why we should not use SELECT \* in a query ?

When writing SQL queries to fetch data, you can use an asterisk (`*`) in the `SELECT` statement to quickly grab all the columns from a table. This is convenient, but it’s not the best approach when building applications like in Python, Java, or PHP.&#x20;

Here’s why,

**1. Performance Issues**

* **Database Load**: If the table has many columns, `SELECT *` pulls everything—even data your application doesn’t need. This can slow down database operations.
* **Application Overhead**: Fetching unnecessary data increases the traffic between your database and app, leading to slower load times, especially for large datasets.

**2. Clarity and Maintainability**

Using `SELECT *` makes the query ambiguous. For example:

* If the database structure changes (e.g., columns are added), the app may break because it wasn’t expecting those extra columns.
* Specifying columns explicitly helps you and your teammates understand exactly what data is being fetched.

Instead of this

```sql
SELECT * FROM employees;
```

Do this,

```sql
SELECT id, name, department FROM employees;
```

**3. When to Use `*`**

* **Ad-hoc Queries**: Perfect for quick checks or one-off investigations directly on the database.
* **Learning**: It’s great for exploring tables when you're not yet sure what data is stored.

Example: If you're troubleshooting, this is fine

```sql
SELECT * FROM customers WHERE city = 'New York';
```

But in your application code, it's better to fetch only what's required

```sql
SELECT customer_id, name, email FROM customers WHERE city = 'New York';
```

**Real-World Example**

Imagine an online store with a `products` table:

* Columns: `id`, `name`, `price`, `description`, `inventory_count`.

For showing a product list on the homepage, you only need `name` and `price`. Using `SELECT *` fetches unnecessary data like the product description, wasting resources.

Efficient Query,&#x20;

```sql
SELECT name, price FROM products;
```

#### **Key Takeaway**

Use `SELECT *` sparingly and only for quick tasks. For application development, **always specify the columns you need** to keep your code efficient, clear, and scalable.
