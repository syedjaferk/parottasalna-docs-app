"""The prep content (problem catalog, pattern guides, placement quiz), read from the database.

``prep/data/*.json`` are only the seed files (``manage.py seed_prep``); ``manage.py build_prep_catalog`` regenerates
``catalog.json`` from the source sheets. Results are cached per process for a few minutes and dropped whenever a
row is saved in the admin (see ``PrepConfig.ready``).
"""
import json
import time
from threading import Lock

from .models import CatalogLookup, CatalogProblem, CatalogSheet, PatternGuide, PlacementQuestion

CACHE_SECONDS = 300
_lock = Lock()
_cache = {}


def invalidate():
    with _lock:
        _cache.clear()


def _cached(key, build):
    with _lock:
        hit = _cache.get(key)
        if hit and hit[0] > time.monotonic():
            return hit[1]
    value = build()
    with _lock:
        _cache[key] = (time.monotonic() + CACHE_SECONDS, value)
    return value


def _raw_catalog():
    """The catalog in the same shape as the original catalog.json."""
    data = {name: [] for name in ("topics", "patterns", "companies", "difficulties")}
    for row in CatalogLookup.objects.all():
        data[row.name] = row.values
    return {
        "problems": [{"id": p.pid, "t": p.title, "pl": p.platform, "u": p.url, "d": p.difficulty, "tg": p.tags, "pa": p.patterns, "co": p.companies}
                     for p in CatalogProblem.objects.all()],
        "sheets": [{"id": s.sheet_id, "name": s.name, "by": s.by, "kind": s.kind, "items": s.items} for s in CatalogSheet.objects.all()],
        **data,
    }


def catalog_json():
    """catalog.json as bytes, for the browser."""
    return _cached("catalog_json", lambda: json.dumps(_raw_catalog(), ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def pattern_guides_json():
    return _cached("guides_json", lambda: json.dumps(pattern_guides(), ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def _build_catalog():
    data = json.loads(catalog_json())      # a fresh copy: the lookups below are added in place
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


def catalog():
    """The problem catalog, with a few lookups added: ``by_id``, ``by_pattern`` and a ``pop`` score per problem."""
    return _cached("catalog", _build_catalog)


def problem_ids():
    return frozenset(catalog()["by_id"])


def pattern_guides():
    return _cached("guides", lambda: {g.pattern: {"kid": g.kid, "when": g.when, "time": g.time, "space": g.space, "session": g.session}
                                      for g in PatternGuide.objects.all()})


def placement_questions():
    return _cached("placement", lambda: [{"id": q.qid, "pattern": q.pattern, "q": q.q, "options": q.options, "answer": q.answer,
                                          "why": q.why, "session": q.session} for q in PlacementQuestion.objects.all()])
