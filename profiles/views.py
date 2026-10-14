from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from courses.security import no_store
from courses.services import accessible_courses, can_track
from jobs.models import Job
from live import calendar
from notes.models import Note
from resumes.models import ResumeReview
from streaks.services import has_streak, summary as streak_summary

from .forms import ProfileForm
from .models import Profile


@login_required
@require_http_methods(["GET", "POST"])
def profile(request):
    """The user's own page: their details (editable), reading streak and everything they've made here."""
    prof, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=prof)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile saved.")
        return redirect("profile")

    user = request.user
    note_courses = [c for c in accessible_courses(user) if can_track(user, c)]
    note_counts = {c.pk: 0 for c in note_courses}
    for course_id in Note.objects.filter(user=user, course__in=note_courses).values_list("course_id", flat=True):
        note_counts[course_id] += 1
    return no_store(render(request, "profiles/profile.html", {
        "form": form,
        "profile": prof,
        "streak": streak_summary(user) if has_streak(user) else None,
        "resume_count": ResumeReview.objects.filter(user=user).count(),
        "job_count": Job.objects.filter(posted_by=user).count(),
        "note_courses": [(c, note_counts[c.pk]) for c in note_courses if note_counts[c.pk]],
        "contact_email": settings.CONTACT_EMAIL,
        "cal": calendar.feed_links(request, prof.ensure_calendar_token()),
        "reminder": {
            "at": calendar.DEFAULT_AT.strftime("%H:%M"),
            "minutes": calendar.DEFAULT_MINUTES,
            "choices": calendar.REMINDER_MINUTES,
            "google": calendar.google_daily_link(calendar.DEFAULT_AT, calendar.DEFAULT_MINUTES,
                                                 request.build_absolute_uri("/").rstrip("/")),
        },
    }))
