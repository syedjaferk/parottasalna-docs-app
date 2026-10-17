"""Loads the generated JSON files in ``prep/data`` (see ``manage.py build_prep_catalog``)."""
import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"


def _read(name):
    return json.loads((DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def catalog():
    """The problem catalog, with a few lookups added: ``by_id``, ``by_pattern`` and a ``pop`` score per problem."""
    data = _read("catalog")
    sheet_count = {}
    for sheet in data["sheets"]:
        for idx, *_ in sheet["items"]:
            sheet_count[idx] = sheet_count.get(idx, 0) + 1
    by_pattern = {name: [] for name in data["patterns"]}
    for i, p in enumerate(data["problems"]):
        # Popularity: appears in many curated sheets, is asked often by companies, and has a LeetCode page to open.
        p["pop"] = sheet_count.get(i, 0) * 2 + sum(f for _, f in p["co"]) * 0.5 + (1 if p["pl"] == "leetcode" else 0)
        for pa in p["pa"]:
            by_pattern[data["patterns"][pa]].append(i)
    data["by_id"] = {p["id"]: i for i, p in enumerate(data["problems"])}
    data["by_pattern"] = by_pattern
    return data


def problem_ids():
    return frozenset(catalog()["by_id"])


@lru_cache(maxsize=1)
def pattern_guides():
    return _read("pattern_guides")
