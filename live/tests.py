from datetime import date, datetime, time, timedelta

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
