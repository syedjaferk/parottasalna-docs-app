from django.conf import settings
from django.db import models

GOAL_SECONDS = 60  # active reading that counts a day, unless the student already did an action


class ReadingDay(models.Model):
    """One row per student per local (IST) day they read or did something in an enrolled course."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reading_days")
    date = models.DateField()
    seconds_read = models.PositiveIntegerField(default=0, help_text="Active reading time (tab visible, recent input).")
    actions = models.PositiveIntegerField(default=0, help_text="Chapters completed, quizzes, flashcards, notes.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user", "date"]
        constraints = [models.UniqueConstraint(fields=["user", "date"], name="uniq_reading_day")]

    def __str__(self):
        return f"{self.user} · {self.date} · {self.seconds_read}s, {self.actions} actions"

    @property
    def counts(self):
        return self.seconds_read >= GOAL_SECONDS or self.actions > 0
