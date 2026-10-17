# Session 1 · Why we need a database

## The big idea

Every app remembers things: movies, customers, orders, marks. The first place most of us put that
data is a **flat file**, a plain text file with one record per line. That works for ten lines. It
starts to hurt at ten thousand, and it breaks when two people use it at once. A **database** is the
answer to those pains: one agreed place to store data, with rules, fast search and safe updates.

**Everyday example:** a school's paper register. For one class it is fine. Now imagine the headmaster
asks, "Which students have more than 90% attendance *and* live in Chennai?" With a hundred loose
registers you read every page. With an organised system (an index, one card per student) you look in
two places. A database is that organised system for your program.

```{raw} html
:file: ../diagrams/flat-vs-db.html
```

## A flat file in action

`movies-flat.txt` holds five Tamil films, one per line, fields separated by `|`.

```{literalinclude} ../code/movies-flat.txt
:language: text
```

Searching works, until you want to *change* something. These shell commands read and edit the file;
the output below is what they printed.

```{literalinclude} ../code/01-flat-file.sh
:language: bash
```

```{literalinclude} ../code/01-flat-file.out
:language: text
```

Look at what happened:

- Finding the director's films needed a text search (`grep`) that only works because we know the
  file layout.
- To rename a director we had to rewrite **every line** that mentions them (two lines here, two
  thousand in a real file).
- One typo (`Ratnum`) quietly created a *second* director. Nothing in a text file says "this name
  must match an existing one".

## The repeating group problem

What if a film has several actors? In a flat file you either add more columns (`actor1`, `actor2`,
`actor3`... and what about a fourth?) or you squeeze a list into one field (`Rajinikanth;Mammootty`)
that is hard to search and hard to sort. This is called a **repeating group**, and it is the problem
that pushed people to invent databases.

A slightly smarter text format, such as an `.ini` file with several `starring=` lines, fixes the shape
but now **your program has to parse it**, and still nothing checks the values. You will end up
writing your own half-database. That is the signal to use a real one.

## What a database gives you

| Pain with a flat file | What a database does |
|---|---|
| Same name copied on many lines | Store it once; link to it |
| Typos create fake records | Rules (constraints) reject bad data |
| Slow search as the file grows | Indexes find rows without reading everything |
| Two people editing at once corrupt the file | Transactions keep changes safe |
| Every program parses the file its own way | One language, SQL, for everyone |

## Common mistakes

- **"A database is just a bigger spreadsheet."** A spreadsheet can't stop you typing "Mani Ratnum".
  A database can refuse it.
- **Using a text file because it feels simpler.** It is simpler for the first hour. Move to a
  database as soon as two things need to point at each other (movies and directors, orders and
  customers).
- **Splitting a list into one cell.** `"Rajinikanth;Mammootty"` in one column cannot be counted or
  joined properly. Use another table (you will build exactly that in Session 6).
- **Believing databases are only for huge data.** They are for *related* data and for safety, at any
  size.

## Hands-on exercises

**Exercise 1 · Spot the pain.** Using `movies-flat.txt`, write a shell command that prints how many
films each director made. Then say what would go wrong if one line had a trailing space after the
director's name.

<details class="solution"><summary>Solution</summary>

```bash
cut -d'|' -f2 movies-flat.txt | sort | uniq -c
```

It counts by exact text, so `Mani Ratnam` and `Mani Ratnam ` (with a trailing space) are counted as
two different directors. A database column with a foreign key to a directors table cannot have that
problem.

</details>

**Exercise 2 · Repeating group.** A new film "Vikram" has four actors. Show two ways to put them in
`movies-flat.txt`, and list one disadvantage of each.

<details class="solution"><summary>Solution</summary>

1. More columns: `Vikram|Lokesh Kanagaraj|2022|Action|Kamal Haasan|Suriya|Fahadh Faasil|Vijay Sethupathi`.
   Every other line needs the same number of columns, and a fifth actor means changing the layout of
   the whole file.
2. One packed field: `Vikram|Lokesh Kanagaraj|2022|Action|Kamal Haasan;Suriya;Fahadh Faasil;Vijay Sethupathi`.
   Counting or searching "films with Suriya" needs custom splitting code.

A database stores each actor in its own row of a separate table instead (Session 6).

</details>

**Exercise 3 · Your own data.** Pick something you track (books you read, expenses). Write three
sample lines, then name one question you would ask of that data that is awkward in a text file.

<details class="solution"><summary>Solution</summary>

There is no single right answer. A good one: expenses with `date|category|amount` lines; the awkward
question is "total spent per category per month", which needs grouping that a text file cannot do on
its own but SQL does in one query (`GROUP BY`).

</details>

## Practice

Take the **Session 1 quiz** in the portal: it checks flat files, repeating groups and what a
database adds.
