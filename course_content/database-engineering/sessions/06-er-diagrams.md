# Session 6 · Entity relationship diagrams

## The big idea

Before you create tables, draw them. An **ER diagram** (entity relationship diagram) shows the
**things** your system stores (entities), the **facts** about each (attributes), and **how things
relate**, including *how many* of one connect to the other (cardinality). Drawing first means you
find design mistakes on paper, where they cost nothing.

**Everyday example:** a school timetable. Teachers, classes and rooms are the things. A teacher takes
many classes; a class has one teacher; a student attends many classes and a class has many students.
Spotting those "one" and "many" words is the whole skill.

```{raw} html
:file: ../diagrams/er-cinema.html
```

## The vocabulary

| Word | Meaning | In our movie database |
|---|---|---|
| Entity | A thing we keep data about | director, movie, actor |
| Attribute | A fact about it | movie: title, year, genre |
| Identifier | Attribute(s) that make a row unique | `movie_id` |
| Relationship | A link between entities | a director *directs* movies |
| Cardinality | How many on each side | one director, many movies |

## Three kinds of relationship

1. **One-to-many.** One director has many movies; each movie has one director. Put the foreign key on
   the "many" side: `movies.director_id`.
2. **One-to-one.** One person, one passport. Rare; often the two tables are merged.
3. **Many-to-many.** A movie has many actors and an actor is in many movies. You cannot put a foreign
   key on either side. The fix is a **link table** with one row per pair: `movie_cast(movie_id,
   actor_id)`, whose primary key is the *pair*.

## From diagram to real tables

The diagram above became the four tables in `code/00-setup.sql`. Ask PostgreSQL to show the two
that carry the relationships, and count how the data really looks.

```{literalinclude} ../code/06-er.sql
:language: sql
```

```{literalinclude} ../code/06-er.out
:language: text
```

In the output, `movies` has a foreign key to `directors` (one-to-many). `movie_cast` has two foreign
keys and a two-column primary key (many-to-many). The counts prove it: actor 2 (Rajinikanth) is in 4
movies, and movie 10 (Vikram) has 4 actors, so neither side is "one".

## Common mistakes

- **Putting a list in one column** (`actors = 'A, B, C'`) instead of a link table.
- **Foreign key on the wrong side.** The key goes on the "many" table. A director row cannot hold
  "all movie ids".
- **Making everything an entity.** "Year" is an attribute of a movie, not its own table, unless you
  need facts about years themselves.
- **Forgetting the primary key of the link table.** Without `PRIMARY KEY (movie_id, actor_id)` the
  same actor can be attached to a movie twice.
- **Confusing the direction of cardinality.** Say it both ways: "a director has many movies, a movie
  has one director".

## Hands-on exercises

**Exercise 1 · Library.** A library has members, books and loans. A member can borrow many books over
time; a book can be borrowed by many members over time. Name the entities and the relationship type.
What table do you need beyond `members` and `books`?

<details class="solution"><summary>Solution</summary>

Members and books are many-to-many, so add a `loans` link table:
`loans(loan_id, member_id, book_id, loaned_on, returned_on)`. It has two foreign keys. It gets its own
`loan_id` because the same member can borrow the same book more than once on different dates.

</details>

**Exercise 2 · Where does the foreign key go?** One `customers` row has many `orders`. Which table
gets the `customer_id` column?

<details class="solution"><summary>Solution</summary>

`orders`, the "many" side. Each order stores the id of its one customer.

</details>

**Exercise 3 · Add genre.** A movie can belong to several genres. Sketch the change to the tables.

<details class="solution"><summary>Solution</summary>

Replace the single `genre` column with a `genres(genre_id, name)` table and a link table
`movie_genres(movie_id, genre_id)` with a two-column primary key, the same pattern as `movie_cast`.

</details>

## Practice

Take the **Session 6 quiz** on cardinality. The original lessons on entities, identifiers,
relationships and attributes, plus DB-TASK-003, are in the reference section.
