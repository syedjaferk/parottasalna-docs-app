from datetime import datetime, timedelta

from django.utils import timezone

from courses.services import accessible_courses, public_courses

from .models import JOIN_EARLY_MINUTES, LiveSession


def _day_bounds(day):
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime.combine(day, datetime.min.time()), tz)
    return start, start + timedelta(days=1)


def sessions_for(user, now=None):
    """Today's sessions and the next one after today, for the courses this visitor can open.

    Signed-out visitors only see sessions of the free (common) courses, and never get the link.
    """
    now = now or timezone.now()
    courses = accessible_courses(user) if user.is_authenticated else public_courses()
    start, end = _day_bounds(timezone.localdate(now))
    base = LiveSession.objects.filter(course__in=courses).select_related("course")
    today = list(base.filter(starts_at__gte=start, starts_at__lt=end))
    upcoming = base.filter(starts_at__gte=end, is_cancelled=False).first()
    show_link = user.is_authenticated
    items = [{
        "session": s,
        "status": s.status(now),
        "join_from": s.starts_at - timedelta(minutes=JOIN_EARLY_MINUTES),
        "show_link": show_link,
    } for s in today]
    return {"today": items, "next": upcoming, "show_link": show_link}


def schedule_series(course, title, meet_url, start_time, end_time, weekdays, first_day, last_day,
                    number_from=None, description=""):
    """Create one session per matching day. "{n}" in the title is replaced by a running number.

    Days that already have a session for this course at that time are skipped.
    Returns (created, skipped).
    """
    tz = timezone.get_current_timezone()
    created = skipped = 0
    number = number_from
    day = first_day
    while day <= last_day:
        if day.weekday() in weekdays:
            starts = timezone.make_aware(datetime.combine(day, start_time), tz)
            ends = timezone.make_aware(datetime.combine(day, end_time), tz)
            if ends <= starts:
                ends += timedelta(days=1)  # e.g. 11:30 PM to 12:30 AM
            label = title.replace("{n}", str(number)) if number is not None else title
            _, made = LiveSession.objects.get_or_create(
                course=course, starts_at=starts,
                defaults={"title": label, "ends_at": ends, "meet_url": meet_url, "description": description},
            )
            if made:
                created += 1
                if number is not None:
                    number += 1
            else:
                skipped += 1
        day += timedelta(days=1)
    return created, skipped
