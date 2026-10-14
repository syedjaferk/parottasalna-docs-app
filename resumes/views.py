import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadhandler import MemoryFileUploadHandler
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_http_methods, require_POST, require_safe

from courses.security import no_store

from . import drive, mailer, services
from .forms import ResumeForm
from .models import ResumeReview, normalise_tracking_id

log = logging.getLogger(__name__)


class InMemoryUploadHandler(MemoryFileUploadHandler):
    """Keep the upload in memory whatever its size (the view caps it first), so a resume is never
    written to a temporary file on this server on its way to Drive."""

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self.activated = True


@login_required
@require_http_methods(["GET", "POST"])
@csrf_exempt   # CSRF is checked in _upload, after the upload handler is swapped (Django needs that order)
def upload(request):
    if request.method == "POST":
        try:
            too_big = int(request.META.get("CONTENT_LENGTH") or 0) > services.MAX_UPLOAD_BYTES + 64 * 1024
        except ValueError:
            too_big = True
        if too_big:     # refuse before reading the body
            messages.error(request, "That file is larger than 5 MB. Please upload a smaller PDF.")
            return redirect("resume_upload")
        request.upload_handlers = [InMemoryUploadHandler(request)]
    return _upload(request)


@csrf_protect
def _upload(request):
    available = drive.is_configured()
    emails_on = mailer.is_configured()
    form = ResumeForm(request.POST or None, request.FILES or None, emails_on=emails_on)
    if request.method == "POST" and available:
        if services.over_daily_limit(request.user):
            messages.error(request, f"You can upload up to {services.DAILY_LIMIT} resumes a day. Please try again tomorrow.")
            return redirect("resume_mine")
        if form.is_valid():
            try:
                review = services.submit(request.user, form.cleaned_data["resume"], form.cleaned_data["target_role"])
            except drive.DriveError:
                log.exception("Resume upload to Drive failed")
                messages.error(request, "We couldn't upload your resume just now. Please try again in a few minutes.")
            else:
                messages.success(request, f"Uploaded! Your tracking ID is {review.tracking_id}. " + (
                    f"We'll email the report to {review.email}." if emails_on
                    else "Your report will appear on this page; check back in a little while."))
                return redirect(review)
    recent = ResumeReview.objects.filter(user=request.user)[:3]
    return render(request, "resumes/upload.html", {
        "form": form, "available": available, "recent": recent, "emails_on": emails_on,
        "daily_limit": services.DAILY_LIMIT,
    })


@login_required
@require_safe
def mine(request):
    """The user's reviews, plus a box to jump to one by tracking ID."""
    query = request.GET.get("id", "").strip()
    if query:
        tracking_id = normalise_tracking_id(query)
        if tracking_id:
            return redirect("resume_status", tracking_id)
        messages.error(request, "That doesn't look like a tracking ID. It looks like ATS-7K3Q-9XMP.")
    reviews = ResumeReview.objects.filter(user=request.user)
    return render(request, "resumes/mine.html", {"reviews": reviews, "query": query})


@login_required
@require_safe
def status(request, tracking_id):
    review = get_object_or_404(ResumeReview, tracking_id=normalise_tracking_id(tracking_id) or tracking_id)
    if not services.can_view(request.user, review):
        raise Http404      # someone else's ID looks the same as a wrong one
    if review.tracking_id != tracking_id:
        return redirect(review)
    return no_store(render(request, "resumes/status.html", {
        "review": review, "report": review.report,
        "retention_days": settings.RESUME_RETENTION_DAYS, "emails_on": mailer.is_configured(),
    }))


@login_required
@require_POST
def delete(request, tracking_id):
    review = get_object_or_404(ResumeReview, tracking_id=tracking_id)
    if not services.can_view(request.user, review):
        raise Http404
    if review.status == ResumeReview.Status.PROCESSING:
        messages.error(request, "This resume is being reviewed right now. You can delete it once that's done.")
        return redirect(review)
    try:
        services.delete_review(review)
    except drive.DriveError:
        log.exception("Deleting resume %s from Drive failed", tracking_id)
        messages.error(request, "We couldn't delete the file just now. Please try again in a few minutes.")
        return redirect(review)
    messages.success(request, f"Deleted {tracking_id}: the PDF and its report are gone.")
    return redirect("resume_mine")
