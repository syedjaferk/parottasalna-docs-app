# More examples on Roles

Roles in PostgreSQL are flexible and can represent different entities: a **user**, a **group**, or a permission set.

Let’s look at some examples of how to create and use roles for various scenarios.

### **1. Basic Role Without Login**

A role without the ability to log in can act as a **permission set** or a **group**.

**Example:**

Create a role to manage permissions for application developers.

```sql
-- Create a role for developers
CREATE ROLE developers;

-- Grant permissions to the role
GRANT SELECT, INSERT ON employees TO developers;

```

* The `developers` role cannot log in but can have permissions assigned.
* Individual users (like Alice and Bob) can be added to this role to inherit its permissions.

### **2. Role with Login (User Role)**

A role that can log in is considered a **user**.

**Example:**

Create a user role for an individual database user.

```sql
-- Create a role with login capability
CREATE ROLE alice WITH LOGIN PASSWORD 'securepassword';

-- Grant specific permissions to the user
GRANT SELECT ON employees TO alice;

```

Alice can now log in to the database and has `SELECT` access to the `employees` table.

### **3. Role as a Group**

A role can act as a **group** to simplify permission management for multiple users.

**Example:**

1. Create a group role for a team of analysts

```sql
CREATE ROLE analysts;

```

2. Grant read-only access to a table

```sql
GRANT SELECT ON sales_data TO analysts;
```

3. Add individual users to the group

```sql
CREATE ROLE bob WITH LOGIN PASSWORD 'password123';
CREATE ROLE carol WITH LOGIN PASSWORD 'password123';

-- Add users to the group
GRANT analysts TO bob, carol;

```

Now both Bob and Carol inherit `SELECT` privileges on the `sales_data` table from the `analysts` role.

### **4. Role with Inheritance**

Roles can be nested, meaning one role can inherit permissions from another.

**Example:**

1. Create a base role for read-only access

```sql
CREATE ROLE read_access;
GRANT SELECT ON employees TO read_access;

```

2. Create a manager role that inherits from `read_access` and has additional permissions

```sql
CREATE ROLE manager;
GRANT INSERT, UPDATE ON employees TO manager;
GRANT read_access TO manager;

```

3. Assign a user to the `manager` role

```sql
CREATE ROLE dave WITH LOGIN PASSWORD 'manager123';
GRANT manager TO dave;

```

Dave can now perform `SELECT`, `INSERT`, and `UPDATE` operations on the `employees` table because he inherits `read_access` through the `manager` role.

### 5. Temporary Role for a Consultant

You might need a temporary role for someone who will have limited access for a short time.

**Example:**

1. Create a role for a consultant

```sql
CREATE ROLE consultant WITH LOGIN PASSWORD 'consult123' VALID UNTIL '2024-12-31';

```

2. Assign limited permissions

```sql
GRANT SELECT ON employees TO consultant;
```

The `consultant` role will automatically lose login privileges after December 31, 2024.
