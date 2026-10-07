# Create a Docker volume and use it to persist data for a MySQL container.

### Question

Create a Docker volume and use it to persist data for a MySQL container. Verify that the data persists even after the container is removed. Try creating a test db.

### Solution

There are ways to persist the data between the container and the host. (Using binded mount and unbinded mount )

#### Step 1:  Create a Docker Volume

```bash
docker volume create mysql_data
```

This creates a volume named `mysql_data` where MySQL will store its data.

#### Step 2: Run a MySQL Container with the Volume

Now, run a MySQL container and attach the volume to it. Replace `your_password` with your own secure password for the root user.

```bash
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=your_password -v mysql_data:/var/lib/mysql -d mysql:latest
```

* `--name mysql-container`: Names the container.
* `-e MYSQL_ROOT_PASSWORD=your_password`: Sets the root password for MySQL.
* `-v mysql_data:/var/lib/mysql`: Mounts the `mysql_data` volume to `/var/lib/mysql`, where MySQL stores its data.
* `-d mysql:latest`: Runs the latest version of MySQL in detached mode.

#### Step 3: Access the MySQL Container and Create a Test Database

To interact with the MySQL container, you can use the following command to get into the MySQL shell

```bash
docker exec -it mysql-container mysql -u root -p
```

Once inside the MySQL shell, enter your `root` password, and then create a test database

```sql
CREATE DATABASE test_db;
SHOW DATABASES;
```

You should see `test_db` in the list of databases.

#### Step 4: Remove the MySQL Container

Now, remove the container

```bash
docker rm -f mysql-container
```

This will remove the MySQL container, but the volume will still exist.

#### Step 5: Re-run the MySQL Container with the Same Volume

To verify that the data persists, re-run the container with the same volume

```bash
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=your_password -v mysql_data:/var/lib/mysql -d mysql:latest
```

#### Step 6: Check if the Data Persists

After the container is running, access the MySQL shell again

```bash
docker exec -it mysql-container mysql -u root -p
```

Once in the shell, check for the existence of \`test\_db\`&#x20;

```sql
SHOW DATABASES;
```

If the `test_db` database appears in the list, this confirms that the data persisted even after the container was removed.
