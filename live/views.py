from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST, require_safe

from profiles.models import Profile

from . import calendar


def _site(request):
    return request.build_absolute_uri("/").rstrip("/")


def _ics(body, filename, inline=False):
    resp = HttpResponse(body, content_type="text/calendar; charset=utf-8")
    resp["Content-Disposition"] = f'{"inline" if inline else "attachment"}; filename="{filename}"'
    return resp


@require_safe
def calendar_feed(request, token):
    """The private feed calendar apps subscribe to. No sign-in: the unguessable token is the key."""
    profile = Profile.objects.select_related("user").filter(calendar_token=token, user__is_active=True).first()
    if profile is None:
        raise Http404
    resp = _ics(calendar.feed(profile.user, _site(request)), "parottasalna-live-classes.ics", inline=True)
    resp["Cache-Control"] = "private, max-age=900"
    resp["X-Robots-Tag"] = "noindex"
    return resp


@require_safe
def daily_reminder(request):
    at, minutes = calendar.parse_reminder(request.GET.get("at"), request.GET.get("mins"))
    return _ics(calendar.daily_reminder(at, minutes, _site(request)), "parottasalna-daily-learning.ics")


@login_required
@require_POST
def reset_calendar_link(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.reset_calendar_token()
    messages.success(request, "New calendar link created. The old one stops working; subscribe again with the new link.")
    return redirect("/profile/#calendar")
