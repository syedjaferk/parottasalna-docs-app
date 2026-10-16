"""Create a Course row for every course_content/<folder> that has a course.yaml and no course yet.

    course_content/linux-basics/course.yaml:
        title: Linux Basics
        description: One or two sentences for the course card.
        common: false          # true = public notes for everyone (optional, default false)

Only MISSING courses are created. Existing ones are never changed, so edits made in the admin are kept.
deploy_content runs this first, so pushing a new course folder is enough to make it appear.
"""
import yaml
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from courses.models import Course


class Command(BaseCommand):
    help = "Create missing Course rows from course_content/*/course.yaml."

    def handle(self, *args, **options):
        root = settings.COURSES_SRC_ROOT
        created = 0
        for folder in sorted(p for p in root.iterdir() if p.is_dir()) if root.is_dir() else []:
            meta_file = folder / "course.yaml"
            if not meta_file.is_file():
                continue
            slug = folder.name
            if Course.objects.filter(Q(slug=slug) | Q(source_dir=slug)).exists():
                continue
            try:
                meta = yaml.safe_load(meta_file.read_text(encoding="utf-8")) or {}
            except (OSError, yaml.YAMLError) as error:
                self.stderr.write(self.style.ERROR(f"{slug}: bad course.yaml: {error}"))
                continue
            Course.objects.create(slug=slug, source_dir=slug, title=meta.get("title") or slug.replace("-", " ").title(),
                                  description=(meta.get("description") or "").strip(),
                                  is_common=bool(meta.get("common", False)), is_active=True)
            created += 1
            self.stdout.write(self.style.SUCCESS(f"{slug}: course created"))
        if not created:
            self.stdout.write("sync_courses: no new courses.")
