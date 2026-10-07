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
