"""Who may do what with a job post."""
from datetime import timedelta

from django.utils import timezone

from .models import Job

DAILY_POST_LIMIT = 5      # submissions per user per 24 hours (staff are not limited)


def can_manage(user, job):
    """The poster and staff can edit or delete a job."""
    return user.is_authenticated and (user.is_staff or job.posted_by_id == user.pk)


def can_view(user, job):
    """Approved jobs are public (even after the last date, shown as closed). Others: poster and staff only."""
    return job.status == Job.Status.APPROVED or can_manage(user, job)


def over_daily_limit(user):
    if user.is_staff:
        return False
    since = timezone.now() - timedelta(hours=24)
    return Job.objects.filter(posted_by=user, created_at__gte=since).count() >= DAILY_POST_LIMIT


def submit(job, user):
    """Save a new or edited job. Staff posts go live at once; everyone else's wait for review."""
    if user.is_staff:
        job.approve(user)
    else:
        job.status = Job.Status.PENDING      # edits by the poster are reviewed again
        job.review_note = ""
    job.save()
    return job


def reject(job, reviewer, note=""):
    job.status = Job.Status.REJECTED
    job.reviewed_by = reviewer
    job.review_note = note[:300]
    job.save(update_fields=["status", "reviewed_by", "review_note", "updated_at"])
