from datetime import date, datetime, time, timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from courses.models import Course, Enrollment

from .models import LiveSession
from .services import schedule_series, sessions_for

User = get_user_model()
MODEL_BACKEND = "django.contrib.auth.backends.ModelBackend"
MEET = "https://meet.google.com/abc-defg-hij"


def at(day, hour, minute=0):
    return timezone.make_aware(datetime.combine(day, time(hour, minute)))


class LiveTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.today = timezone.localdate()
        # Freeze the clock at noon: the 8 PM test sessions would otherwise count as ended when the
        # suite runs late in the evening, which failed the deploy's test step.
        clock = mock.patch("django.utils.timezone.now", return_value=at(self.today, 12))
        clock.start()
        self.addCleanup(clock.stop)
        self.course = Course.objects.create(slug="k8s", title="Kube", build_status="ok")
        self.other = Course.objects.create(slug="other", title="Other batch", build_status="ok")
        self.free = Course.objects.create(slug="free", title="Free course", is_common=True, build_status="ok")
        Enrollment.objects.create(course=self.course, email="stu@gmail.com")
        self.student = User.objects.create_user("stu", email="stu@gmail.com")

    def session(self, course, hour=20, day=None, **kw):
        day = day or self.today
        return LiveSession.objects.create(course=course, title=kw.pop("title", f"{course.slug} class"),
                                          starts_at=at(day, hour), ends_at=at(day, hour) + timedelta(hours=1),
                                          meet_url=kw.pop("meet_url", MEET), **kw)


class StatusTests(LiveTestCase):
    def test_status_through_the_day(self):
        s = self.session(self.course, hour=20)
        self.assertEqual(s.status(at(self.today, 19, 0)), "upcoming")
        self.assertEqual(s.status(at(self.today, 19, 50)), "soon")
        self.assertEqual(s.status(at(self.today, 20, 30)), "live")
        self.assertEqual(s.status(at(self.today, 21, 0)), "ended")
        s.is_cancelled = True
        self.assertEqual(s.status(at(self.today, 20, 30)), "cancelled")

    def test_validation(self):
        s = LiveSession(course=self.course, title="x", starts_at=at(self.today, 20), ends_at=at(self.today, 19),
                        meet_url="http://meet.google.com/x")
        with self.assertRaises(ValidationError) as ctx:
            s.full_clean()
        self.assertIn("ends_at", ctx.exception.message_dict)
        self.assertIn("meet_url", ctx.exception.message_dict)


class VisibilityTests(LiveTestCase):
    def test_students_see_their_courses_with_links(self):
        self.session(self.course, title="Kube today")
        self.session(self.other, title="Other today")
        self.session(self.free, hour=18, title="Free today")
        self.session(self.course, day=self.today + timedelta(days=1), title="Kube tomorrow")
        data = sessions_for(self.student)
        self.assertEqual([i["session"].title for i in data["today"]], ["Free today", "Kube today"])
        self.assertTrue(data["show_link"])
        self.assertEqual(data["next"].title, "Kube tomorrow")

    def test_dashboard_shows_join_link_for_enrolled_course(self):
        self.session(self.course, title="Kube today")
        self.session(self.other, title="Other today", meet_url="https://meet.google.com/zzz-zzzz-zzz")
        self.client.force_login(self.student, backend=MODEL_BACKEND)
        html = self.client.get("/").content.decode()
        self.assertIn("Today's live sessions", html)
        self.assertIn(MEET, html)
        self.assertNotIn("Other today", html)
        self.assertNotIn("zzz-zzzz-zzz", html)

    def test_signed_out_landing_shows_free_sessions_without_any_link(self):
        self.session(self.free, title="Free today")
        self.session(self.course, title="Kube today")
        html = self.client.get("/").content.decode()
        self.assertIn("Free today", html)
        self.assertNotIn("Kube today", html)
        self.assertNotIn("meet.google.com", html)
        self.assertIn("Sign in to join", html)

    def test_no_card_when_nothing_is_scheduled(self):
        self.client.force_login(self.student, backend=MODEL_BACKEND)
        self.assertNotContains(self.client.get("/"), "Today's live sessions")


