"""Loads the generated JSON files in ``prep/data`` (see ``manage.py build_prep_catalog``)."""
import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
MATERIALS = {"hr", "sql", "cs", "roles", "system_design", "notes", "playlists", "cold_emails", "resumes"}


@lru_cache(maxsize=1)
def problem_ids():
    return frozenset(p["id"] for p in json.loads((DATA_DIR / "catalog.json").read_text(encoding="utf-8"))["problems"])
