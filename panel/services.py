"""What's waiting for an admin. Database checks only here; Calendly lives in calendly.py."""
from courses.models import Course
from jobs.models import Job


def pending_jobs():
    return Job.objects.filter(status=Job.Status.PENDING).select_related("posted_by").order_by("created_at")


def failed_builds():
    return Course.objects.filter(is_active=True, build_status=Course.BuildStatus.FAILED).order_by("title")


def attention_count():
    """For the header badge: cheap COUNT queries only (no Calendly call on every page)."""
    return pending_jobs().count() + failed_builds().count()
