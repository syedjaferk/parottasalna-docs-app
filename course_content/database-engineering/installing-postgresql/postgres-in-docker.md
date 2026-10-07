# Postgres in Docker

### _docker-compose.yml_

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: postgres_db
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin_password
      POSTGRES_DB: my_database
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  pgadmin:
    image: dpage/pgadmin4
    container_name: pgadmin_container
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@pgadmin.com
      PGADMIN_DEFAULT_PASSWORD: admin_password
    ports:
      - "8080:80"
    depends_on:
      - postgres

volumes:
  postgres_data:

```

### Configuration Breakdown

* **PostgreSQL Service**:
  * `image: postgres:15`: Specifies the PostgreSQL version.
  * `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: Environment variables to set up the database and credentials.
  * `ports: "5432:5432"`: Exposes PostgreSQL on port 5432 (default port).
  * `volumes`: Mounts a Docker volume to persist PostgreSQL data.
* **pgAdmin Service**:
  * `image: dpage/pgadmin4`: Pulls the latest pgAdmin image.
  * `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD`: Default login credentials.
  * `ports: "8080:80"`: Exposes pgAdmin on port 8080.
  * `depends_on`: Ensures PostgreSQL starts before pgAdmin.

### Start the service

```bash
docker-compose up -d
```
