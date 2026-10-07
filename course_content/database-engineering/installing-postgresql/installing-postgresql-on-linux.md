# Installing PostgreSQL on Linux

### **Step 1: Update your Package Manager**

Before installing anything, ensure your system's package manager is up-to-date.

```bash
sudo apt update
```

**Explanation**: This tells the system to refresh the list of available software so you can install the latest versions.

### **Step 2: Install PostgreSQL**

Use the package manager to download and install PostgreSQL.

```bash
sudo apt install postgresql postgresql-contrib
```

**Explanation**:

* `postgresql`: The main PostgreSQL software.
* `postgresql-contrib`: Additional helpful tools and extensions.

### **Step 3: Verify Installation**

Check if PostgreSQL is running by checking its status.

```bash
sudo systemctl status postgresql
```

**Explanation**: This displays whether the PostgreSQL service is active. If it says **active (running)**, you're good to go!

### **Step 4: Access PostgreSQL**

Switch to the default PostgreSQL user and access the database.

```bash
sudo -i -u postgres
psql

```

**Explanation**:

* `sudo -i -u postgres`: Switches to the PostgreSQL user.
* `psql`: Opens the PostgreSQL command-line interface.
