"""Reading streaks: recording activity and working out current/best streaks.

Rules
- A day (in the site's time zone, IST) counts when the student reads for GOAL_SECONDS or does
  any action (completes a chapter, submits a quiz, reviews a flashcard, saves a note).
- Freeze: a single missed day between two counted days is covered automatically, at most once per
  calendar week (Monday to Sunday). Frozen days keep the streak alive but don't add to it.
- Two missed days in a row end the streak.
- Only students enrolled in a course (and staff) have streaks, like progress tracking.
"""
from datetime import timedelta

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from courses.models import Enrollment

from .models import GOAL_SECONDS, ReadingDay

MILESTONES = (3, 7, 14, 30, 50, 100)
PING_MAX_SECONDS = 330            # one ping can credit at most this much reading
DAY_MAX_SECONDS = 6 * 60 * 60     # and a day at most this much (a tab left open all day)
CALENDAR_WEEKS = 12


def has_streak(user) -> bool:
    """Streaks only exist for students enrolled in at least one course, and for staff."""
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    return bool(user.email) and Enrollment.objects.filter(email__iexact=user.email).exists()


def _week(day):
    return day.isocalendar()[:2]


def compute(counted_days, today):
    """Streak numbers from the set of counted dates. Pure function, easy to test.

    Returns dict(current, best, frozen: set of dates, status) where status is
    "done" (today counted), "pending" (alive, read today to extend), "freeze" (yesterday was missed;
    reading today uses this week's freeze) or "none".
    """
    used_weeks, frozen = set(), set()
    best = run = 0
    prev = None
    for day in sorted(counted_days):
        if day > today:
            break
        if prev is None:
            run = 1
        else:
            gap = (day - prev).days
            missed = prev + timedelta(days=1)
            if gap == 1:
                run += 1
            elif gap == 2 and _week(missed) not in used_weeks:
                used_weeks.add(_week(missed))
                frozen.add(missed)
                run += 1
            else:
                run = 1
        best = max(best, run)
        prev = day

    if prev is None:
        return {"current": 0, "best": 0, "frozen": frozen, "status": "none"}
    gap = (today - prev).days
    if gap == 0:
        status, current = "done", run
    elif gap == 1:
        status, current = "pending", run
    elif gap == 2 and _week(today - timedelta(days=1)) not in used_weeks:
        status, current = "freeze", run
    else:
        status, current = "none", 0
    return {"current": current, "best": best, "frozen": frozen, "status": status}


def _counted_days(user):
    rows = ReadingDay.objects.filter(user=user).values_list("date", "seconds_read", "actions")
    return {day for day, seconds, actions in rows if seconds >= GOAL_SECONDS or actions > 0}


def _record(user, seconds=0, action=False):
    """Add reading time or an action to today's row. Returns (row, became_counted_now)."""
    today = timezone.localdate()
    with transaction.atomic():
        row, _ = ReadingDay.objects.select_for_update().get_or_create(user=user, date=today)
        before = row.counts
        if seconds:
            room = max(DAY_MAX_SECONDS - row.seconds_read, 0)
            ReadingDay.objects.filter(pk=row.pk).update(seconds_read=F("seconds_read") + min(seconds, room))
        if action:
            ReadingDay.objects.filter(pk=row.pk).update(actions=F("actions") + 1)
        row.refresh_from_db()
    return row, (row.counts and not before)


def record_reading(user, seconds):
    return _record(user, seconds=max(0, min(int(seconds), PING_MAX_SECONDS)))


def record_action(user):
    """Called by views that already checked the user is enrolled (can_track)."""
    return _record(user, action=True)


def summary(user, today=None):
    """Everything the dashboard card and the docs chip need."""
    today = today or timezone.localdate()
    counted = _counted_days(user)
    result = compute(counted, today)
    row = ReadingDay.objects.filter(user=user, date=today).first()
    current = result["current"]
    result.update(
        today_seconds=row.seconds_read if row else 0,
        today_done=result["status"] == "done",
        goal_seconds=GOAL_SECONDS,
        total_days=len(counted),
        milestones=[{"days": m, "earned": result["best"] >= m} for m in MILESTONES],
        next_milestone=next((m for m in MILESTONES if m > current), None),
        calendar=_calendar(counted, result["frozen"], today),
    )
    return result


def _calendar(counted, frozen, today):
    """CALENDAR_WEEKS columns of Monday..Sunday cells, oldest first."""
    start = today - timedelta(days=today.weekday()) - timedelta(weeks=CALENDAR_WEEKS - 1)
    weeks = []
    for w in range(CALENDAR_WEEKS):
        week = []
        for d in range(7):
            day = start + timedelta(weeks=w, days=d)
            if day > today:
                state = "future"
            elif day in counted:
                state = "read"
            elif day in frozen:
                state = "frozen"
            else:
                state = "missed"
            week.append({"date": day, "state": state, "today": day == today})
        weeks.append(week)
    return weeks
