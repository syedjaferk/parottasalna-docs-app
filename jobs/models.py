"""Job board: signed-in users submit jobs, staff approve them, everyone can browse approved jobs."""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Job(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Waiting for review"
        APPROVED = "approved", "Live"
        REJECTED = "rejected", "Not approved"

    class JobType(models.TextChoices):
        FULL_TIME = "full_time", "Full-time"
        PART_TIME = "part_time", "Part-time"
        INTERNSHIP = "internship", "Internship"
        CONTRACT = "contract", "Contract"
        FREELANCE = "freelance", "Freelance"

    class WorkMode(models.TextChoices):
        ONSITE = "onsite", "On-site"
        REMOTE = "remote", "Remote"
        HYBRID = "hybrid", "Hybrid"

    title = models.CharField(max_length=120)
    company = models.CharField(max_length=120)
    location = models.CharField(max_length=120, help_text="City, or “Anywhere” for remote jobs.")
    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME)
    work_mode = models.CharField(max_length=10, choices=WorkMode.choices, default=WorkMode.ONSITE)
    experience = models.CharField(max_length=60, blank=True, help_text="e.g. “0–2 years” or “Freshers”.")
    salary = models.CharField(max_length=60, blank=True, help_text="Optional, e.g. “₹6–9 LPA”.")
    skills = models.CharField(max_length=200, blank=True, help_text="Comma separated, e.g. “Python, Django, SQL”.")
    description = models.TextField(max_length=5000)
    apply_url = models.URLField(max_length=500, blank=True, validators=[URLValidator(schemes=["http", "https"])])
    apply_email = models.EmailField(blank=True)
    last_date = models.DateField(null=True, blank=True, help_text="Last date to apply (optional).")

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True)
    review_note = models.CharField(max_length=300, blank=True, help_text="Shown to the poster if not approved.")
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="jobs")
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return f"{self.title} · {self.company}"

    def clean(self):
        if not (self.apply_url or self.apply_email):
            raise ValidationError("Add an application link or an email address, so people can apply.")
        if self.last_date and self.last_date < timezone.localdate() and self.status != self.Status.REJECTED:
            raise ValidationError({"last_date": "The last date to apply is already in the past."})

    def get_absolute_url(self):
        return reverse("job_detail", args=[self.pk, slugify(f"{self.title} {self.company}")[:60] or "job"])

    def skill_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    @property
    def is_expired(self):
        return bool(self.last_date and self.last_date < timezone.localdate())

    def approve(self, reviewer):
        self.status = self.Status.APPROVED
        self.reviewed_by = reviewer
        self.review_note = ""
        if not self.published_at:
            self.published_at = timezone.now()

    @classmethod
    def visible(cls):
        """Approved jobs whose last date hasn't passed: what the public sees."""
        today = timezone.localdate()
        return cls.objects.filter(status=cls.Status.APPROVED).filter(Q(last_date__isnull=True) | Q(last_date__gte=today))
