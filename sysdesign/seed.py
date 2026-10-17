"""Copies ``sysdesign/data/*.json`` into ``Problem`` rows. Safe to run repeatedly."""
import json
from pathlib import Path

from .models import Problem

DATA_DIR = Path(__file__).resolve().parent / "data"
CONTENT_FIELDS = ("title", "tagline", "difficulty", "minutes", "course_slug", "statement", "steps")


def load_problems(data_dir=DATA_DIR):
    """Create or update one Problem per JSON file. Admin-owned fields (is_pro, is_published, position) are
    only set on creation, so edits made in the admin survive a re-run. Returns (created, updated)."""
    created = updated = 0
    for position, path in enumerate(sorted(Path(data_dir).glob("*.json"))):
        data = json.loads(path.read_text(encoding="utf-8"))
        slug = data.get("slug") or path.stem
        content = {k: data[k] for k in CONTENT_FIELDS if k in data}
        obj, was_created = Problem.objects.get_or_create(slug=slug, defaults={**content, "position": data.get("position", position), "is_pro": bool(data.get("is_pro", False))})
        if was_created:
            created += 1
        elif any(getattr(obj, k) != v for k, v in content.items()):
            for k, v in content.items():
                setattr(obj, k, v)
            obj.save()
            updated += 1
    return created, updated
