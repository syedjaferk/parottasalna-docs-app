"""What's waiting for an admin. Database checks only here; Calendly lives in calendly.py."""
from datetime import timedelta

from django.utils import timezone

from courses.models import Course
from jobs.models import Job
from resumes import mailer
from resumes import services as resume_services
from resumes.models import ResumeReview


def pending_jobs():
    return Job.objects.filter(status=Job.Status.PENDING).select_related("posted_by").order_by("created_at")


def failed_builds():
    return Course.objects.filter(is_active=True, build_status=Course.BuildStatus.FAILED).order_by("title")


def held_resume_reviews():
    """Reviews the guardrails held back (resumes/results.py) until a person checks them."""
    return ResumeReview.objects.filter(status=ResumeReview.Status.HELD).order_by("completed_at")


def unsent_resume_emails():
    """Finished reviews whose email still hasn't gone out after an hour: the mailer needs a look."""
    if not mailer.is_configured():
        return ResumeReview.objects.none()
    return resume_services.unsent_emails().filter(completed_at__lt=timezone.now() - timedelta(hours=1))


def attention_count():
    """For the header badge: cheap COUNT queries only (no Calendly call on every page)."""
    return (pending_jobs().count() + failed_builds().count() + held_resume_reviews().count()
            + unsent_resume_emails().count())