class ScheduleTests(LiveTestCase):
    def test_series_on_selected_weekdays_with_numbers_and_no_duplicates(self):
        monday = date(2026, 10, 12)
        created, skipped = schedule_series(self.course, "Session {n}", MEET, time(20), time(21), {0, 2, 4},
                                           monday, monday + timedelta(days=13), number_from=10)
        self.assertEqual((created, skipped), (6, 0))
        titles = list(LiveSession.objects.values_list("title", flat=True))
        self.assertEqual(titles, [f"Session {n}" for n in range(10, 16)])
        first = LiveSession.objects.first()
        self.assertEqual(timezone.localtime(first.starts_at).strftime("%a %H:%M"), "Mon 20:00")
        self.assertEqual(schedule_series(self.course, "Session {n}", MEET, time(20), time(21), {0, 2, 4},
                                         monday, monday + timedelta(days=13), number_from=10), (0, 6))

    def test_overnight_session_ends_next_day(self):
        schedule_series(self.course, "Late", MEET, time(23, 30), time(0, 30), {0, 1, 2, 3, 4, 5, 6},
                        self.today, self.today)
        s = LiveSession.objects.get()
        self.assertEqual(s.ends_at - s.starts_at, timedelta(hours=1))

    def test_admin_schedule_form(self):
        admin = User.objects.create_superuser("admin", "admin@gmail.com", "x")
        self.client.force_login(admin, backend=MODEL_BACKEND)
        self.assertContains(self.client.get("/admin/live/livesession/schedule/"), "Create sessions")
        response = self.client.post("/admin/live/livesession/schedule/", {
            "course": self.course.pk, "title": "Session {n}", "number_from": 1, "meet_url": MEET,
            "start_time": "20:00", "end_time": "21:00", "weekdays": ["0", "1", "2", "3", "4", "5", "6"],
            "first_day": "2026-11-01", "last_day": "2026-11-07", "description": "",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(LiveSession.objects.count(), 7)
        self.assertEqual(self.client.get("/admin/live/livesession/").status_code, 200)


class CalendarTests(TestCase):
    """Add to calendar: the private live-class feed and the daily learning reminder."""

    def setUp(self):
        from profiles.models import Profile
        self.mine = Course.objects.create(slug="mine", title="Docker, Kubernetes; and more")
        self.other = Course.objects.create(slug="other", title="Other course")
        self.user = get_user_model().objects.create_user("s", email="s@gmail.com")
        Enrollment.objects.create(course=self.mine, email="s@gmail.com")
        start = timezone.now() + timedelta(days=2)
        self.session = LiveSession.objects.create(course=self.mine, title="Session 3 · Pods", starts_at=start,
                                                  ends_at=start + timedelta(hours=1), meet_url="https://meet.google.com/abc-defg-hij",
                                                  description="Bring questions, please")
        LiveSession.objects.create(course=self.mine, title="Cancelled one", starts_at=start + timedelta(days=1),
                                   ends_at=start + timedelta(days=1, hours=1), meet_url="https://meet.google.com/xyz",
                                   is_cancelled=True)
        LiveSession.objects.create(course=self.other, title="Not yours", starts_at=start,
                                   ends_at=start + timedelta(hours=1), meet_url="https://meet.google.com/secret")
        self.profile = Profile.objects.create(user=self.user)
        self.token = self.profile.ensure_calendar_token()

    def feed(self, token=None):
        from django.urls import reverse
        return self.client.get(reverse("live_calendar_feed", args=[token or self.token]))

    def test_feed_has_only_my_sessions_with_meet_links(self):
        resp = self.feed()
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp["Content-Type"].startswith("text/calendar"))
        body = resp.content.decode()
        unfolded = body.replace("\r\n ", "")
        self.assertTrue(body.startswith("BEGIN:VCALENDAR\r\n") and body.endswith("END:VCALENDAR\r\n"))
        self.assertIn(f"UID:live-{self.session.pk}@parottasalna", unfolded)
        self.assertIn("SUMMARY:Docker\\, Kubernetes\; and more: Session 3 · Pods", unfolded)   # escaped
        self.assertIn("https://meet.google.com/abc-defg-hij", unfolded)
        self.assertIn("STATUS:CANCELLED", unfolded)
        self.assertNotIn("meet.google.com/secret", unfolded)       # a course I'm not enrolled in
        self.assertNotIn("Not yours", unfolded)

    def test_feed_needs_a_valid_token(self):
        self.assertEqual(self.feed("not-a-real-token").status_code, 404)
        old = self.token
        self.profile.reset_calendar_token()
        self.assertEqual(self.feed(old).status_code, 404)
        self.assertEqual(self.feed(self.profile.calendar_token).status_code, 200)
        self.user.is_active = False
        self.user.save()
        self.assertEqual(self.feed(self.profile.calendar_token).status_code, 404)

    def test_reset_link_requires_post_and_sign_in(self):
        from django.urls import reverse
        url = reverse("live_calendar_reset")
        self.assertEqual(self.client.post(url).status_code, 302)          # to sign in
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url)
        self.profile.refresh_from_db()
        self.assertNotEqual(self.profile.calendar_token, self.token)

    def test_daily_reminder_ics(self):
        from django.urls import reverse
        resp = self.client.get(reverse("live_calendar_daily"), {"at": "06:30", "mins": "20"})
        body = resp.content.decode().replace("\r\n ", "")
        self.assertIn("attachment", resp["Content-Disposition"])
        self.assertIn("RRULE:FREQ=DAILY", body)
        self.assertIn("T063000", body)
        self.assertIn("DURATION:PT20M", body)
        self.assertIn("TZID:Asia/Kolkata", body)
        bad = self.client.get(reverse("live_calendar_daily"), {"at": "25:99", "mins": "999"}).content.decode()
        self.assertIn("T210000", bad)                 # falls back to 9 PM
        self.assertIn("DURATION:PT15M", bad)          # and 15 minutes

    def test_profile_and_live_card_link_to_calendar(self):
        from django.urls import reverse
        self.client.force_login(self.user)
        page = self.client.get(reverse("profile"))
        self.assertContains(page, 'id="calendar"')
        self.assertContains(page, "calendar.google.com/calendar/render?cid=webcal")
        self.assertContains(page, "recur=RRULE")


class IcsFormatTests(TestCase):
    def test_fold_keeps_lines_short_and_utf8_intact(self):
        from . import ics
        line = "SUMMARY:" + "📖 Daily learning " * 10
        folded = ics.fold(line)
        for part in folded.split("\r\n"):
            self.assertLessEqual(len(part.encode()), 75)
        self.assertEqual(folded.replace("\r\n ", ""), line)

    def test_escape(self):
        from . import ics
        self.assertEqual(ics.escape("a,b;c\\d\ne"), "a\\,b\;c\\\\d\\ne")
