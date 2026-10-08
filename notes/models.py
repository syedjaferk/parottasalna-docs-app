from django.conf import settings
from django.db import models

from courses.models import Course

QUOTE_MAX = 1000
BODY_MAX = 10000
NOTES_PER_COURSE_MAX = 2000  # per student; stops a runaway script filling the database


class Note(models.Model):
    """A student's private note on a docs page, optionally tied to a section and a quoted passage.

    Only the student who wrote a note can see it in the app (it is deliberately not in the admin).
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="notes")
    page = models.CharField(max_length=255, help_text="Sphinx page name, e.g. sessions/03-namespaces")
    anchor = models.CharField(max_length=200, blank=True, help_text="Section id on the page, if any.")
    quote = models.TextField(blank=True, max_length=QUOTE_MAX, help_text="Text the student selected.")
    body = models.TextField(max_length=BODY_MAX)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [models.Index(fields=["user", "course", "page"])]

    def __str__(self):
        return f"{self.user} · {self.course.slug}/{self.page}"

    def as_json(self):
        return {
            "id": self.pk,
            "page": self.page,
            "anchor": self.anchor,
            "quote": self.quote,
            "body": self.body,
            "created": self.created_at.isoformat(),
            "updated": self.updated_at.isoformat(),
        }
