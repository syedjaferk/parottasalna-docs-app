# DB-TASK-003

1. Online Book Store

* A **customer** can place multiple **orders**, but each **order** belongs to one **customer**.
* A **book** can appear in multiple **orders**, and an **order** can contain multiple **books**.
* Each **order** consists of one or more **order details** entries, specifying the quantity and price of each book in that order.
* The **stock quantity** of a book should decrease when an order is placed.
* A book’s **price** is stored at the time of the order to maintain historical pricing.


![](/_assets/image-2.png)


**Customer Table**

```sql
CREATE TABLE customer (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    address TEXT,
    phone_number VARCHAR(15)
);

```

**Book Table**

```sql
CREATE TABLE book (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100),
    isbn VARCHAR(20) UNIQUE,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL
);

```

**Order Table**

```sql
CREATE TABLE order_table (
    order_id SERIAL PRIMARY KEY ,
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    customer_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);
```

**OrderDetails Table**

```sql
CREATE TABLE order_details (
    order_details_id SERIAL PRIMARY KEY ,
    order_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES order_table (order_id),
    FOREIGN KEY (book_id) REFERENCES book(book_id)
);
```

**Insert Sample Data**

Insert Customers:

```sql
INSERT INTO customer (name, email, address, phone_number) VALUES
('Alice Johnson', 'alice.johnson@example.com', '123 Elm Street, City A', '1234567890'),
('Bob Smith', 'bob.smith@example.com', '456 Oak Avenue, City B', '0987654321');

```

Insert Books:

```sql
INSERT INTO book (title, author, isbn, price, stock_quantity) VALUES
('Physics Fundamentals', 'John Doe', '978-1234567890', 50.00, 10),
('Advanced Physics', 'Jane Roe', '978-0987654321', 60.00, 5),
('Organic Chemistry', 'Emily Stone', '978-1122334455', 45.00, 8),
('Inorganic Chemistry', 'Michael Green', '978-6677889900', 55.00, 12);

```

Insert Orders:

```sql
INSERT INTO order_table (order_date, customer_id, total_amount) VALUES
('2024-12-01 10:00:00', 1, 155.00), 
('2024-12-02 15:30:00', 2, 105.00); 
```

Insert Order Details:

```sql
INSERT INTO order_details (order_id, book_id, quantity, price) VALUES
(1, 1, 2, 100.00),
(1, 3, 1, 45.00), 
(2, 2, 1, 60.00), 
(2, 4, 1, 55.00);
```

List all Physics and Chemistry books:

```sql
SELECT * 
FROM book 
WHERE title LIKE '%Physics%' OR title LIKE '%Chemistry%';
```

Get total stock of Physics and Chemistry books:

```sql
SELECT title, stock_quantity 
FROM book 
WHERE title LIKE '%Physics%' OR title LIKE '%Chemistry%';
```

Find the total sales for Physics books:

```sql
SELECT SUM(price * quantity) AS total_sales
FROM order_details od
JOIN book b ON od.book_id = b.book_id
WHERE b.title LIKE '%Physics%';
```







2. Library Management System

* A **member** can borrow multiple **books**, but each **loan** belongs to one **member**.
* A **book** can be loaned to multiple members over time, but only to one member at a time.
* The **return date** should be recorded when the book is returned.


![](/_assets/image-3.png)


3. School Management System

* A **student** can enroll in multiple **classrooms**, and each **classroom** can have multiple **students**.
* Each **classroom** is assigned one **teacher**.
* A **teacher** can teach multiple **classrooms**.



4. E-Commerce System

* A **customer** can place multiple **orders**, and each **order** can have multiple **products** via **OrderDetails**.
* A **product** can belong to multiple **categories** via **ProductCategory**.
* Each **order** must be associated with a **payment**.
