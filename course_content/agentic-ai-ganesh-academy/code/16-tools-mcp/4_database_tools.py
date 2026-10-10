"""
4. Database Tools - let an agent answer questions from a SQL database.
SQLite is used so the demo runs anywhere. The same pattern works for Postgres/MySQL.

Safety layers (IMPORTANT for the session):
  1. Read-only DB connection  (the database itself refuses writes)
  2. SELECT-only check        (tool refuses anything else)
  3. Row limit                (agent can't dump a huge table into the context)
"""

import re
import sqlite3
from pathlib import Path

from langchain.agents import create_agent
from langchain.tools import tool
from model import model

DB_PATH = Path(__file__).parent / "shop.db"
MAX_ROWS = 50


def setup_demo_db() -> None:
    """Create a small sample database (runs once)."""
    if DB_PATH.exists():
        return
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT);
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(id),
            product TEXT, amount REAL, order_date TEXT
        );
        INSERT INTO customers VALUES
            (1,'Arun','Chennai'),(2,'Priya','Bangalore'),(3,'Karthik','Chennai'),(4,'Meena','Madurai');
        INSERT INTO orders VALUES
            (1,1,'Laptop',65000,'2026-08-01'),(2,1,'Mouse',800,'2026-08-03'),
            (3,2,'Keyboard',2500,'2026-08-10'),(4,3,'Monitor',12000,'2026-09-02'),
            (5,3,'Laptop',58000,'2026-09-15'),(6,4,'Headphones',3000,'2026-09-20');
        """
    )
    conn.commit()
    conn.close()


def _connect_readonly() -> sqlite3.Connection:
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)


@tool
def list_tables() -> str:
    """List all tables in the database with their columns. Call this first."""
    conn = _connect_readonly()
    try:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        out = []
        for (name,) in tables:
            cols = conn.execute(f"PRAGMA table_info({name})").fetchall()
            out.append(f"{name}({', '.join(c[1] + ' ' + c[2] for c in cols)})")
        return "\n".join(out)
    finally:
        conn.close()


@tool
def run_sql_query(query: str) -> str:
    """Run a read-only SQL SELECT query and return the rows.
    Only SELECT statements are allowed. Use list_tables first to learn the schema."""
    q = query.strip().rstrip(";")
    if not re.match(r"(?is)^\s*select\b", q) or ";" in q:
        return "Error: only a single SELECT statement is allowed."

    conn = _connect_readonly()
    try:
        cur = conn.execute(q)
        headers = [d[0] for d in cur.description]
        rows = cur.fetchmany(MAX_ROWS)
        if not rows:
            return "No rows returned."
        lines = [" | ".join(headers)] + [" | ".join(map(str, r)) for r in rows]
        return "\n".join(lines)
    except sqlite3.Error as e:
        # Returning the error lets the agent fix its own SQL and retry
        return f"SQL error: {e}"
    finally:
        conn.close()


setup_demo_db()

agent = create_agent(
    model,
    tools=[list_tables, run_sql_query],
    system_prompt=(
        "You are a data analyst. Always inspect the schema with list_tables first, "
        "then write a SELECT query. Explain the answer in plain English."
    ),
)

if __name__ == "__main__":
    question = "Which customer from Chennai has spent the most in total, and how much?"
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    for m in result["messages"]:
        m.pretty_print()
