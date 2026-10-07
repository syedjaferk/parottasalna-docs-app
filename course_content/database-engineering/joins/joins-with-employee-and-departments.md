# Joins With Employee and Departments

```sql
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(50)
);

CREATE TABLE employees (
    emp_id SERIAL PRIMARY KEY,
    emp_name VARCHAR(50),
    dept_id INT REFERENCES departments(dept_id),
    salary INT
);
```

Insert data into the tables,&#x20;

```sql
INSERT INTO departments (dept_name) VALUES 
('HR'), 
('Finance'), 
('IT');

INSERT INTO employees (emp_name, dept_id, salary) VALUES 
('Alice', 1, 50000), 
('Bob', 2, 60000), 
('Charlie', 3, 70000), 
('David', NULL, 55000);

```

#### **INNER JOIN**

**Definition:** Combines rows from two tables when there is a matching value in the specified columns.

* **Use Case:** When you want only the records that have corresponding entries in both tables.
* **Real-World Example:** Show employees and their respective departments.

```sql
SELECT e.emp_name, d.dept_name
FROM employees e
INNER JOIN departments d 
ON e.dept_id = d.dept_id;
```


![](/_assets/image.png)


**Explanation:**\
The `INNER JOIN` only includes employees who belong to a department. Employees without a department will not appear in the result.



#### **LEFT JOIN (or LEFT OUTER JOIN)**

**Definition:** Returns all rows from the left table and the matching rows from the right table. If no match is found, NULL values are returned for columns of the right table.

* **Use Case:** When you want to see all entries in one table (left) and their matches, if they exist, in the other table.
* **Real-World Example:** List all employees, including those who don’t belong to any department.

```sql
SELECT e.emp_name, d.dept_name
FROM employees e
LEFT JOIN departments d 
ON e.dept_id = d.dept_id;
```


![](/_assets/image-1.png)


#### **RIGHT JOIN (or RIGHT OUTER JOIN)**

**Definition:** Returns all rows from the right table and the matching rows from the left table. If no match is found, NULL values are returned for columns of the left table.

* **Use Case:** When you want to ensure that all entries from the right table are included, even if there’s no match in the left table.
* **Real-World Example:** List all departments, even those with no employees

```sql
SELECT e.emp_name, d.dept_name
FROM employees e
RIGHT JOIN departments d 
ON e.dept_id = d.dept_id;
```

All departments appear in the result. If a department has no employees, the employee column will show `NULL`.



#### **FULL OUTER JOIN**

**Definition:** Combines the results of both `LEFT JOIN` and `RIGHT JOIN`. Returns all rows from both tables, with NULLs for non-matching rows.

* **Use Case:** When you need to see everything, even if there are no matches in either table.
* **Real-World Example:** List all employees and departments, including unmatched records from both.

```sql
SELECT e.emp_name, d.dept_name
FROM employees e
FULL OUTER JOIN departments d 
ON e.dept_id = d.dept_id;

```

**Explanation:**\
The result will include

1. Employees with departments.
2. Employees without departments (`dept_name = NULL`).
3. Departments with no employees (`emp_name = NULL`).
