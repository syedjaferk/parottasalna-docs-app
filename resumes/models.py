"""Resume ATS review: a signed-in user uploads a PDF, which goes straight to Google Drive (never to this
server's disk), and gets a tracking ID. A worker on our own machine claims it through the API, reviews
it with a local model and reports the result back; the PDF is deleted from Drive a few days later."""
import re
import secrets

from django.conf import settings
from django.db import models
from django.urls import reverse

# No 0/O or 1/I, so an ID read out over the phone or typed from a screenshot can't be misread.
ID_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


def new_tracking_id():
    raw = "".join(secrets.choice(ID_ALPHABET) for _ in range(8))
    return f"ATS-{raw[:4]}-{raw[4:]}"


def normalise_tracking_id(text):
    """'ats 7k3q 9xmp', 'ATS7K3Q9XMP' and 'ATS-7K3Q-9XMP' all mean the same ID. Returns '' if it can't be one."""
    raw = re.sub(r"[\s-]", "", (text or "").upper())
    raw = raw.removeprefix("ATS")
    if len(raw) != 8 or any(c not in ID_ALPHABET for c in raw):
        return ""
    return f"ATS-{raw[:4]}-{raw[4:]}"


class ResumeReview(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "In the queue"
        PROCESSING = "processing", "Being reviewed"
        HELD = "held", "Being checked by our team"
        DONE = "done", "Ready"
        FAILED = "failed", "Could not be reviewed"

    tracking_id = models.CharField(max_length=14, unique=True, default=new_tracking_id, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resume_reviews")
    email = models.EmailField(help_text="Where the report is sent: the user's verified sign-in email.")
    file_name = models.CharField(max_length=200, help_text="Name of the uploaded file, shown back to the user.")
    target_role = models.CharField(max_length=80, blank=True)
    drive_file_id = models.CharField(max_length=100, blank=True, help_text="Empty once the PDF is deleted.")

    status = models.CharField(max_length=12, choices=Status.choices, default=Status.QUEUED, db_index=True)
    status_note = models.CharField(max_length=300, blank=True, help_text="Shown to the user.")
    result = models.JSONField(null=True, blank=True, help_text="The review, after the checks in results.py.")
    ats_score = models.PositiveSmallIntegerField(null=True, blank=True)
    flags = models.JSONField(default=list, blank=True, help_text="Why the review was held. Staff only.")
    attempts = models.PositiveSmallIntegerField(default=0)

    consented_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    claimed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    file_deleted_at = models.DateTimeField(null=True, blank=True)
    mailed_at = models.DateTimeField(null=True, blank=True, help_text="When the report (or failure notice) was emailed.")
    mail_attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tracking_id} · {self.email}"

    def get_absolute_url(self):
        return reverse("resume_status", args=[self.tracking_id])

    @property
    def is_open(self):
        return self.status in {self.Status.QUEUED, self.Status.PROCESSING}

    @property
    def report(self):
        """The result, but only once it may be shown to the user."""
        return self.result if self.status == self.Status.DONE else None
