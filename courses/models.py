from pathlib import Path

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation, ValidationError
from django.db import models
from django.utils._os import safe_join


class Course(models.Model):
    class BuildStatus(models.TextChoices):
        NEVER = "never", "Never built"
        BUILDING = "building", "Building"
        OK = "ok", "OK"
        FAILED = "failed", "Failed"

    slug = models.SlugField(max_length=64, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    source_dir = models.CharField(
        max_length=255,
        blank=True,
        help_text="Folder with the markdown files, relative to the course content root. "
        "Defaults to the slug.",
    )
    is_active = models.BooleanField(default=True)
    class Access(models.TextChoices):
        FREE = "free", "Free: anyone can enrol"
        PRO = "pro", "Pro: needs a Pro membership"
        INVITE = "invite", "Invite only: cohort or admin adds students"

    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    access = models.CharField(
        max_length=10, choices=Access.choices, default=Access.FREE,
        help_text="Who may enrol from the course catalogue. Admins can always add students by email.",
    )
    level = models.CharField(max_length=14, choices=Level.choices, blank=True)
    est_hours = models.PositiveSmallIntegerField("Estimated hours", null=True, blank=True)
    audience = models.TextField(blank=True, help_text="Who this course is for, one or two sentences.")
    outcomes = models.TextField(blank=True, help_text="What the student can do afterwards, one per line.")
    is_listed = models.BooleanField(
        "Listed in catalogue", default=True, help_text="Untick to hide it from the catalogue (it stays reachable for enrolled students).")
    sort_order = models.PositiveSmallIntegerField(default=100, help_text="Lower numbers come first in the catalogue.")
    is_common = models.BooleanField(
        "Common course",
        default=False,
        help_text="Public: anyone can read it without signing in or enrolling. Progress tracking and "
        "quizzes are only for students you enrol below. Leave unticked for enrolled-only courses.",
    )

    build_status = models.CharField(
        max_length=10, choices=BuildStatus.choices, default=BuildStatus.NEVER
    )
    last_built_at = models.DateTimeField(null=True, blank=True)
    build_log = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    @property
    def src_dir(self) -> Path:
        return Path(safe_join(settings.COURSES_SRC_ROOT, self.source_dir or self.slug))

    @property
    def html_dir(self) -> Path:
        return Path(settings.DOCS_BUILD_ROOT) / self.slug / "html"

    def clean(self):
        super().clean()
        try:
            safe_join(settings.COURSES_SRC_ROOT, self.source_dir or self.slug)
        except SuspiciousFileOperation:
            raise ValidationError(
                {"source_dir": "Must be a folder inside the course content root."}
            )


class Enrollment(models.Model):
    """An allow-list entry: this email may read this course's docs.

    Keyed by email so admins can enrol people before they ever sign in.
    `user` is filled in automatically on their first login.
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    email = models.EmailField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="enrollments",
    )
    class Source(models.TextChoices):
        ADMIN = "admin", "Added by an admin"
        SELF = "self", "Enrolled themselves"
        PRO = "pro", "Pro membership"
        COHORT = "cohort", "Cohort"

    source = models.CharField(max_length=8, choices=Source.choices, default=Source.ADMIN)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["course", "email"], name="uniq_course_email")
        ]
        ordering = ["email"]

    def save(self, *args, **kwargs):
        self.email = (self.email or "").strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} -> {self.course.slug}"


class PageProgress(models.Model):
    """A docs page a student has marked as complete."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="page_progress"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="page_progress")
    page = models.CharField(max_length=255, help_text="Sphinx page name, e.g. filtering-data/where")
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "course", "page"], name="uniq_user_course_page")
        ]
        ordering = ["course", "page"]
        verbose_name_plural = "page progress"

    def __str__(self):
        return f"{self.user} · {self.course.slug}/{self.page}"


class PageVisit(models.Model):
    """A signed-in user opened a chapter. Together with PageProgress this shows where learners drop off."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="page_visits")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="page_visits")
    page = models.CharField(max_length=255)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "course", "page"], name="uniq_visit_user_course_page")]
        indexes = [models.Index(fields=["course", "page"])]

    def __str__(self):
        return f"{self.user} · {self.course.slug}/{self.page}"


class LearningPath(models.Model):
    """A recommended route through courses and tools toward a goal. A few flagship paths are the front door."""

    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=120)
    tagline = models.CharField(max_length=200)
    audience = models.CharField(max_length=240, blank=True, help_text="Who it is for.")
    outcome = models.CharField(max_length=240, blank=True, help_text="What you can do at the end.")
    icon = models.CharField(max_length=8, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=100)

    class Meta:
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title


class PathStep(models.Model):
    class Kind(models.TextChoices):
        COURSE = "course", "Course"
        LINK = "link", "Tool or page"

    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name="steps")
    order = models.PositiveSmallIntegerField(default=1)
    kind = models.CharField(max_length=8, choices=Kind.choices, default=Kind.COURSE)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.CASCADE, related_name="path_steps")
    title = models.CharField(max_length=120, blank=True, help_text="Required for tools; defaults to the course title.")
    url = models.CharField(max_length=200, blank=True, help_text="Site path such as /resume-review/ (tools only).")
    note = models.CharField(max_length=240, blank=True, help_text="Why this step, in one line.")

    class Meta:
        ordering = ["path", "order"]

    def __str__(self):
        return f"{self.path.slug} #{self.order}"

    @property
    def label(self):
        return self.title or (self.course.title if self.course else "")
