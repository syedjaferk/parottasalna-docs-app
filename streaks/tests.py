from datetime import date, timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase

from courses.models import Course, Enrollment

from .models import ReadingDay
from .services import compute, record_action, summary

User = get_user_model()
MODEL_BACKEND = "django.contrib.auth.backends.ModelBackend"
# A Wednesday, so the week runs Mon 5 Oct .. Sun 11 Oct 2026.
TODAY = date(2026, 10, 7)


def days_ago(*offsets):
    return {TODAY - timedelta(days=n) for n in offsets}


class ComputeTests(SimpleTestCase):
    def test_no_reading(self):
        self.assertEqual(compute(set(), TODAY)["status"], "none")

    def test_consecutive_days_and_today_pending(self):
        result = compute(days_ago(1, 2, 3), TODAY)
        self.assertEqual((result["current"], result["status"]), (3, "pending"))
        result = compute(days_ago(0, 1, 2, 3), TODAY)
        self.assertEqual((result["current"], result["best"], result["status"]), (4, 4, "done"))

    def test_single_missed_day_is_frozen_and_not_counted(self):
        result = compute(days_ago(0, 2, 3), TODAY)  # yesterday missed
        self.assertEqual((result["current"], result["status"]), (3, "done"))
        self.assertEqual(result["frozen"], days_ago(1))

    def test_only_one_freeze_per_week(self):
        # Missed Sun 4 Oct and Tue 6 Oct: different weeks (Mon-Sun), both frozen.
        result = compute({date(2026, 10, d) for d in (3, 5, 7)}, TODAY)
        self.assertEqual((result["current"], len(result["frozen"])), (3, 2))
        # Missed Fri 2 and Sun 4 Oct, both in the week of 28 Sep: the second gap breaks the streak.
        result = compute({date(2026, 10, d) for d in (1, 3, 5, 6, 7)}, TODAY)
        self.assertEqual((result["current"], result["best"], len(result["frozen"])), (3, 3, 1))
        # Missed Mon 5 and Wed 7 Oct, same week again.
        result = compute({date(2026, 10, d) for d in (4, 6, 8)}, date(2026, 10, 8))
        self.assertEqual((result["current"], result["best"]), (1, 2))

    def test_two_missed_days_break_it(self):
        result = compute(days_ago(3, 4, 5), TODAY)
        self.assertEqual((result["current"], result["best"], result["status"]), (0, 3, "none"))

    def test_missed_yesterday_is_still_alive_today(self):
        result = compute(days_ago(2, 3), TODAY)
        self.assertEqual((result["current"], result["status"]), (2, "freeze"))


class StreakApiTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(slug="c1", title="C1", build_status="ok")
        self.common = Course.objects.create(slug="open", title="Open", is_common=True, build_status="ok")
        Enrollment.objects.create(course=self.course, email="stu@gmail.com")
        self.student = User.objects.create_user("stu", email="stu@gmail.com")
        self.reader = User.objects.create_user("reader", email="reader@gmail.com")
        self.client = self.client_class(enforce_csrf_checks=True)

    def ping(self, seconds, course="c1"):
        token = self.client.get("/streak.json", {"course": course}).cookies.get("csrftoken")
        return self.client.post("/streak/ping/", {"course": course, "seconds": seconds},
                                HTTP_X_CSRFTOKEN=token.value if token else "")

    def test_reading_a_minute_counts_the_day_once(self):
        self.client.force_login(self.student, backend=MODEL_BACKEND)
        first = self.ping(30).json()
        self.assertEqual((first["extended"], first["today_done"], first["current"]), (False, False, 0))
        second = self.ping(30).json()
        self.assertEqual((second["extended"], second["today_done"], second["current"]), (True, True, 1))
        self.assertFalse(self.ping(300).json()["extended"])  # only once a day
        self.assertEqual(ReadingDay.objects.get(user=self.student).seconds_read, 360)

    def test_bad_input_and_caps(self):
        self.client.force_login(self.student, backend=MODEL_BACKEND)
        for bad in ("0", "-5", "abc", "100000"):
            self.assertEqual(self.ping(bad).status_code, 400, bad)
        with mock.patch("streaks.services.DAY_MAX_SECONDS", 400):
            for _ in range(3):
                self.ping(300)
        self.assertEqual(ReadingDay.objects.get(user=self.student).seconds_read, 400)

    def test_not_enrolled_readers_have_no_streak_and_store_nothing(self):
        self.client.force_login(self.reader, backend=MODEL_BACKEND)
        self.assertEqual(self.client.get("/streak.json", {"course": "open"}).json(), {"enabled": False})
        self.assertEqual(self.ping(60, course="open").status_code, 404)
        self.client.logout()
        self.assertEqual(self.client.get("/streak.json", {"course": "c1"}).json(), {"enabled": False})
        self.assertFalse(ReadingDay.objects.exists())

    def test_actions_count_the_day(self):
        record_action(self.student)
        data = summary(self.student)
        self.assertEqual((data["current"], data["today_done"]), (1, True))

    def test_marking_a_chapter_complete_counts(self):
        import tempfile
        from pathlib import Path

        from django.test import override_settings

        with tempfile.TemporaryDirectory() as root, override_settings(DOCS_BUILD_ROOT=Path(root)):
            (Path(root) / "c1" / "html").mkdir(parents=True)
            (Path(root) / "c1" / "html" / "intro.html").write_text("x")
            self.client.force_login(self.student, backend=MODEL_BACKEND)
            token = self.client.get("/courses/c1/progress.json").cookies["csrftoken"].value
            self.client.post("/courses/c1/progress/", {"page": "intro", "completed": "true"}, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(ReadingDay.objects.get(user=self.student).actions, 1)

    def test_dashboard_card_only_for_students_with_a_streak(self):
        self.client.force_login(self.student, backend=MODEL_BACKEND)
        self.assertContains(self.client.get("/"), "reading streak")
        self.client.force_login(self.reader, backend=MODEL_BACKEND)
        self.assertNotContains(self.client.get("/"), "reading streak")
