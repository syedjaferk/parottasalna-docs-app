"""A signed-in user's own page: optional details about them, plus their streak and activity.

Everything here is private: only the user and the portal admins see it. There are no public profiles.
"""
import secrets

from django.conf import settings
from django.db import models

INTERESTS = [
    ("backend", "Backend engineering"),
    ("system-design", "System design"),
    ("python", "Python"),
    ("databases", "Databases"),
    ("cloud", "AWS & cloud"),
    ("devops", "Docker, Kubernetes & DevOps"),
    ("data", "Data engineering"),
    ("ai", "AI engineering & agents"),
    ("dsa", "DSA & interviews"),
    ("frontend", "Frontend"),
    ("career", "Jobs & career"),
]


class Profile(models.Model):
    class Stage(models.TextChoices):
        STUDENT = "student", "Student"
        FRESHER = "fresher", "Looking for my first job"
        WORKING = "working", "Working professional"
        SWITCHING = "switching", "Switching careers"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    headline = models.CharField(max_length=120, blank=True, help_text="e.g. Final-year CSE student, Chennai")
    stage = models.CharField(max_length=12, choices=Stage.choices, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=80, blank=True)
    interests = models.JSONField(default=list, blank=True)
    github = models.URLField(max_length=200, blank=True)
    linkedin = models.URLField(max_length=200, blank=True)
    website = models.URLField(max_length=200, blank=True)
    # Secret part of the user's live-class calendar feed URL (it contains Meet links). Reset if it leaks.
    calendar_token = models.CharField(max_length=64, unique=True, null=True, blank=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user}"

    def ensure_calendar_token(self):
        if not self.calendar_token:
            self.reset_calendar_token()
        return self.calendar_token

    def reset_calendar_token(self):
        self.calendar_token = secrets.token_urlsafe(32)
        self.save(update_fields=["calendar_token", "updated_at"])
        return self.calendar_token

    def interest_labels(self):
        names = dict(INTERESTS)
        return [names[key] for key in self.interests if key in names]
