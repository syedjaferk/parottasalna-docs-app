"""Add-to-calendar: a private feed of the user's live classes, and a repeating daily learning reminder."""
import re
from datetime import datetime, time, timedelta
from urllib.parse import quote, urlencode

from django.urls import reverse
from django.utils import timezone

from courses.services import accessible_courses

from . import ics
from .models import LiveSession

FEED_PAST_DAYS = 30           # keep last month's sessions so calendars don't drop them abruptly
REMINDER_MINUTES = [10, 15, 20, 30, 45, 60]
DEFAULT_AT, DEFAULT_MINUTES = time(21, 0), 15
DAILY_TITLE = "📖 Daily learning · Parottasalna"


def feed(user, site_url, now=None):
    """The .ics feed of every live session in the courses this user can open."""
    now = now or timezone.now()
    sessions = (LiveSession.objects.filter(course__in=accessible_courses(user),
                                           starts_at__gte=now - timedelta(days=FEED_PAST_DAYS))
                .select_related("course").order_by("starts_at"))
    events = []
    for s in sessions:
        details = [s.description] if s.description else []
        details += [f"Join on Google Meet: {s.meet_url}", f"Course notes: {site_url}{reverse('home')}"]
        events.append(ics.event(
            f"live-{s.pk}@parottasalna", f"{s.course.title}: {s.title}", s.starts_at, s.ends_at,
            description="\n".join(details), location=s.meet_url, url=s.meet_url,
            status="CANCELLED" if s.is_cancelled else "CONFIRMED", alarm_minutes=15, now=now))
    return ics.calendar(events, name="Parottasalna live classes", refresh_hours=6)


def parse_reminder(at, minutes):
    """Validate the ?at=HH:MM&mins=N query. Falls back to the defaults for anything odd."""
    m = re.fullmatch(r"([01]\d|2[0-3]):([0-5]\d)", at or "")
    start = time(int(m[1]), int(m[2])) if m else DEFAULT_AT
    try:
        mins = int(minutes)
    except (TypeError, ValueError):
        mins = DEFAULT_MINUTES
    return start, mins if mins in REMINDER_MINUTES else DEFAULT_MINUTES


def _first_day(at, now):
    """Today if that time is still ahead (in IST), otherwise tomorrow."""
    local = timezone.localtime(now)
    return local.date() if local.time() < at else local.date() + timedelta(days=1)


def daily_reminder(at, minutes, site_url, now=None):
    now = now or timezone.now()
    start = datetime.combine(_first_day(at, now), at)            # naive, written with TZID=Asia/Kolkata
    event = ics.event(
        f"daily-learning-{at:%H%M}@parottasalna", DAILY_TITLE, start, duration=timedelta(minutes=minutes),
        description=f"{minutes} minutes: read a chapter, take a quiz or review flashcards.\n{site_url}/",
        url=f"{site_url}/", rrule="FREQ=DAILY", tzid="Asia/Kolkata", alarm_minutes=0, now=now)
    return ics.calendar([event], extra=ics.VTIMEZONE_KOLKATA)


def google_daily_link(at, minutes, site_url, now=None):
    start = datetime.combine(_first_day(at, now or timezone.now()), at)
    end = start + timedelta(minutes=minutes)
    return "https://calendar.google.com/calendar/render?" + urlencode({
        "action": "TEMPLATE", "text": DAILY_TITLE,
        "dates": f"{start:%Y%m%dT%H%M%S}/{end:%Y%m%dT%H%M%S}", "ctz": "Asia/Kolkata",
        "recur": "RRULE:FREQ=DAILY",
        "details": f"{minutes} minutes: read a chapter, take a quiz or review flashcards.\n{site_url}/",
    })


def feed_links(request, token):
    """https, webcal:// and Google Calendar "subscribe" links for one user's feed."""
    https_url = request.build_absolute_uri(reverse("live_calendar_feed", args=[token]))
    webcal = re.sub(r"^https?://", "webcal://", https_url)
    return {
        "url": https_url,
        "webcal": webcal,
        "google": "https://calendar.google.com/calendar/render?cid=" + quote(webcal, safe=""),
    }
