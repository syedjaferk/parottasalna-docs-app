"""Per-student progress on the interview-prep problem catalog (``prep/data/catalog.json``)."""
from django.conf import settings
from django.db import models


class ProblemProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="prep_progress")
    problem_id = models.CharField(max_length=200, help_text="Catalog id, e.g. leetcode:two-sum")
    solved = models.BooleanField(default=False)
    bookmarked = models.BooleanField(default=False)
    note = models.TextField(blank=True, max_length=2000)
    solved_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "problem_id"], name="uniq_prep_progress")]
        indexes = [models.Index(fields=["user", "solved"])]

    def __str__(self):
        return f"{self.user_id} · {self.problem_id}"
