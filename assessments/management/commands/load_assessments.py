"""Load timed assessments from YAML files kept next to a course's docs.

Files live in ``course_content/<course>/assessments/*.yaml``::

    slug: linux-basics-exam
    title: "Linux Basics · Final exam"
    description: Optional intro.
    time_limit_minutes: 20
    pass_percentage: 70
    max_attempts: 2
    publish: true
    questions:
      - text: Which command prints the current directory?
        choices: |
          *pwd
          ls
          cd
        explanation: Optional.

Assessments are matched by slug; questions are updated in place by position, so loading again keeps attempts.
"""
from pathlib import Path

import yaml
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from assessments.models import Assessment, AssessmentQuestion
from courses.models import Course


class Command(BaseCommand):
    help = "Create or update timed assessments from course_content/<course>/assessments/*.yaml."

    def add_arguments(self, parser):
        parser.add_argument("course", help="Course slug.")

    @transaction.atomic
    def handle(self, *args, course, **options):
        try:
            course_obj = Course.objects.get(slug=course)
        except Course.DoesNotExist:
            raise CommandError(f"No course with slug '{course}'.")
        folder = course_obj.src_dir / "assessments"
        files = sorted(folder.glob("*.yaml")) if folder.is_dir() else []
        if not files:
            self.stdout.write(f"{course}: no assessments folder.")
            return
        for path in files:
            self._load(course_obj, path)

    def _load(self, course, path: Path):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            slug, title = data["slug"], data["title"]
            rows = data["questions"]
        except (OSError, yaml.YAMLError, KeyError, TypeError) as error:
            raise CommandError(f"{path.name}: {error}")
        assessment, created = Assessment.objects.get_or_create(slug=slug, defaults={"title": title, "course": course})
        assessment.course = course
        assessment.title = title
        assessment.description = (data.get("description") or "").strip()
        assessment.time_limit_minutes = data.get("time_limit_minutes", 30)
        assessment.pass_percentage = data.get("pass_percentage", 60)
        assessment.max_attempts = data.get("max_attempts", 1)
        assessment.shuffle_questions = data.get("shuffle_questions", True)
        assessment.show_answers = data.get("show_answers", True)
        assessment.is_published = bool(data.get("publish", True))
        try:
            assessment.full_clean(exclude=["slug"])
            assessment.save()
            existing = list(assessment.questions.order_by("order", "id"))
            for position, row in enumerate(rows):
                fields = {"text": row["text"].strip(), "choices": row["choices"].strip(),
                          "explanation": (row.get("explanation") or "").strip(),
                          "points": row.get("points", 1), "order": position}
                obj = existing[position] if position < len(existing) else AssessmentQuestion(assessment=assessment)
                for name, value in fields.items():
                    setattr(obj, name, value)
                obj.full_clean()
                obj.save()
            for obj in existing[len(rows):]:
                obj.delete()
        except (ValidationError, KeyError) as error:
            raise CommandError(f"{path.name}: {error}")
        self.stdout.write(self.style.SUCCESS(f"{course.slug}: assessment '{slug}' {'created' if created else 'updated'} "
                                             f"({len(rows)} questions, {assessment.time_limit_minutes} min)"))
