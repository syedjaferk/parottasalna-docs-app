# What happens during the initial installation ?

When you install and initialize PostgreSQL, several processes occur to set up the database system for use. (This is my flow of understanding)

### 1. **Installation Phase**

* **Binary Installation**: PostgreSQL binaries (e.g., `postgres`, `psql`) and utilities are installed. This is handled by package managers like `apt`, `yum`, or directly from source.
* **Configuration Files**: Default configuration files like `postgresql.conf`, `pg_hba.conf`, and `pg_ident.conf` are set up.

### 2. **Initialization (`initdb`)**

The `initdb` command prepares the environment for the PostgreSQL database cluster. Key processes include:

#### **a. Directory Creation**:

* The data directory specified (e.g., `/var/lib/postgresql/data`) is created if it doesn’t already exist.
* Subdirectories like `base`, `global`, `pg_wal`, `pg_stat`, etc., are created to organize data files and system metadata.

#### **b. Configuration File Generation**:

* `postgresql.conf`: Main configuration file.
* `pg_hba.conf`: Controls client authentication.
* `pg_ident.conf`: Maps operating system usernames to database usernames.

#### **c. Creation of System Catalog**:

* Core system catalogs (e.g., `pg_class`, `pg_attribute`, `pg_database`) are created to manage database objects.
* Essential metadata is initialized.

#### **d. Default Templates Setup**:

* **`template0`**:
  * This is a pristine template used to create other databases.
  * Contains only standard objects provided by PostgreSQL.
  * Frozen to prevent modifications.
* **`template1`**:
  * This template is used by default for database creation.
  * It can be modified to include custom extensions, schemas, or objects you want in all new databases.
  * If `template1` is damaged, `template0` can restore it.

#### **e. Default Databases**:

* **`postgres`**: A default administrative database created for use by DBAs.
* **`template0`** and **`template1`**: As described above.
* **`postgres`** is often the initial user-created database for experimentation or administration.

#### **f. Encoding and Locale**:

* Specifies the default character set and locale for the cluster.
* All databases inherit these settings unless overridden.

#### **g. WAL Initialization**:

* The Write-Ahead Logging (WAL) mechanism is set up under `pg_wal`.
* Ensures data durability and crash recovery.

#### **h. Superuser Role**:

* The default superuser role (e.g., `postgres`) is created. It owns all the system objects.

### 3. **Role Management**

* Roles are PostgreSQL’s way of handling users and groups.
* During initialization:
  * The **`postgres` superuser role** is created.
  * Privileges for managing other roles and databases are assigned to this role.

### 4. **Background Processes** (When PostgreSQL Starts)

Once initialized, PostgreSQL runs several background processes for database management:

#### **a. `postmaster` Process**:

* This is the main server process that manages all other subprocesses.

#### **b. Background Worker Processes**:

* **WAL Writer**: Handles WAL updates.
* **Checkpoint Process**: Writes dirty pages to disk to maintain data integrity.
* **Autovacuum**: Automatically manages vacuum and analyze tasks.
* **Stats Collector**: Collects and updates statistics for query optimization.
* **Archiver**: Archives completed WAL segments when configured.

```{toctree}
:maxdepth: 1

Roles, Users & Groups <roles-users-and-groups>
More examples on Roles <more-examples-on-roles>
```
