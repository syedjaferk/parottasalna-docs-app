# Installing PostgreSQL on Mac

### **Step 1: Use Homebrew**

Homebrew is a package manager for macOS. If you don’t have Homebrew installed, install it first by running

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### **Step 2: Install PostgreSQL**

Once Homebrew is installed, run

```bash
brew install postgresql
```

**Explanation**: This command downloads and installs PostgreSQL via Homebrew.

### **Step 3: Start PostgreSQL**

Start the PostgreSQL service.

```
brew services start postgresql
```

**Explanation**: This ensures PostgreSQL runs in the background, even after restarting your Mac.

### **Step 4: Verify Installation**

1. Check if PostgreSQL is running

```bash
brew services list
```

**Explanation**: This shows all services managed by Homebrew and their statuses.

2. Access PostgreSQL:

```bash
psql postgres
```

**Explanation**: Opens the PostgreSQL interface connected to the default `postgres` database.
