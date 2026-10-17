# Database Engineering with PostgreSQL

Learn relational databases and SQL with PostgreSQL: installation, roles, querying, filtering, ER diagrams and joins, with hands-on tasks on the DVD Rental sample database.

## How each session works

1. **The big idea**: the topic in plain words, with an everyday example.
2. **A picture**: a diagram of the idea.
3. **Real queries**: every SQL statement was run on PostgreSQL 17 and the output you see is what it printed.
4. **Common mistakes**: what trips beginners up.
5. **Hands-on exercises**: try first, then open the solution (each was run too).
6. **Practice**: a quiz for the session.

:::{tip}
All sessions use one small movie database. Create it once with `code/00-setup.sql` (`psql -d course -f 00-setup.sql`),
then follow along in `psql`. Install PostgreSQL first from the *Installing PostgreSQL* page below if you have not yet.
:::

```{toctree}
:maxdepth: 1
:caption: Sessions

sessions/01-why-databases
sessions/02-database-and-dbms
sessions/03-relational-model
sessions/04-querying-data
sessions/05-filtering-data
sessions/06-er-diagrams
sessions/07-joins
sessions/08-joins-on-e-commerce
```

```{toctree}
:maxdepth: 2
:caption: Reference: install and sample data

Installing Postgresql <installing-postgresql/README>
What happens during the initial installation ? <what-happens-during-the-initial-installation/README>
Sample Databases <sample-databases/README>
```

```{toctree}
:maxdepth: 2
:caption: Querying Data

SELECT Query <querying-data/select-query>
Column Aliases <querying-data/column-aliases>
Order By <querying-data/order-by>
SELECT DISTINCT <querying-data/select-distinct>
DB-TASK-001 <querying-data/db-task-001>
```


```{toctree}
:maxdepth: 2
:caption: Filtering Data

WHERE ? <filtering-data/where>
AND Operator <filtering-data/and-operator>
OR Operator <filtering-data/or-operator>
LIMIT <filtering-data/limit>
FETCH <filtering-data/fetch>
IN <filtering-data/in>
BETWEEN <filtering-data/between>
LIKE <filtering-data/like>
SIMILAR TO <filtering-data/similar-to>
IS NULL <filtering-data/is-null>
ESCAPE <filtering-data/escape>
DB-TASK-002 <filtering-data/db-task-002>
```


```{toctree}
:maxdepth: 2
:caption: Entity Relationship Diagram

What is an ER Diagram ? <entity-relationship-diagram/what-is-an-er-diagram>
Entity <entity-relationship-diagram/entity>
Identifiers <entity-relationship-diagram/identifiers>
Relationship <entity-relationship-diagram/relationship>
Attributes <entity-relationship-diagram/attributes>
Cardinality <entity-relationship-diagram/cardinality>
Entity Relationship Diagram Tutorial <entity-relationship-diagram/entity-relationship-diagram-tutorial>
DB-TASK-003 <entity-relationship-diagram/db-task-003>
```


```{toctree}
:maxdepth: 2
:caption: Joins

Joins <joins/joins>
Joins With Employee and Departments <joins/joins-with-employee-and-departments>
```

