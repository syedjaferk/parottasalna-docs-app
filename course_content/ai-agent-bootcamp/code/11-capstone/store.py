# store.py - the bot's long-term memory: every message goes into a small SQLite database file.
# SQLite is built into Python: no server to install. The whole database is ONE file: support.db
import sqlite3
from datetime import date, datetime

DB_FILE = "support.db"


def connect():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row          # lets us read columns by name: row["text"]
    return conn


def init():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                ts       TEXT    NOT NULL,
                chat_id  INTEGER NOT NULL,
                user_id  INTEGER NOT NULL,
                role     TEXT    NOT NULL,      -- 'user' or 'assistant'
                text     TEXT    NOT NULL,
                guard    TEXT,                  -- allow / review / block
                category TEXT,
                urgent   REAL,
                tier     TEXT                   -- cheap / strong / blocked / human_review
            )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chat ON messages (chat_id, id)")


def add_message(chat_id, user_id, role, text, guard=None, category=None, urgent=None, tier=None):
    with connect() as conn:
        conn.execute(
            "INSERT INTO messages (ts, chat_id, user_id, role, text, guard, category, urgent, tier) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (datetime.now().isoformat(timespec="seconds"), chat_id, user_id, role, text, guard, category, urgent, tier),
        )                                       # the ? marks are filled in safely: never build SQL with f-strings!


def recent(chat_id, limit=6):
    """The last few SAFE messages of a chat, oldest first, ready to send to the LLM."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT role, text FROM messages WHERE chat_id = ? AND (guard IS NULL OR guard = 'allow') "
            "ORDER BY id DESC LIMIT ?", (chat_id, limit)).fetchall()
    return [{"role": r["role"], "content": r["text"]} for r in reversed(rows)]


def day_rows(day=None):
    """All USER messages of one day (default: today)."""
    day = day or date.today().isoformat()
    with connect() as conn:
        return conn.execute("SELECT * FROM messages WHERE role = 'user' AND ts LIKE ? ORDER BY id",
                            (day + "%",)).fetchall()


def stats(day=None):
    rows = day_rows(day)
    by_category, by_tier = {}, {}
    for r in rows:
        by_category[r["category"] or "none"] = by_category.get(r["category"] or "none", 0) + 1
        by_tier[r["tier"] or "none"] = by_tier.get(r["tier"] or "none", 0) + 1
    return {
        "date": day or date.today().isoformat(),
        "messages": len(rows),
        "customers": len({r["user_id"] for r in rows}),
        "blocked": sum(1 for r in rows if r["guard"] == "block"),
        "review": sum(1 for r in rows if r["guard"] == "review"),
        "urgent": [r["text"][:80] for r in rows if (r["urgent"] or 0) >= 0.8],
        "by_category": by_category,
        "by_tier": by_tier,
    }
