# Session 8 · Joins on an e-commerce database

## The big idea

Online shops are the classic joins problem. **Customers** place **orders**; each order is for a
**product**. Because one order row only stores two ids, every useful report ("who bought what, and
how much did they spend?") needs joins across all three tables, plus `SUM` and `GROUP BY` to add
things up.

**Everyday example:** a shop's bill book. Each carbon copy says "customer no. 7, item no. 3, qty 2".
To write the monthly statement you look up customer 7 in the customer register, item 3 in the price
list, and multiply. SQL does that lookup for every row in a single query.

```{raw} html
:file: ../diagrams/join-chain.html
```

## Setup and queries

`code/08-ecommerce.sql` creates three tables and fills them (three customers, four products, three
orders), then runs three reports.

```{literalinclude} ../code/08-ecommerce.sql
:language: sql
```

```{literalinclude} ../code/08-ecommerce.out
:language: text
```

## What the reports teach

1. **Every order, with names.** `orders` is the hub; two `JOIN`s fetch the customer name and product
   name. The order table alone only had ids.
2. **Total spent per customer.** `p.price * o.quantity` is the value of each order line, `SUM` adds
   them per customer, `GROUP BY customer_name` makes one row per customer. Alice bought a laptop (1000)
   and two headphones (2 x 100), so 1200.00.
3. **Charlie appears with an empty total.** Because both joins are `LEFT JOIN`, a customer with no
   orders is kept; the total is `NULL`, not 0. `NULLS LAST` keeps him at the bottom. Use
   `COALESCE(SUM(...), 0)` if you want a 0 shown.
4. **Products nobody bought.** The anti-join pattern again: left join and keep rows where the right
   side is `NULL`. Only the Charger is returned.

## Reading a three-table join step by step

Take the first report. Start with `FROM orders o`: three rows, each holding only ids (customer 1,
product 1, quantity 1). The first `JOIN customers c ON c.customer_id = o.customer_id` looks up each
customer id in the customers table and attaches the name, so the rows are now wider. The second
`JOIN products p ON p.product_id = o.product_id` does the same for the product, attaching its name and
price. Last, `SELECT` picks the columns to show and `ORDER BY` sorts.

You can build any report this way: begin with the table that has one row per *thing you are counting*
(here, orders), then join in each table that holds a fact you need. If the row count changes
unexpectedly between steps, you have found a bug before it reaches a customer's invoice.

## Common mistakes

- **Joining in the wrong order or on the wrong columns.** `ON o.customer_id = p.product_id` runs
  without error and returns nonsense. Name the keys the same way in both tables and read the `ON` aloud.
- **Summing after a join that duplicates rows.** If one order matched two rows in another table, `SUM`
  would double count. Check row counts before and after a join.
- **Using `INNER JOIN` for "all customers" reports.** Customers with no orders vanish.
- **Storing the price only on `products`.** If the price changes next year, old orders change too.
  Real shops copy the price onto the order line when it is placed.
- **Float for money.** Use `NUMERIC`/`DECIMAL`, as in `price DECIMAL(10,2)`.

## Hands-on exercises

**Exercise 1.** Show each customer with the number of orders they placed (0 for Charlie).

<details class="solution"><summary>Solution</summary>

```sql
SELECT c.customer_name, count(o.order_id) AS orders
FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_name
ORDER BY orders DESC, c.customer_name;
```

Alice has 2, Bob has 1, Charlie has 0.

</details>

**Exercise 2.** Show total revenue per product, including products never sold (revenue 0).

<details class="solution"><summary>Solution</summary>

```sql
SELECT p.product_name, COALESCE(SUM(p.price * o.quantity), 0) AS revenue
FROM products p LEFT JOIN orders o ON o.product_id = p.product_id
GROUP BY p.product_name
ORDER BY revenue DESC;
```

`COALESCE` swaps the `NULL` for 0. The Charger shows revenue 0.

</details>

**Exercise 3.** Find the customer who spent the most.

<details class="solution"><summary>Solution</summary>

```sql
SELECT c.customer_name, SUM(p.price * o.quantity) AS total_spent
FROM customers c
JOIN orders o   ON o.customer_id = c.customer_id
JOIN products p ON p.product_id  = o.product_id
GROUP BY c.customer_name
ORDER BY total_spent DESC
LIMIT 1;
```

Alice, with 1200.00.

</details>

## Practice

Take the **Session 8 quiz**. Then try the same ideas on your own data, or on the DVD Rental database
from the reference section.
