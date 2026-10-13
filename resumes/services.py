"""Submitting, claiming, finishing and deleting resume reviews."""
import logging
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import F, Q
from django.db.models.functions import Coalesce
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from . import drive, mailer
from .models import ResumeReview, new_tracking_id
from .results import FAILURE_REASONS, clean_result

log = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
DAILY_LIMIT = 3            # uploads per user per 24 hours (staff are not limited)
CLAIM_TIMEOUT = timedelta(minutes=30)   # a claimed job not finished by then goes back to the queue
MAX_ATTEMPTS = 3
MAX_MAIL_ATTEMPTS = 6      # then it shows on the admin panel instead of being retried

Status = ResumeReview.Status


def can_view(user, review):
    return user.is_authenticated and (user.is_staff or review.user_id == user.pk)


def over_daily_limit(user):
    if user.is_staff:
        return False
    since = timezone.now() - timedelta(hours=24)
    return ResumeReview.objects.filter(user=user, created_at__gte=since).count() >= DAILY_LIMIT


def submit(user, upload, target_role=""):
    """Upload the PDF to Drive, then record the review. Raises drive.DriveError if Drive fails."""
    tracking_id = new_tracking_id()
    while ResumeReview.objects.filter(tracking_id=tracking_id).exists():
        tracking_id = new_tracking_id()
    upload.seek(0)
    # The Drive name carries no personal data: the worker maps it back through the API.
    file_id = drive.upload_pdf(upload.read(), f"{tracking_id}.pdf", tracking_id)
    try:
        return ResumeReview.objects.create(
            tracking_id=tracking_id, user=user, email=user.email, file_name=upload.name[:200],
            target_role=target_role, drive_file_id=file_id, consented_at=timezone.now(),
        )
    except Exception:
        delete_quietly(file_id)
        raise


# ---------------------------------------------------------------- worker side

def claim_next():
    """Hand the oldest waiting review to the worker, or None. Safe with several workers polling at once."""
    now = timezone.now()
    stale = Q(status=Status.PROCESSING, claimed_at__lt=now - CLAIM_TIMEOUT)
    # Jobs that keep timing out (the worker crashes on them) stop being retried.
    for review in ResumeReview.objects.filter(stale, attempts__gte=MAX_ATTEMPTS):
        _finish_failed(review, "error")
    candidates = ResumeReview.objects.filter(Q(status=Status.QUEUED) | stale).exclude(drive_file_id="")
    for review in candidates.order_by("created_at")[:5]:
        # Conditional update: only one poller can move a row out of the state it saw.
        won = ResumeReview.objects.filter(pk=review.pk, status=review.status, claimed_at=review.claimed_at).update(
            status=Status.PROCESSING, claimed_at=now, attempts=F("attempts") + 1)
        if won:
            review.refresh_from_db()
            return review
    return None


def complete(review, raw_result):
    """Store a finished review. Raises results.ResultError if the output can't be used."""
    result, flags = clean_result(raw_result)
    review.result = result
    review.ats_score = result["ats_score"]
    review.flags = flags
    review.status = Status.HELD if flags else Status.DONE
    review.status_note = ""
    review.completed_at = timezone.now()
    review.save()
    if flags:
        log.warning("Resume review %s held for checking: %s", review.tracking_id, "; ".join(flags))
    else:
        send_email(review)
    return review


def fail(review, reason):
    """The worker gave up. The user only ever sees one of our fixed messages, never worker text."""
    _finish_failed(review, reason if reason in FAILURE_REASONS else "error")


def _finish_failed(review, reason):
    review.status = Status.FAILED
    review.status_note = FAILURE_REASONS[reason]
    review.completed_at = timezone.now()
    review.save(update_fields=["status", "status_note", "completed_at"])
    send_email(review)


# ---------------------------------------------------------------- staff + cleanup

def release(review):
    """A person checked a held review and it's fine: show it to the user."""
    review.status = Status.DONE
    review.save(update_fields=["status"])
    send_email(review)


def requeue(review):
    if not review.drive_file_id:
        return False
    review.status, review.status_note, review.attempts, review.claimed_at = Status.QUEUED, "", 0, None
    review.save(update_fields=["status", "status_note", "attempts", "claimed_at"])
    return True


def delete_file(review):
    """Delete the PDF from Drive (raises drive.DriveError) and remember that it's gone."""
    if review.drive_file_id:
        drive.delete_file(review.drive_file_id)
    review.drive_file_id = ""
    review.file_deleted_at = review.file_deleted_at or timezone.now()
    review.save(update_fields=["drive_file_id", "file_deleted_at"])


@transaction.atomic
def delete_review(review):
    """The user deletes their review: the PDF first (so it's never orphaned on Drive), then the record."""
    delete_file(review)
    review.delete()


def expired_files(days=None):
    """Finished reviews whose PDF has been kept long enough: counted from the email, or from the end of the
    review if the email never went out (so a broken mailer can't keep PDFs forever)."""
    days = settings.RESUME_RETENTION_DAYS if days is None else days
    cutoff = timezone.now() - timedelta(days=days)
    return (ResumeReview.objects.filter(status__in=[Status.DONE, Status.FAILED]).exclude(drive_file_id="")
            .annotate(kept_since=Coalesce("mailed_at", "completed_at")).filter(kept_since__lt=cutoff))


# ---------------------------------------------------------------- email

def send_email(review):
    """Email the report (done) or the failure notice (failed). Returns True if sent. Never raises: a review
    that couldn't be emailed is retried by  manage.py send_resume_emails."""
    if review.status not in (Status.DONE, Status.FAILED) or review.mailed_at or not mailer.is_configured():
        return False
    kind = "report" if review.status == Status.DONE else "failed"
    ctx = {
        "review": review, "report": review.report,
        "name": review.user.first_name or "there",
        "url": settings.SITE_URL + review.get_absolute_url(),
        "upload_url": settings.SITE_URL + reverse("resume_upload"),
        "privacy_url": settings.SITE_URL + reverse("privacy"),
        "retention_days": settings.RESUME_RETENTION_DAYS,
    }
    if kind == "report":
        subject = f"Your resume review is ready: ATS score {review.ats_score}/100 ({review.tracking_id})"
    else:
        subject = f"We couldn't review your resume ({review.tracking_id})"
    ResumeReview.objects.filter(pk=review.pk).update(mail_attempts=F("mail_attempts") + 1)
    try:
        mailer.send(review.email, subject, render_to_string(f"resumes/email/{kind}.html", ctx),
                    render_to_string(f"resumes/email/{kind}.txt", ctx))
    except mailer.MailerError as e:
        log.error("Emailing resume review %s failed: %s", review.tracking_id, e)
        return False
    review.mailed_at = timezone.now()
    review.save(update_fields=["mailed_at"])
    return True


def unsent_emails():
    return ResumeReview.objects.filter(status__in=[Status.DONE, Status.FAILED], mailed_at__isnull=True)


def delete_quietly(file_id):
    try:
        drive.delete_file(file_id)
    except drive.DriveError:
        log.exception("Could not delete Drive file %s; delete it by hand.", file_id)
