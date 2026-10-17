"""Diagrams for the Database Engineering course. Run:  python course_content/database-engineering/diagrams/make_diagrams.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "docs"))
from diagram_kit import D  # noqa: E402


def new(name, w, h, title, caption):
    return D(name, w, h, title, caption, HERE)


def flat_vs_db():
    d = new("flat-vs-db", 760, 260, "A flat file versus a database",
            "In a flat file the director's name is copied onto every line; in a database it is stored once and each movie points to it.")
    d.box(20, 20, 330, 40, ("Flat file: name repeated", "bold"), "red")
    for i, t in enumerate(["Nayakan | Mani Ratnam | 1987", "Thalapathi | Mani Ratnam | 1991", "Baasha | Suresh Krissna | 1995"]):
        d.box(20, 75 + i * 44, 330, 36, (t, "code"), "box", rx=6)
    d.text(185, 225, "rename a director = edit every line", "small")
    d.box(410, 20, 330, 40, ("Database: stored once, linked", "bold"), "green")
    d.box(410, 75, 140, 36, ("1 · Mani Ratnam", "code"), "green", rx=6)
    d.box(410, 119, 140, 36, ("2 · Suresh Krissna", "code"), "green", rx=6)
    for i, (t, to) in enumerate([("Nayakan → 1", 93), ("Thalapathi → 1", 93), ("Baasha → 2", 137)]):
        y = 75 + i * 44
        d.box(610, y, 130, 36, (t, "code"), "box", rx=6)
        d.arrow([(608, y + 18), (552, to)], kind="blue")
    d.text(575, 225, "rename a director = edit one row", "small")
    return d.render()


def dbms_layers():
    d = new("dbms-layers", 760, 250, "Apps talk to the DBMS, not to the files",
            "Applications send SQL to the DBMS, which reads and writes the database files on disk, checks the rules and handles many users at once.")
    d.box(20, 30, 170, 70, [("Web app", "bold"), ("INSERT, SELECT", "small")], "blue")
    d.box(20, 130, 170, 70, [("Report script", "bold"), ("SELECT", "small")], "blue")
    d.box(280, 60, 200, 110, [("DBMS", "bold"), ("PostgreSQL", "code"), ("rules · users · speed", "small")], "amber")
    d.box(570, 60, 170, 110, [("Database", "bold"), ("files on disk", "small")], "green")
    d.arrow([(192, 65), (278, 100)], kind="blue", label="SQL", lx=235, ly=70)
    d.arrow([(192, 165), (278, 130)], kind="blue")
    d.arrow([(482, 115), (568, 115)], kind="green", label="reads / writes", lx=525, ly=100)
    return d.render()


def relational_keys():
    d = new("relational-keys", 760, 270, "Tables, primary keys and foreign keys",
            "directors and movies are two tables. movies.director_id is a foreign key that points at directors.director_id.")
    d.box(20, 20, 250, 36, ("directors", "bold"), "blue")
    d.box(20, 60, 250, 30, ("director_id (PK)   name", "code"), "ghost", rx=4)
    for i, t in enumerate(["1   Mani Ratnam", "5   Mari Selvaraj", "6   Lokesh Kanagaraj"]):
        d.box(20, 96 + i * 34, 250, 30, (t, "code"), "box", rx=4)
    d.box(380, 20, 360, 36, ("movies", "bold"), "green")
    d.box(380, 60, 360, 30, ("movie_id (PK)  title  year  director_id (FK)", "code"), "ghost", rx=4)
    for i, (t, y) in enumerate([("1   Nayakan     1987   1", 96), ("9   Karnan      2021   5", 130), ("10  Vikram      2022   6", 164)]):
        d.box(380, y, 360, 30, (t, "code"), "box", rx=4)
    d.arrow([(378, 111), (272, 111)], kind="red")
    d.arrow([(378, 145), (272, 145)], kind="red", dashed=True)
    d.text(380, 240, "The arrow is the foreign key: a movie may only point at a director that exists.", "small")
    return d.render()


def select_flow():
    d = new("select-flow", 760, 230, "The order a query is read in",
            "You write SELECT first, but the database works FROM table, then WHERE, then picks columns, then ORDER BY and LIMIT.")
    steps = [("FROM", "which table", "blue"), ("WHERE", "which rows", "green"), ("SELECT", "which columns", "amber"),
             ("ORDER BY", "what order", "blue"), ("LIMIT", "how many", "green")]
    for i, (a, b, k) in enumerate(steps):
        x = 15 + i * 148
        d.box(x, 40, 126, 80, [(a, "bold"), (b, "small")], k)
        if i:
            d.arrow([(x - 20, 80), (x - 2, 80)], kind="blue")
    d.box(15, 150, 730, 56, [("SELECT title, year FROM movies WHERE genre = 'Action' ORDER BY year LIMIT 3;", "code")], "ghost")
    return d.render()


def filter_funnel():
    d = new("filter-funnel", 760, 250, "Filters narrow the rows",
            "Eleven movies go in; WHERE genre = 'Action' keeps four; AND year > 2000 keeps three.")
    for i, (n, t, w, k) in enumerate([(11, "all movies", 640, "box"), (4, "genre = 'Action'", 320, "blue"), (3, "AND year > 2000", 240, "green")]):
        x = 20 + (640 - w) / 2 + (0)
        d.box(x + 40, 20 + i * 70, w, 54, [(f"{n} rows", "bold"), (t, "small")], k)
    d.text(380, 230, "each condition only removes rows, never adds", "small")
    return d.render()


def er_cinema():
    d = new("er-cinema", 760, 270, "ER diagram for the movie database",
            "A director directs many movies (one-to-many). Movies and actors are many-to-many, so they meet in the movie_cast table.")
    d.box(20, 90, 150, 70, [("directors", "bold"), ("director_id", "code")], "blue")
    d.box(250, 90, 150, 70, [("movies", "bold"), ("movie_id", "code")], "green")
    d.box(480, 90, 120, 70, [("movie_cast", "bold"), ("movie_id + actor_id", "small")], "amber")
    d.box(640, 90, 100, 70, [("actors", "bold"), ("actor_id", "code")], "blue")
    d.arrow([(172, 125), (248, 125)], kind="blue", head=True)
    d.text(210, 105, "1 : many", "small")
    d.arrow([(402, 125), (478, 125)], kind="blue")
    d.text(440, 105, "1 : many", "small")
    d.arrow([(638, 125), (602, 125)], kind="blue")
    d.text(620, 105, "1 : many", "small")
    d.text(380, 215, "many-to-many = two one-to-many links through a middle table", "small")
    return d.render()


def join_types():
    d = new("join-types", 760, 260, "Which rows each join keeps",
            "INNER JOIN keeps only matches. LEFT JOIN keeps every left row and fills the right side with NULL when nothing matches.")
    d.box(20, 20, 340, 36, ("INNER JOIN", "bold"), "green")
    d.box(20, 66, 150, 120, [("movies", "bold"), ("10 with a director", "small")], "box")
    d.box(190, 66, 150, 120, [("directors", "bold"), ("matches only", "small")], "box")
    d.text(190, 215, "10 rows: Untitled Project and Vetrimaaran drop out", "small")
    d.box(400, 20, 340, 36, ("LEFT JOIN movies → directors", "bold"), "amber")
    d.box(400, 66, 150, 120, [("movies", "bold"), ("all 11 kept", "small")], "box")
    d.box(570, 66, 150, 120, [("directors", "bold"), ("NULL if no match", "small")], "box")
    d.text(570, 215, "11 rows: Untitled Project has director NULL", "small")
    return d.render()


def join_chain():
    d = new("join-chain", 760, 230, "Three tables, two joins",
            "orders sits in the middle: one join reaches customers and another reaches products.")
    d.box(20, 80, 180, 70, [("customers", "bold"), ("customer_id", "code")], "blue")
    d.box(290, 80, 180, 70, [("orders", "bold"), ("customer_id, product_id", "code")], "amber")
    d.box(560, 80, 180, 70, [("products", "bold"), ("product_id", "code")], "green")
    d.arrow([(290, 115), (202, 115)], kind="blue", label="ON customer_id", lx=245, ly=95)
    d.arrow([(472, 115), (558, 115)], kind="green", label="ON product_id", lx=515, ly=95)
    d.text(380, 200, "FROM orders JOIN customers ... JOIN products ...", "code")
    return d.render()


if __name__ == "__main__":
    fns = [flat_vs_db, dbms_layers, relational_keys, select_flow, filter_funnel, er_cinema, join_types, join_chain]
    for fn in fns:
        fn()
    print(len(fns), "diagrams written")
