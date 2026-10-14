"""Load (or restore) code smells from a JSON file; matched by slug so it is safe to re-run.

    python manage.py load_smells                 # smells/data/code_smells.json
    python manage.py load_smells backup.json
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from smells.models import CodeSmell, SmellQuiz

DEFAULT_FILE = Path(__file__).resolve().parents[2] / "data" / "code_smells.json"
FIELDS = ("number", "title", "level", "tags", "summary", "problem", "why_bad", "bad_code", "good_code",
          "language", "fix", "source_url", "is_active")


class Command(BaseCommand):
    help = "Create or update code smells (and their quizzes) from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument("file", nargs="?", default=str(DEFAULT_FILE))

    @transaction.atomic
    def handle(self, *args, file, **options):
        try:
            data = json.loads(Path(file).read_text(encoding="utf-8"))
            rows = data["code_smells"]
        except (OSError, ValueError, KeyError) as exc:
            raise CommandError(f"Can't read {file}: {exc}")
        created = 0
        for position, row in enumerate(rows):
            defaults = {f: row[f] for f in FIELDS if f in row}
            defaults["order"] = row.get("order", position)
            smell, new = CodeSmell.objects.update_or_create(slug=row["slug"], defaults=defaults)
            created += new
            quiz = row.get("quiz")
            if quiz:
                obj = SmellQuiz(smell=smell, question=quiz["question"], choices=quiz["choices"],
                                answer=quiz["answer"], explanation=quiz.get("explanation", ""))
                obj.clean()
                SmellQuiz.objects.update_or_create(smell=smell, defaults={
                    "question": obj.question, "choices": obj.choices, "answer": obj.answer,
                    "explanation": obj.explanation})
        self.stdout.write(self.style.SUCCESS(f"{len(rows)} smells loaded ({created} new)."))
