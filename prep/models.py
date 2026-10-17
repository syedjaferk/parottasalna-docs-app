"""Per-student progress on the interview-prep problem catalog (``prep/data/catalog.json``).

``ProblemProgress`` holds the current state of one problem for one student, including the spaced
re-solve schedule (see ``prep/scheduling.py``). ``Attempt`` is the history of every try, and
``PrepProfile`` stores the result of the placement quiz.
"""
from django.conf import settings
from django.db import models


class ProblemProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="prep_progress")
    problem_id = models.CharField(max_length=200, help_text="Catalog id, e.g. leetcode:two-sum")
    solved = models.BooleanField(default=False)
    bookmarked = models.BooleanField(default=False)
    note = models.TextField(blank=True, max_length=2000, help_text="Notes, ideally the key insight in a line or two.")
    solved_at = models.DateTimeField(null=True, blank=True)
    # Spaced repetition: 0 = not solved cold yet, 1..3 = waiting for the 1-day / 1-week / 3-4-week re-solve, 4 = mastered.
    stage = models.PositiveSmallIntegerField(default=0)
    next_review = models.DateField(null=True, blank=True, db_index=True)
    confidence = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-5, from the last attempt.")
    attempts = models.PositiveIntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "problem_id"], name="uniq_prep_progress")]
        indexes = [models.Index(fields=["user", "solved"]), models.Index(fields=["user", "next_review"])]

    def __str__(self):
        return f"{self.user_id} · {self.problem_id}"


class Attempt(models.Model):
    class Outcome(models.TextChoices):
        COLD = "cold", "Solved on my own"
        HINT = "hint", "Needed a hint"
        FAIL = "fail", "Could not solve"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="prep_attempts")
    problem_id = models.CharField(max_length=200)
    outcome = models.CharField(max_length=8, choices=Outcome.choices)
    confidence = models.PositiveSmallIntegerField(null=True, blank=True)
    minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    is_review = models.BooleanField(default=False, help_text="True when the problem had been solved before this attempt.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "created_at"])]

    def __str__(self):
        return f"{self.user_id} · {self.problem_id} · {self.outcome}"


class PrepProfile(models.Model):
    """Result of the placement quiz (one per student, replaced when it is retaken)."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="prep_profile")
    level = models.CharField(max_length=20, blank=True, help_text="beginner / intermediate / advanced")
    diagnostic = models.JSONField(default=dict, blank=True, help_text="Pattern name -> {asked, right}.")
    score = models.PositiveSmallIntegerField(default=0)
    total = models.PositiveSmallIntegerField(default=0)
    taken_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user_id} · {self.level or 'not taken'}"
