# Identifiers

Identifiers refers to an attribute that uniquely defines an entity in an entity set. Entity keys can be super, candidate or primary.

### **1. Super Key**

* A **super key** is any set of one or more attributes that can uniquely identify a record in a table.
* **Example:** In a **Students** table:
  * Attributes: `StudentID`, `Name`, `Email`, `PhoneNumber`
  * Super Key: `{StudentID}`, `{StudentID, Name}`, `{StudentID, Email}`, etc.
    * Any combination that includes `StudentID` uniquely identifies a student.

### **2. Candidate Key**

* A **candidate key** is a minimal super key — a super key with no redundant attributes.
* **Example:** In a **Students** table:
  * `{StudentID}` (if `StudentID` uniquely identifies students)
  * `{Email}` (if all emails are unique for students)

### **3. Primary Key**

* A **primary key** is the candidate key selected to uniquely identify records in a table.
* **Example:** In a **Students** table:
  * Primary Key: `{StudentID}` (chosen from candidate keys because it is short and meaningful)

### **4. Foreign Key**

* A **foreign key** is an attribute in one table that refers to the primary key of another table, creating a relationship between the two tables.
* **Example:**
  * In an **Enrollments** table:
    * Attributes: `EnrollmentID`, `StudentID`, `CourseID`
    * Foreign Keys:
      * `StudentID` references `StudentID` in the **Students** table.
      * `CourseID` references `CourseID` in the **Courses** table.

### Why Not Just Use the Primary Key for Everything?

1. **Super Key and Candidate Key**\
   These help **identify possible unique identifiers** for the data. Not every candidate key becomes a primary key; the others may have other uses or simply remain as potential unique identifiers.
2. **Primary Key**\
   Only one key can serve as the **primary identifier**, but other candidate keys still exist and may be useful for specific queries or constraints.
3. **Foreign Key**\
   While primary keys are unique within their own table, foreign keys are used to create **relationships** between tables.

Imagine a classroom

* **Super Key:** All possible combinations to uniquely identify a student (e.g., roll number + name, roll number alone, or roll number + email).
* **Candidate Key:** The minimal identifiers (e.g., roll number, email).
* **Primary Key:** The chosen identifier (e.g., roll number).
* **Foreign Key:** A way to link the student with their course (e.g., roll number in the student table links to the enrollment table).

By defining these keys, we ensure **data uniqueness**, **integrity**, and a well-structured database!



### Declaring a Primary Key

```sql
CREATE TABLE students ( 
    sid VARCHAR(10) PRIMARY KEY,
    name VARCHAR(20), 
    address VARCHAR(20)
);
```


![](/_assets/image-9.png)



![](/_assets/image-10.png)


Let's try to insert values into the table,&#x20;

```sql
INSERT INTO students VALUES ('12345-6789', 'Syed Jafer', 'Coimbatore');
```

After Insertion,&#x20;


![](/_assets/image-11.png)


Now, if we try to Insert the same record again, it will result in a duplicate key error.&#x20;


![](/_assets/image-12.png)


### Declaring Other Candidate Keys

If we want the DBMS to check other uniqueness constraints, we may add to the SQL relation schema any number of lines of the form,

```sql
UNIQUE (<list of attributes in key>)
```

Uniqueness is not guaranteed for tuples having NULL values in the key attributes. However, NULL values can be prevented by adding a NOT NULL constraint after the declaration of each key attribute.

```sql
CREATE TABLE Student (
    sid VARCHAR(10) PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    address VARCHAR(20),
    hobby VARCHAR(20),
    UNIQUE (name, address)
);
```

Let's Insert one value,&#x20;

```sql
INSERT INTO Student VALUES (
'06027-5112','Syed Jafer','Coimbatore','chess');
```

Try Inserting the below value again,&#x20;

```sql
INSERT INTO Student VALUES (
'06027-5113','Syed Jafer','Coimbatore','chess');
```


![](/_assets/image-13.png)


Like these, candidate key helps us in saving us from entering duplicate values.&#x20;
