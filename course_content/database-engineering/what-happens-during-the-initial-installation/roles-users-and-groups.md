# Roles, Users & Groups

### Role

As postgres documentation mentions,&#x20;

> A role can be thought of as either a database user, or a group of database users, depending on how the role is set up. Roles can own database objects (for example, tables and functions) and can assign privileges on those objects to other roles to control who has access to which objects. Furthermore, it is possible to grant _membership_ in a role to another role, thus allowing the member role to use privileges assigned to another role.

In PostgreSQL, a **role** is a broad concept that represents an entity that can:

* **Own objects** in the database (like tables, schemas, or databases).
* **Have permissions** to perform operations (like SELECT, INSERT, or DELETE).
* Be granted other roles or privileges

Roles are of 2 types

1. Login Role
2. No-Login Role

All operations that are been executed in postgres will be needing a role. Roles can be granted permissions to perform various actions.&#x20;

Let's create a simple role,

```sql
-- Create a role for developers
CREATE ROLE developers;

-- Grant permissions to the role
GRANT SELECT, INSERT ON employees TO developers;
```

* It creates a role named  `developers`&#x20;
* The `developers` role cannot log in but can have permissions assigned.
* Individual users (like Alice and Bob) can be added to this role to inherit its permissions.

### What is a User then ?

A **user** in PostgreSQL is simply a role with the ability to log in. It represents a person or application that connects to the database.

**How a User is Created:**

* When you create a role and give it the `LOGIN` privilege, it becomes a user.

```sql
CREATE ROLE alice WITH LOGIN PASSWORD 'password123';
GRANT developers TO alice;
```

When you create a role and give it the `LOGIN` privilege, it becomes a user.&#x20;

### **Key Differences Between Roles and Users**

| **Aspect**           | **Role**                                  | **User**                                                          |
| -------------------- | ----------------------------------------- | ----------------------------------------------------------------- |
| **Definition**       | A generic entity for managing privileges. | A role with the `LOGIN` privilege.                                |
| **Purpose**          | Can be a user, group, or permission set.  | Specifically for someone/something that connects to the database. |
| **Login Capability** | Cannot log in by default.                 | Can log in to the database.                                       |
| **Example**          | `CREATE ROLE manager;`                    | `CREATE ROLE john WITH LOGIN;`                                    |

### **When to Use Roles vs Users**

1. **Use Roles as Groups:**
   * Roles are often used as **groups** to manage permissions efficiently.
   * For example, you can create a `developers` role and grant it access to a table

```sql
CREATE ROLE developers;
GRANT SELECT, INSERT ON my_table TO developers;

```

2. **Use Users for Individuals:**

* Users represent actual people or applications connecting to the database.
* For example, you can create a user `alice` and assign her to the `developers` group

```sql
CREATE ROLE alice WITH LOGIN PASSWORD 'password123';
GRANT developers TO alice;

```

### **How Roles and Users Work Together**

* A **user** (a role with `LOGIN`) can be assigned to one or more **group roles**.
* A user inherits the permissions of the roles it belongs to.

**Example:**

1. Create a **group role** for developers:

```sql
CREATE ROLE developers;
GRANT SELECT, INSERT ON my_table TO developers;

```

2. Create a **user** and assign them to the group

```sql
CREATE ROLE alice WITH LOGIN PASSWORD 'password123';
GRANT developers TO alice;

```

3. When Alice logs in, she automatically gets the permissions of the `developers` role.

### **Why Does PostgreSQL Use Roles Instead of Separate Users and Groups?**

PostgreSQL’s unified concept of **roles** simplifies permission management:

* A role can act as a **user**, a **group**, or both.
* Roles can be nested, meaning one role can inherit privileges from another.

This approach avoids having separate systems for users and groups, making the database more flexible and easier to manage.

### **Key Points About Roles**

* **No Login by Default**: Roles can only log in if the `LOGIN` attribute is set.
* **Inheritance**: Roles can inherit permissions from other roles using `GRANT`.
* **Combining Roles**: Users can belong to multiple roles, and their permissions will combine.
