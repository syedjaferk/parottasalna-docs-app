# What is Relational Database Model ?

The **relational database model** is a way of organizing and storing data in a structured format using tables, which are composed of rows and columns. The primary concept behind this model is the relationship between different data entities.

### Library Analogy

Imagine a **relational database** as a **library**, where information is organized in a very structured way to make it easy to find and manage.

1. **Tables as Bookshelves:**
   * In a library, there are many **bookshelves**. Each bookshelf contains books related to a specific topic (e.g., history, science, or fiction). Similarly, in a relational database, each **table** is like a bookshelf, and it stores data related to a specific category (e.g., customers, orders, products).
2. **Rows as Books:**
   * Each **row** in a table is like a **book** on a bookshelf. A row contains all the information about a single entity, just like a book contains detailed information on a particular subject. For instance, a row in a **Customer** table might represent all the details about a specific customer (name, address, phone number).
3. **Columns as Information Fields:**
   * The **columns** in a table are like the **chapters** or sections of a book, each containing specific information. For example, a column for "CustomerName" in the **Customers** table is like a chapter in the book that details the name of the person. Other columns might be like chapters on address, email, or phone number.
4. **Primary Key as ISBN:**
   * Each **book** in the library has a unique identifier (like an **ISBN** number). This ensures that no two books are the same. In the same way, each **row** in a table has a **primary key**, which is a unique identifier for each record in the table (e.g., "CustomerID" in the **Customers** table). This key ensures that every row can be uniquely identified, just like every book can be found with its ISBN.
5. **Foreign Key as a Reference to Another Book:**
   * If a book references another book, it’s like having a **footnote** or **reference** to another book on the bookshelf. For example, a **book** in a **history section** might refer to a book in the **geography section**. In the same way, a **foreign key** in one table (like **CustomerID** in the **Orders** table) refers to the primary key of another table (like the **CustomerID** in the **Customers** table). This establishes a connection or relationship between the two tables, just as referencing one book might link to another.
6. **Relationships as Connections Between Bookshelves:**
   * Imagine that there are **multiple bookshelves** in the library, and some books refer to others across different bookshelves. For instance, a book on **history** might reference a book on **geography**. This is similar to how tables in a relational database are connected by **relationships**. For example, a **Customer** table is connected to an **Orders** table via a foreign key (the **CustomerID**), creating a **relationship** between the two. You can easily find all the books (or records) that are related to each other by these references.
7. **Queries as Searching for Books:**
   * If you wanted to find specific information in the library, you could go to the **library catalog** and search for books by title, author, or subject. In the relational database, you use **SQL queries** to search for and retrieve specific information from the tables. For instance, if you want to find all orders placed by a specific customer, you can "query" the database in the same way you'd search the library catalog for all books written by a specific author.
8. **Normalization as Organizing the Library Efficiently:**
   * In a library, books are organized so that similar topics are grouped together to avoid duplication (e.g., you don't store the same book on multiple shelves). Similarly, **normalization** in a relational database ensures that data is stored efficiently, reducing redundancy. For example, customer information might be stored in one table, and order details in another, linked together by a reference (foreign key). This prevents storing the same customer information multiple times, just as you wouldn’t want to have multiple copies of the same book on different shelves.

### What is Data Integrity ?

To understand **data integrity** in a relational database, let’s continue with the **library analogy**.

Imagine you’re managing a **library** where the books are carefully organized on bookshelves (tables), and you must ensure that the information about the books, their authors, and other details is accurate, consistent, and trustworthy. **Data integrity** is like the set of rules and procedures that ensure the library’s catalog remains correct, reliable, and up-to-date.

#### Key Types of Integrity:

1. **Entity Integrity (Uniqueness):**
   * **Analogy**: Every book in the library must have a unique **ISBN** or identifier so that no two books are confused with each other. This is similar to how in a relational database, every row must have a unique **primary key** that identifies it unambiguously.
   * **Data Integrity**: In the database, the **primary key** (like **CustomerID** in a **Customer** table) guarantees that every record is unique and can be easily found without duplication. Just as two books can’t share the same ISBN, two rows cannot share the same primary key.
2. **Referential Integrity (Correct Links Between Data):**
   * **Analogy**: Imagine there’s a **cross-reference** in a history book pointing you to another book in the library on the same topic, and you want to ensure that the book being referred to is actually there on the shelf. You wouldn’t want the reference to point to a book that doesn’t exist.
   * **Data Integrity**: In a relational database, **referential integrity** ensures that **foreign keys** (the references between tables) correctly point to valid data in other tables. For instance, in the **Orders** table, each order should reference an existing **CustomerID** in the **Customers** table. If a foreign key points to a non-existent record (like a reference to a missing book), it would break the integrity of the system. The database enforces rules to ensure foreign keys always reference valid, existing records.
3. **Domain Integrity (Valid Data in Each Field):**
   * **Analogy**: Every book in the library has a **category**—such as fiction, non-fiction, or science fiction—and must follow a valid classification system. You can’t put a science fiction book in the history section, just as you can’t assign an **invalid** category to a book.
   * **Data Integrity**: Similarly, **domain integrity** ensures that each column in a table only contains valid data. For example, the **Email** column in a **Customers** table should contain only valid email addresses (not a number or a date), just like how the **category** field for a book can’t contain something nonsensical like "1234" if it’s supposed to list genres like “fiction” or “history.”
4. **User-Defined Integrity (Custom Rules for Your Data):**
   * **Analogy**: Imagine that the library has a specific rule, such as: "All books in the **children's section** must be for readers aged 12 or younger." This rule ensures that the books are organized in a way that makes sense to library users.
   * **Data Integrity**: In a relational database, **user-defined integrity** allows you to define specific rules or constraints based on the needs of your application. For example, you might create a rule that a **product price** in an **Inventory** table must always be greater than zero, just like a library’s custom rule about the children's books.

Miro Board: [https://miro.com/app/board/uXjVLD2T5os=/?share\_link\_id=299975414637](https://miro.com/app/board/uXjVLD2T5os=/?share_link_id=299975414637)
