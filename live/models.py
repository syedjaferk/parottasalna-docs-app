from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from courses.models import Course

JOIN_EARLY_MINUTES = 15  # the Join button turns on this long before the start


def validate_meeting_url(value):
    if not value.startswith("https://"):
        raise ValidationError("Use the full https:// link, e.g. https://meet.google.com/abc-defg-hij")


class LiveSession(models.Model):
    """One live class. The Meet link is only shown to signed-in users who can open the course."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="live_sessions")
    title = models.CharField(max_length=200, help_text="e.g. “Session 12 · Kubernetes Services”.")
    starts_at = models.DateTimeField(help_text="In India time (IST).")
    ends_at = models.DateTimeField()
    meet_url = models.URLField("Google Meet link", max_length=300, validators=[validate_meeting_url])
    description = models.CharField(max_length=300, blank=True, help_text="Optional one-line agenda.")
    is_cancelled = models.BooleanField("cancelled", default=False,
                                       help_text="Keeps the session on the list, marked as cancelled.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["starts_at", "course__title"]
        indexes = [models.Index(fields=["starts_at"])]
        constraints = [models.UniqueConstraint(fields=["course", "starts_at"], name="uniq_course_session_start")]

    def __str__(self):
        return f"{self.course.title} · {self.title} · {timezone.localtime(self.starts_at):%d %b %Y %I:%M %p}"

    def clean(self):
        super().clean()
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "The session must end after it starts."})

    def status(self, now=None):
        """"cancelled", "upcoming", "soon" (join window open), "live" or "ended"."""
        now = now or timezone.now()
        if self.is_cancelled:
            return "cancelled"
        if now >= self.ends_at:
            return "ended"
        if now >= self.starts_at:
            return "live"
        if (self.starts_at - now).total_seconds() <= JOIN_EARLY_MINUTES * 60:
            return "soon"
        return "upcoming"
