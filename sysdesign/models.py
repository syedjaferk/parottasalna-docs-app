"""System design playground content (``Problem``) and each signed-in learner's progress through it.

``sysdesign/data/*.json`` are the seed files; ``manage.py load_sysdesign`` copies them into ``Problem`` rows.
"""
from django.conf import settings
from django.db import models


class Problem(models.Model):
    slug = models.SlugField(max_length=80, unique=True)
    title = models.CharField(max_length=200)
    tagline = models.CharField(max_length=300, blank=True)
    difficulty = models.CharField(max_length=30, default="Beginner")
    minutes = models.PositiveSmallIntegerField(default=45)
    course_slug = models.SlugField(max_length=80, blank=True, default="system-design", help_text="Course linked from the problem page.")
    is_pro = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0, help_text="Lower numbers are listed first.")
    statement = models.JSONField(default=dict, blank=True, help_text="Left pane: prompt, context, given, expectations, scope, timeline, great.")
    steps = models.JSONField(default=list, blank=True, help_text="Right pane: the guided steps, in order.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "slug"]

    def __str__(self):
        return self.title

    def as_dict(self):
        """The shape the templates and ``sysdesign.js`` expect (the same as the seed JSON files)."""
        return {"slug": self.slug, "title": self.title, "tagline": self.tagline, "difficulty": self.difficulty,
                "minutes": self.minutes, "course_slug": self.course_slug, "is_pro": self.is_pro,
                "statement": self.statement, "steps": self.steps}


class ProblemProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sysdesign_progress")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="progress")
    answers = models.JSONField(default=dict, blank=True, help_text="Step id -> the learner's recorded answer and verdict.")
    current_step = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "problem"], name="uniq_sysdesign_progress")]
        verbose_name_plural = "problem progress"

    def __str__(self):
        return f"{self.user_id} · {self.problem.slug}"
