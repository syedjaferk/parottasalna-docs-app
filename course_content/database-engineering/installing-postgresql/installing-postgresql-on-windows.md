# Installing PostgreSQL on Windows

### Step 1: Download the Installer

* Go to the [PostgreSQL website.](https://www.enterprisedb.com/download-postgresql-binaries)
* Select **Windows** and download the installer.

### **Step 2: Run the Installer**

1. Open the downloaded file and follow the prompts.
2. During installation:
   * Choose a directory for PostgreSQL (default is fine).
   * Set a password for the default PostgreSQL user (`postgres`). **Remember this password!**
   * Select the components you need. By default, everything essential is selected.
   * Choose a port (default is 5432). Keep this unless you have a specific reason to change it.

#### **Step 3: Verify Installation**

1. Open **pgAdmin** (a graphical tool included in the installation) and connect using the password you set.
2. Alternatively, open the command prompt and type

```bash
psql -U postgres
```

**Explanation**: `psql` is the command-line tool for PostgreSQL. It connects to the database using the username `postgres`.
