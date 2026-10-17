\set QUIET on
SET client_min_messages = warning;
DROP TABLE IF EXISTS orders, products, customers CASCADE;
CREATE TABLE customers (customer_id SERIAL PRIMARY KEY, customer_name VARCHAR(50));
CREATE TABLE products  (product_id SERIAL PRIMARY KEY, product_name VARCHAR(50), price DECIMAL(10,2));
CREATE TABLE orders (
    order_id    SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    product_id  INT REFERENCES products(product_id),
    quantity    INT
);
INSERT INTO customers (customer_name) VALUES ('Alice'), ('Bob'), ('Charlie');
INSERT INTO products (product_name, price) VALUES ('Laptop', 1000.00), ('Smartphone', 500.00), ('Headphones', 100.00), ('Charger', 20.00);
INSERT INTO orders (customer_id, product_id, quantity) VALUES (1, 1, 1), (1, 3, 2), (2, 2, 1);

\echo '-- every order with the customer and product names'
SELECT o.order_id, c.customer_name, p.product_name, o.quantity
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN products  p ON p.product_id  = o.product_id
ORDER BY o.order_id;
\echo '-- order value'
SELECT c.customer_name, SUM(p.price * o.quantity) AS total_spent
FROM customers c
LEFT JOIN orders o   ON o.customer_id = c.customer_id
LEFT JOIN products p ON p.product_id  = o.product_id
GROUP BY c.customer_name
ORDER BY total_spent DESC NULLS LAST;
\echo '-- products nobody has bought'
SELECT p.product_name
FROM products p LEFT JOIN orders o ON o.product_id = p.product_id
WHERE o.order_id IS NULL;
