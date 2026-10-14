"""Daily code-smell tip + one practice question, shown on the dashboard.

The content lives in ``smells/data/code_smells.json`` (``load_smells`` / ``dump_smells``)."""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class CodeSmell(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    slug = models.SlugField(unique=True)
    number = models.PositiveIntegerField(null=True, blank=True, help_text="Number in Maximiliano Contieri's series, if known.")
    title = models.CharField(max_length=200)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
    tags = models.JSONField(default=list, blank=True, help_text="List of short tag strings.")
    summary = models.CharField(max_length=300, help_text="One-line TL;DR.")
    problem = models.TextField()
    why_bad = models.JSONField(default=list, blank=True, help_text="List of bullet strings.")
    bad_code = models.TextField(blank=True)
    good_code = models.TextField(blank=True)
    language = models.CharField(max_length=20, default="python")
    fix = models.JSONField(default=list, blank=True, help_text="List of fix-step strings.")
    source_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Position in the daily rotation (lower first).")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.number or '–'} · {self.title}"


class SmellQuiz(models.Model):
    smell = models.OneToOneField(CodeSmell, on_delete=models.CASCADE, related_name="quiz")
    question = models.TextField(help_text="Markdown-free; a short code block may follow a blank line.")
    choices = models.JSONField(default=list, help_text="List of 2–5 answer strings.")
    answer = models.PositiveSmallIntegerField(help_text="Index (from 0) of the correct choice.")
    explanation = models.TextField(blank=True)

    def clean(self):
        if not isinstance(self.choices, list) or not 2 <= len(self.choices) <= 5:
            raise ValidationError({"choices": "Give 2–5 choices as a list."})
        if not 0 <= (self.answer or 0) < len(self.choices):
            raise ValidationError({"answer": "Answer must be the index of one of the choices."})

    def __str__(self):
        return self.question[:80]


class SmellAnswer(models.Model):
    """A student's first answer to a smell's quiz (later tries are not recorded)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="smell_answers")
    smell = models.ForeignKey(CodeSmell, on_delete=models.CASCADE, related_name="answers")
    choice = models.PositiveSmallIntegerField()
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "smell"], name="uniq_smell_answer")]
