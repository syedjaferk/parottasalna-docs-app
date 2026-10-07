# Attributes

Attributes are the properties or characteristics of an entity in a database. They represent the data stored about the entity and are implemented as columns in a table. Graphically represented as ovals or circles.&#x20;

Here are examples of different types of attributes with explanations,

### **1. Simple Attribute**

* **Definition:** Cannot be divided into smaller parts.
* **Example:**
  * **Entity:** `Student`
  * **Attributes:** `StudentID`, `Name`, `Age`
  * Explanation: `StudentID` is a simple, indivisible identifier for a student.

**Table Example**

```sql
CREATE TABLE Student (
    StudentID SERIAL PRIMARY KEY,
    Name TEXT NOT NULL,
    Age INT
);
```


![](/_assets/image-59.png)


### **2. Composite Attribute**

* **Definition:** Can be divided into smaller sub-parts, each with independent meaning.
* **Example:**
  * **Entity:** `Student`
  * **Attribute:** `FullName` (composed of `FirstName` and `LastName`)
  * Explanation: `FullName` can be divided into `FirstName` and `LastName`.

**Table Example**

```sql
CREATE TABLE Student (
    StudentID SERIAL PRIMARY KEY,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL
);
```


![](/_assets/image-60.png)


### **3. Derived Attribute**

* **Definition:** Can be calculated from other attributes.
* **Example:**
  * **Entity:** `Employee`
  * **Attributes:** `DateOfBirth`, `Age`
  * Explanation: `Age` is derived from `DateOfBirth`.

**Table Example**

```sql
CREATE TABLE Employee (
    EmployeeID SERIAL PRIMARY KEY,
    Name TEXT NOT NULL,
    DateOfBirth DATE
);
-- Age can be calculated as:
-- SELECT DATE_PART('year', AGE(DateOfBirth)) AS Age FROM Employee;
```


![](/_assets/image-61.png)


### **4. Multivalued Attribute**

* **Definition:** Can have more than one value for a single entity.
* **Example:**
  * **Entity:** `Student`
  * **Attribute:** `PhoneNumbers` (a student may have multiple phone numbers)
  * Explanation: A student can have a home phone and a mobile phone.

**Table Example**

To handle multivalued attributes, we use a separate table

```sql
CREATE TABLE Student (
    StudentID SERIAL PRIMARY KEY,
    Name TEXT NOT NULL
);

CREATE TABLE StudentPhone (
    StudentID INT REFERENCES Student(StudentID),
    PhoneNumber TEXT NOT NULL
);
```


![](/_assets/image-62.png)


### **5. Key Attribute**

* **Definition:** Uniquely identifies an entity in a table.
* **Example:**
  * **Entity:** `Student`
  * **Attribute:** `StudentID`
  * Explanation: `StudentID` is a unique identifier for each student.

**Table Example**

```sql
CREATE TABLE Student (
    StudentID SERIAL PRIMARY KEY,
    Name TEXT NOT NULL
);
```


![](/_assets/image-63.png)


### Summary

| **Type** | **Description** | **Example** |
| -------- | --------------- | ----------- |

| **Simple** | Cannot be divided further. | `Name`, `Age` |
| ---------- | -------------------------- | ------------- |

| **Composite** | Can be divided into sub-parts. | `FullName` → `FirstName`, `LastName` |
| ------------- | ------------------------------ | ------------------------------------ |

| **Derived** | Calculated from other attributes. | `Age` from `DateOfBirth` |
| ----------- | --------------------------------- | ------------------------ |

| **Multivalued** | Can have multiple values for one entity. | `PhoneNumbers` |
| --------------- | ---------------------------------------- | -------------- |

| **Key** | Uniquely identifies an entity. | `StudentID` |
| ------- | ------------------------------ | ----------- |

| **Foreign Key** | References the primary key of another entity. | `StudentID` in `Enrollment` table |
| --------------- | --------------------------------------------- | --------------------------------- |
