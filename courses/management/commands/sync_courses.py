"""Create a Course row for every course_content/<folder> that has a course.yaml and no course yet.

    course_content/linux-basics/course.yaml:
        title: Linux Basics
        description: One or two sentences for the course card.
        common: false          # true = public notes for everyone (optional, default false)

Only MISSING courses are created. Existing ones are never changed (so edits made in the admin are kept),\nexcept that --update fills catalogue fields that are still blank.
deploy_content runs this first, so pushing a new course folder is enough to make it appear.
"""
import yaml
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from courses.models import Course


def catalogue_fields(meta):
    """Catalogue values from course.yaml. Lists are joined one item per line."""
    outcomes = meta.get("outcomes") or ""
    if isinstance(outcomes, list):
        outcomes = "\n".join(str(o) for o in outcomes)
    common = bool(meta.get("common", False))
    access = meta.get("access") or ("free" if common else "invite")
    fields = {
        "access": access if access in {"free", "pro", "invite"} else "invite",
        "level": meta.get("level") if meta.get("level") in {"beginner", "intermediate", "advanced"} else "",
        "est_hours": meta.get("hours") if isinstance(meta.get("hours"), int) else None,
        "audience": str(meta.get("audience") or "").strip(),
        "outcomes": str(outcomes).strip(),
    }
    return fields


class Command(BaseCommand):
    help = "Create missing Course rows from course_content/*/course.yaml."

    def add_arguments(self, parser):
        parser.add_argument("--update", action="store_true",
                            help="Also fill BLANK catalogue fields (level, hours, audience, outcomes) on existing courses.")

    def handle(self, *args, **options):
        root = settings.COURSES_SRC_ROOT
        created = updated = 0
        for folder in sorted(p for p in root.iterdir() if p.is_dir()) if root.is_dir() else []:
            meta_file = folder / "course.yaml"
            if not meta_file.is_file():
                continue
            slug = folder.name
            try:
                meta = yaml.safe_load(meta_file.read_text(encoding="utf-8")) or {}
            except (OSError, yaml.YAMLError) as error:
                self.stderr.write(self.style.ERROR(f"{slug}: bad course.yaml: {error}"))
                continue
            extra = catalogue_fields(meta)
            existing = Course.objects.filter(Q(slug=slug) | Q(source_dir=slug)).first()
            if existing:
                if options["update"]:
                    changed = [f for f in ("level", "est_hours", "audience", "outcomes")
                               if extra[f] not in ("", None) and getattr(existing, f) in ("", None)]
                    for f in changed:
                        setattr(existing, f, extra[f])
                    if changed:
                        existing.save(update_fields=changed)
                        updated += 1
                        self.stdout.write(f"{slug}: filled {', '.join(changed)}")
                continue
            Course.objects.create(slug=slug, source_dir=slug, title=meta.get("title") or slug.replace("-", " ").title(),
                                  description=(meta.get("description") or "").strip(),
                                  is_common=bool(meta.get("common", False)), is_active=True, **extra)
            created += 1
            self.stdout.write(self.style.SUCCESS(f"{slug}: course created"))
        if not created and not updated:
            self.stdout.write("sync_courses: nothing to do.")
