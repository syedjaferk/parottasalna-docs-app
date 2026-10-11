from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_safe

from courses.security import no_store

from . import calendly, services


@staff_member_required
@require_safe
def home(request):
    """One page for admins: everything that's waiting on someone."""
    calls, calls_error = calendly.upcoming_calls(refresh=request.GET.get("refresh") == "calls")
    jobs = list(services.pending_jobs()[:20])
    builds = list(services.failed_builds())
    today = timezone.localdate()
    calls_today = [c for c in calls or [] if c["start"] and timezone.localtime(c["start"]).date() == today]
    return no_store(render(request, "panel/home.html", {
        "jobs": jobs, "jobs_total": services.pending_jobs().count(),
        "builds": builds,
        "calls": calls, "calls_error": calls_error, "calls_today": len(calls_today),
        "all_clear": not jobs and not builds and not calls,
    }))
