from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_safe

from courses.models import Course
from courses.security import api_login_required, no_store
from courses.services import can_track

from .services import MILESTONES, PING_MAX_SECONDS, record_reading, summary


def _trackable(request):
    course = Course.objects.filter(slug=request.GET.get("course") or request.POST.get("course", ""),
                                   is_active=True).first()
    return course if course is not None and can_track(request.user, course) else None


@require_safe
@ensure_csrf_cookie
def streak_json(request):
    """The reader's streak, for the docs sidebar chip. Disabled outside enrolled courses."""
    course = _trackable(request)
    if course is None:
        return no_store(JsonResponse({"enabled": False}))
    data = summary(request.user)
    return no_store(JsonResponse({
        "enabled": True,
        "ping_url": reverse("streak_ping"),
        "course": course.slug,
        "current": data["current"],
        "best": data["best"],
        "status": data["status"],
        "today_done": data["today_done"],
        "today_seconds": data["today_seconds"],
        "goal_seconds": data["goal_seconds"],
        "next_milestone": data["next_milestone"],
    }))


@require_POST
@api_login_required
def streak_ping(request):
    """Credit active reading time from a docs page (sent after each minute or so of reading)."""
    course = _trackable(request)
    if course is None:
        return JsonResponse({"error": "Not found"}, status=404)  # not enrolled: nothing is stored
    try:
        seconds = int(request.POST.get("seconds", ""))
    except ValueError:
        return JsonResponse({"error": "Invalid seconds"}, status=400)
    if not 1 <= seconds <= PING_MAX_SECONDS:
        return JsonResponse({"error": "Invalid seconds"}, status=400)
    _, extended = record_reading(request.user, seconds)
    data = summary(request.user)
    return no_store(JsonResponse({
        "extended": extended,
        "current": data["current"],
        "best": data["best"],
        "today_done": data["today_done"],
        "today_seconds": data["today_seconds"],
        "milestone": data["current"] if extended and data["current"] in MILESTONES else None,
        "next_milestone": data["next_milestone"],
    }))
