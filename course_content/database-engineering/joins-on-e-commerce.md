# Joins on E-Commerce

#### **Setup: Create Tables**

We have three tables:

1. **Customers**: Stores customer details.
2. **Orders**: Stores order details.
3. **Products**: Stores product details.

```sql
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(50)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    product_id INT,
    quantity INT
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(50),
    price DECIMAL(10, 2)
);

```

Populate some data,&#x20;

```sql
INSERT INTO customers (customer_name) VALUES
('Alice'), ('Bob'), ('Charlie');

INSERT INTO products (product_name, price) VALUES
('Laptop', 1000.00),
('Smartphone', 500.00),
('Tablet', 300.00);

INSERT INTO orders (customer_id, product_id, quantity) VALUES
(1, 1, 2), 
(2, 2, 1), 
(3, NULL, 3); 



```

#### **1. INNER JOIN**

**Question:** List all customers who placed orders with the product name and quantity.

```sql
SELECT c.customer_name, p.product_name, o.quantity
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
INNER JOIN products p ON o.product_id = p.product_id;
```


![](/_assets/image-74.png)


#### **2. LEFT JOIN**

**Question:** Show all customers and their orders, including orders without a product.

```sql
SELECT c.customer_name, p.product_name, o.quantity
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN products p ON o.product_id = p.product_id;

```


![](/_assets/image-76.png)


#### **3. FULL OUTER JOIN**

**Question:** Show all customers, orders, and products, including those with no matches.

```sql
SELECT c.customer_name, o.order_id, p.product_name
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id
FULL OUTER JOIN products p ON o.product_id = p.product_id;
```


![](/_assets/image-77.png)
