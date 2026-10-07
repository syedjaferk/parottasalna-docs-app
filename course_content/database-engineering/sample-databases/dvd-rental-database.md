# DVD Rental Database

### Source&#x20;

[https://github.com/syedjaferk/postgres\_sample\_database/blob/main/dvd\_rental/dvdrental.tar](https://github.com/syedjaferk/postgres_sample_database/blob/main/dvd_rental/dvdrental.tar)

### Steps to import the database

1. Download the tar file from the given link.
2. Create the dvdrental database. Login to the postgres db, with the user. (here for example we are using the postgres superuser.)

```bash
psql -U postgres
```

After entering the password correctly, you will be connected to the PostgreSQL server.

```
postgres=#
```


![](/_assets/image-47.png)


Second, create a new database called `dvdrental` using `CREATE DABASE` statement:

```sql
CREATE DATABASE dvdrental;
```


![](/_assets/image-48.png)


Output:

```
CREATE DATABASE
```

PostgreSQL will create a new database called `dvdrental`.

Third, verify the database creation using the `\l` command. The `\l` command will show all databases in the PostgreSQL server. The output shows that `dvdrental` on the list, meaning that you have created the `dvdrental` database successfully. Now disconnect from the PostgreSQL server and exit the `psql` using the `exit` command

3. Load the dataset into the db using the `pg_restore`

```bash
pg_restore -U postgres -d dvdrental dvdrental.tar
```

n this command:

* The `-U postgres` instructs `pg_restore` to connect the PostgreSQL server using the `postgres` user.
* The `-d dvdrental` specifies the target database to load.

It might prompt you to enter the password for the `postgres` user. Enter the password for the `postgres` user and press the Enter (or Return key)

It’ll take about seconds to load data stored in the `dvdrental.tar` file into the `dvdrental` database.

4. Verify the database is loaded.

Login to the postgres with database as `dvdrental`,&#x20;

```bash
psql -U postgres -d dvdrental;
```


![](/_assets/image-49.png)


&#x20;display all tables in the `dvdrental` database

```
\dt
```


![](/_assets/image-50.png)


Now you have the practice DB. Happy Learning !
