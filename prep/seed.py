"""Copies ``prep/data/*.json`` (catalog, pattern guides, placement quiz) into the database. Idempotent:
re-running updates rows to match the files and removes rows the files no longer have."""
import json
from pathlib import Path

from django.db import transaction

from . import catalog as cat_module
from .models import CatalogLookup, CatalogProblem, CatalogSheet, PatternGuide, PlacementQuestion

DATA_DIR = Path(__file__).resolve().parent / "data"
LOOKUPS = ("topics", "patterns", "companies", "difficulties")


def _read(data_dir, name):
    return json.loads((Path(data_dir) / f"{name}.json").read_text(encoding="utf-8"))


def _sync(model, key, wanted):
    """Make ``model`` rows match ``wanted`` ({key value: field dict}). Returns (created, updated, deleted)."""
    existing = {getattr(o, key): o for o in model.objects.all()}
    new, changed = [], []
    fields = set()
    for k, values in wanted.items():
        obj = existing.get(k)
        if obj is None:
            new.append(model(**{key: k}, **values))
        elif any(getattr(obj, f) != v for f, v in values.items()):
            for f, v in values.items():
                setattr(obj, f, v)
            changed.append(obj)
            fields.update(values)
    stale = [o.pk for k, o in existing.items() if k not in wanted]
    model.objects.bulk_create(new, batch_size=500)
    if changed:
        model.objects.bulk_update(changed, sorted(fields), batch_size=500)
    if stale:
        model.objects.filter(pk__in=stale).delete()
    return len(new), len(changed), len(stale)


@transaction.atomic
def seed_prep(data_dir=DATA_DIR):
    """Returns {table: (created, updated, deleted)}."""
    catalog = _read(data_dir, "catalog")
    guides = _read(data_dir, "pattern_guides")
    questions = _read(data_dir, "placement")
    report = {}
    report["lookups"] = _sync(CatalogLookup, "name", {n: {"values": catalog[n]} for n in LOOKUPS})
    report["problems"] = _sync(CatalogProblem, "pid", {
        p["id"]: {"position": i, "title": p["t"], "platform": p["pl"], "url": p["u"], "difficulty": p["d"],
                  "tags": p["tg"], "patterns": p["pa"], "companies": p["co"]}
        for i, p in enumerate(catalog["problems"])})
    report["sheets"] = _sync(CatalogSheet, "sheet_id", {
        s["id"]: {"position": i, "name": s["name"], "by": s.get("by", ""), "kind": s.get("kind", ""), "items": s["items"]}
        for i, s in enumerate(catalog["sheets"])})
    report["guides"] = _sync(PatternGuide, "pattern", {
        name: {"position": i, **{f: g[f] for f in ("kid", "when", "time", "space", "session")}} for i, (name, g) in enumerate(guides.items())})
    report["questions"] = _sync(PlacementQuestion, "qid", {
        q["id"]: {"position": i, "pattern": q["pattern"], "q": q["q"], "options": q["options"], "answer": q["answer"], "why": q["why"], "session": q["session"]}
        for i, q in enumerate(questions)})
    cat_module.invalidate()
    return report
