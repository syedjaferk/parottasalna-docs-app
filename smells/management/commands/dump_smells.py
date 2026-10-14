"""Write every code smell (with its quiz) to JSON, in the format ``load_smells`` reads.

    python manage.py dump_smells > backup.json
"""
import json

from django.core.management.base import BaseCommand

from smells.management.commands.load_smells import FIELDS
from smells.models import CodeSmell


class Command(BaseCommand):
    help = "Dump code smells and quizzes as JSON to stdout."

    def handle(self, *args, **options):
        rows = []
        for smell in CodeSmell.objects.select_related("quiz").order_by("order", "id"):
            row = {"slug": smell.slug, "order": smell.order, **{f: getattr(smell, f) for f in FIELDS}}
            quiz = getattr(smell, "quiz", None)
            if quiz:
                row["quiz"] = {"question": quiz.question, "choices": quiz.choices, "answer": quiz.answer,
                               "explanation": quiz.explanation}
            rows.append(row)
        self.stdout.write(json.dumps({"version": 1, "code_smells": rows}, indent=2, ensure_ascii=False))
