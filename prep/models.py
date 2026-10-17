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


# ---- interview-prep content (seeded from prep/data/*.json with ``manage.py seed_prep``) ----------------
class CatalogLookup(models.Model):
    """One of the shared lists the catalog refers to by position: topics, patterns, companies, difficulties.

    ``CatalogProblem.patterns`` / ``companies`` and the sheet items hold indexes into these lists, so only
    append to them; reordering or removing an entry shifts every problem that points at it.
    """

    name = models.CharField(max_length=20, unique=True, help_text="topics, patterns, companies or difficulties")
    values = models.JSONField(default=list)

    def __str__(self):
        return f"{self.name} ({len(self.values)})"


class CatalogProblem(models.Model):
    position = models.PositiveIntegerField(db_index=True, help_text="Order in the catalog. Sheets point at problems by this position.")
    pid = models.CharField("id", max_length=200, unique=True, help_text="e.g. leetcode:two-sum")
    title = models.CharField(max_length=200)
    platform = models.CharField(max_length=40)
    url = models.URLField(max_length=400, blank=True)
    difficulty = models.PositiveSmallIntegerField(default=0, help_text="Index into the difficulties lookup.")
    tags = models.JSONField(default=list, blank=True, help_text="Topic tags (names).")
    patterns = models.JSONField(default=list, blank=True, help_text="Indexes into the patterns lookup.")
    companies = models.JSONField(default=list, blank=True, help_text="[company index, how often] pairs.")

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.pid


class CatalogSheet(models.Model):
    position = models.PositiveIntegerField(db_index=True)
    sheet_id = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    by = models.CharField(max_length=200, blank=True)
    kind = models.CharField(max_length=40, blank=True)
    items = models.JSONField(default=list, blank=True, help_text="[problem position, section, subsection] rows.")

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.name


class PatternGuide(models.Model):
    position = models.PositiveIntegerField(db_index=True)
    pattern = models.CharField(max_length=100, unique=True)
    kid = models.TextField(blank=True, help_text="The explain-it-like-I'm-ten story.")
    when = models.JSONField(default=list, blank=True, help_text="Signals that the pattern applies (a list of strings).")
    time = models.CharField(max_length=100, blank=True)
    space = models.CharField(max_length=100, blank=True)
    session = models.CharField(max_length=100, blank=True, help_text="Course session slug, e.g. 01-two-pointers")

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.pattern


class PlacementQuestion(models.Model):
    position = models.PositiveIntegerField(db_index=True)
    qid = models.CharField(max_length=20, unique=True)
    pattern = models.CharField(max_length=100)
    q = models.TextField("question")
    options = models.JSONField(default=list)
    answer = models.PositiveSmallIntegerField(help_text="Index of the correct option.")
    why = models.TextField(blank=True)
    session = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.qid} · {self.pattern}"
