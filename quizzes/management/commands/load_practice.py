"""Load quizzes and flashcard decks from YAML files kept next to a course's docs.

Files live in ``course_content/<course>/practice/*.yaml``, one per chapter::

    chapter: sessions/01-why-docker
    quizzes:
      - title: "Session 1 · Concepts"
        description: Optional intro.
        questions:
          - text: What does a container share with the host?
            choices: |
              *The Linux kernel
              Nothing at all
            explanation: Optional, shown after submitting.
    decks:
      - title: "Session 1 · Flashcards"
        cards:
          - front: Image
            back: A read-only template.

Choices use the same format as the admin: one per line, correct ones start with ``*``
(use a ``|`` block so YAML doesn't read ``*`` as an alias).

Quizzes and decks are matched by course + chapter + title, and their questions and cards are
updated in place by position, so loading again keeps students' attempts and card progress.
"""

from pathlib import Path

import yaml
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.models import Course
from quizzes.models import Deck, Flashcard, Question, Quiz, clean_chapter


def _sync_children(manager, rows, make):
    """Update existing children by position, add new ones, delete leftovers."""
    existing = list(manager.order_by("order", "id"))
    for position, row in enumerate(rows):
        fields = make(row) | {"order": position}
        if position < len(existing):
            obj = existing[position]
            for name, value in fields.items():
                setattr(obj, name, value)
        else:
            obj = manager.model(**{manager.field.name: manager.instance}, **fields)
        obj.full_clean()
        obj.save()
    for obj in existing[len(rows):]:
        obj.delete()


def _question(row):
    return {
        "text": row["text"].strip(),
        "choices": row["choices"].strip(),
        "explanation": (row.get("explanation") or "").strip(),
        "points": row.get("points", 1),
    }


def _card(row):
    return {"front": str(row["front"]).strip(), "back": str(row["back"]).strip()}


class Command(BaseCommand):
    help = "Create or update quizzes and flashcard decks from course_content/<course>/practice/*.yaml."

    def add_arguments(self, parser):
        parser.add_argument("slugs", nargs="+")
        parser.add_argument("--draft", action="store_true", help="Load unpublished (staff-only preview).")
        parser.add_argument(
            "--prune", action="store_true",
            help="Delete this course's quizzes and decks that are not in the files.",
        )

    def handle(self, *args, **options):
        for slug in options["slugs"]:
            try:
                course = Course.objects.get(slug=slug)
            except Course.DoesNotExist:
                raise CommandError(f"No course with slug {slug!r}.")
            folder = course.src_dir / "practice"
            files = sorted(folder.glob("*.yaml"))
            if not files:
                raise CommandError(f"No practice files in {folder}.")
            try:
                with transaction.atomic():
                    counts = self.load_course(course, files, options)
            except ValidationError as exc:
                raise CommandError(f"{slug}: {exc}")
            self.stdout.write(self.style.SUCCESS(
                f"{slug}: {counts['quizzes']} quizzes, {counts['questions']} questions, "
                f"{counts['decks']} decks, {counts['cards']} cards"
                + (f", pruned {counts['pruned']}" if options["prune"] else "")
            ))

    def load_course(self, course, files, options):
        published = not options["draft"]
        counts = dict(quizzes=0, questions=0, decks=0, cards=0, pruned=0)
        keep_quizzes, keep_decks = set(), set()
        for number, path in enumerate(files, start=1):
            try:
                data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
            except yaml.YAMLError as exc:
                raise CommandError(f"{path.name}: {exc}")
            try:
                chapter = clean_chapter(course, data.get("chapter", ""))
            except ValidationError as exc:
                raise CommandError(f"{path.name}: {exc}")
            for index, item in enumerate(data.get("quizzes") or []):
                quiz, _ = Quiz.objects.update_or_create(
                    course=course, chapter=chapter, title=item["title"],
                    defaults=dict(
                        description=(item.get("description") or "").strip(),
                        pass_percentage=item.get("pass_percentage", 60),
                        is_published=published, order=number * 10 + index,
                    ),
                )
                try:
                    _sync_children(quiz.questions, item["questions"], _question)
                except ValidationError as exc:
                    raise CommandError(f"{path.name} · {quiz.title}: {exc}")
                keep_quizzes.add(quiz.pk)
                counts["quizzes"] += 1
                counts["questions"] += len(item["questions"])
            for index, item in enumerate(data.get("decks") or []):
                deck, _ = Deck.objects.update_or_create(
                    course=course, chapter=chapter, title=item["title"],
                    defaults=dict(
                        description=(item.get("description") or "").strip(),
                        is_published=published, order=number * 10 + index,
                    ),
                )
                _sync_children(deck.cards, item["cards"], _card)
                keep_decks.add(deck.pk)
                counts["decks"] += 1
                counts["cards"] += len(item["cards"])
        if options["prune"]:
            counts["pruned"] += Quiz.objects.filter(course=course).exclude(pk__in=keep_quizzes).delete()[1].get("quizzes.Quiz", 0)
            counts["pruned"] += Deck.objects.filter(course=course).exclude(pk__in=keep_decks).delete()[1].get("quizzes.Deck", 0)
        return counts
