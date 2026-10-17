import json
from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from courses.models import Course, Enrollment

from . import services as svc
from .models import Assessment, AssessmentAttempt, AssessmentQuestion

User = get_user_model()
BACKEND = "django.contrib.auth.backends.ModelBackend"


class AssessmentCase(TestCase):
    def setUp(self):
        self.course = Course.objects.create(slug="c1", title="C1", build_status="ok")
        Enrollment.objects.create(course=self.course, email="stu@gmail.com")
        self.student = User.objects.create_user("stu", email="stu@gmail.com")
        self.outsider = User.objects.create_user("out", email="out@gmail.com")
        self.staff = User.objects.create_user("adm", email="adm@gmail.com", is_staff=True)
        self.exam = Assessment.objects.create(title="Exam", slug="exam", course=self.course, time_limit_minutes=10,
                                              max_attempts=2, is_published=True, shuffle_questions=False)
        self.q1 = AssessmentQuestion.objects.create(assessment=self.exam, text="Pick pwd", choices="ls\n*pwd\ncd", order=1)
        self.q2 = AssessmentQuestion.objects.create(assessment=self.exam, text="Two", choices="*a\nb\n*c", points=2, order=2)

    def login(self, user):
        self.client.force_login(user, backend=BACKEND)

    def answers(self, a=1, b=(0, 2)):
        return {str(self.q1.pk): [a], str(self.q2.pk): list(b)}


class ServiceTests(AssessmentCase):
    def test_grading_is_all_or_nothing_per_question(self):
        qs = list(self.exam.questions.all())
        self.assertEqual(svc.grade(qs, self.answers()), (3, 3))
        self.assertEqual(svc.grade(qs, self.answers(b=(0,))), (1, 3))
        self.assertEqual(svc.grade(qs, {}), (0, 3))

    def test_clean_answers_drops_junk(self):
        qs = list(self.exam.questions.all())
        cleaned = svc.clean_answers({str(self.q1.pk): [1, 99, "x", -1, True], "999": [0]}, qs)
        self.assertEqual(cleaned[str(self.q1.pk)], [1])
        self.assertNotIn("999", cleaned)

    def test_start_sets_deadline_once_and_resumes(self):
        now = timezone.now()
        attempt, resumed = svc.start_attempt(self.exam, self.student, now)
        self.assertFalse(resumed)
        self.assertEqual(attempt.deadline, now + timedelta(minutes=10))
        again, resumed = svc.start_attempt(self.exam, self.student, now + timedelta(minutes=3))
        self.assertTrue(resumed)
        self.assertEqual(again.pk, attempt.pk)
        self.assertEqual(again.deadline, attempt.deadline)        # refreshing never restarts the clock

    def test_close_time_caps_the_deadline(self):
        now = timezone.now()
        self.exam.closes_at = now + timedelta(minutes=4)
        self.exam.save()
        attempt, _ = svc.start_attempt(self.exam, self.student, now)
        self.assertEqual(attempt.deadline, self.exam.closes_at)

    def test_window_and_attempt_limits(self):
        now = timezone.now()
        self.exam.opens_at = now + timedelta(hours=1)
        self.exam.save()
        with self.assertRaises(svc.AssessmentError):
            svc.start_attempt(self.exam, self.student, now)
        self.exam.opens_at = None
        self.exam.closes_at = now - timedelta(minutes=1)
        self.exam.save()
        with self.assertRaises(svc.AssessmentError):
            svc.start_attempt(self.exam, self.student, now)
        self.exam.closes_at = None
        self.exam.save()
        for _ in range(2):
            a, _ = svc.start_attempt(self.exam, self.student, now)
            svc.finalize(a.pk, answers=self.answers(), now=now)
        with self.assertRaises(svc.AssessmentError):
            svc.start_attempt(self.exam, self.student, now)

    def test_autosave_then_expiry_grades_saved_answers(self):
        now = timezone.now()
        attempt, _ = svc.start_attempt(self.exam, self.student, now)
        self.assertTrue(svc.save_answers(attempt, self.answers(b=(0,)), now + timedelta(minutes=2)))
        late = now + timedelta(minutes=10, seconds=svc.GRACE_SECONDS + 1)
        self.assertFalse(svc.save_answers(attempt, self.answers(), late))        # too late to change anything
        self.assertEqual(svc.expire_stale(now=late), 1)
        attempt.refresh_from_db()
        self.assertTrue(attempt.timed_out)
        self.assertEqual((attempt.score, attempt.max_score), (1, 3))             # only the autosaved answers count
        self.assertLessEqual(attempt.submitted_at, attempt.deadline)

    def test_finalize_is_idempotent(self):
        attempt, _ = svc.start_attempt(self.exam, self.student)
        first = svc.finalize(attempt.pk, answers=self.answers())
        second = svc.finalize(attempt.pk, answers={})
        self.assertEqual(first.score, second.score)
        self.assertEqual(second.score, 3)

    def test_expire_leaves_running_attempts_alone(self):
        now = timezone.now()
        svc.start_attempt(self.exam, self.student, now)
        self.assertEqual(svc.expire_stale(now=now + timedelta(minutes=9)), 0)


class ViewTests(AssessmentCase):
    def start(self):
        response = self.client.post(reverse("assessment_start", args=["exam"]))
        return AssessmentAttempt.objects.get(user=self.student), response

    def test_access_rules(self):
        self.assertEqual(self.client.get(reverse("assessment_list")).status_code, 302)       # login required
        self.login(self.outsider)
        self.assertEqual(self.client.get(reverse("assessment_detail", args=["exam"])).status_code, 404)
        self.assertNotIn("Exam", self.client.get(reverse("assessment_list")).content.decode())
        open_exam = Assessment.objects.create(title="Open", slug="open", is_published=True)
        AssessmentQuestion.objects.create(assessment=open_exam, text="x", choices="*a\nb")
        self.assertEqual(self.client.get(reverse("assessment_detail", args=["open"])).status_code, 200)
        self.login(self.student)
        self.assertContains(self.client.get(reverse("assessment_list")), "Exam")

    def test_drafts_are_staff_only(self):
        self.exam.is_published = False
        self.exam.save()
        self.login(self.student)
        self.assertEqual(self.client.get(reverse("assessment_detail", args=["exam"])).status_code, 404)
        self.login(self.staff)
        self.assertEqual(self.client.get(reverse("assessment_detail", args=["exam"])).status_code, 200)

    def test_full_flow_submit_and_result(self):
        self.login(self.student)
        attempt, response = self.start()
        self.assertRedirects(response, reverse("assessment_take", args=[attempt.pk]))
        page = self.client.get(reverse("assessment_take", args=[attempt.pk]))
        self.assertContains(page, 'id="timer"')
        self.assertContains(page, "data-deadline")
        post = {f"q{self.q1.pk}": "1", f"q{self.q2.pk}": ["0", "2"]}
        response = self.client.post(reverse("assessment_take", args=[attempt.pk]), post)
        self.assertRedirects(response, reverse("assessment_result", args=[attempt.pk]))
        attempt.refresh_from_db()
        self.assertEqual((attempt.score, attempt.max_score, attempt.timed_out), (3, 3, False))
        self.assertContains(self.client.get(reverse("assessment_result", args=[attempt.pk])), "100%")
        # a submitted attempt can't be reopened
        self.assertRedirects(self.client.get(reverse("assessment_take", args=[attempt.pk])),
                             reverse("assessment_result", args=[attempt.pk]))

    def test_autosave_endpoint_and_resume(self):
        self.login(self.student)
        attempt, _ = self.start()
        url = reverse("assessment_save", args=[attempt.pk])
        r = self.client.post(url, json.dumps({"answers": {str(self.q1.pk): [1]}}), content_type="application/json")
        self.assertEqual(r.json()["ok"], True)
        self.assertGreater(r.json()["remaining"], 0)
        page = self.client.get(reverse("assessment_take", args=[attempt.pk]))
        self.assertContains(page, "checked")                                    # the saved answer is restored
        self.assertEqual(self.client.post(url, "not json", content_type="application/json").status_code, 400)

    def test_posting_after_deadline_uses_only_autosaved_answers(self):
        self.login(self.student)
        attempt, _ = self.start()
        self.client.post(reverse("assessment_save", args=[attempt.pk]),
                         json.dumps({"answers": {str(self.q1.pk): [1]}}), content_type="application/json")
        later = timezone.now() + timedelta(minutes=10, seconds=svc.GRACE_SECONDS + 5)
        with mock.patch("django.utils.timezone.now", return_value=later):
            self.client.post(reverse("assessment_take", args=[attempt.pk]),
                             {f"q{self.q1.pk}": "1", f"q{self.q2.pk}": ["0", "2"], "auto": "1"})
        attempt.refresh_from_db()
        self.assertTrue(attempt.timed_out)
        self.assertEqual(attempt.score, 1)                                       # the late answers for Q2 were ignored

    def test_submit_inside_grace_period_counts(self):
        self.login(self.student)
        attempt, _ = self.start()
        just_after = attempt.deadline + timedelta(seconds=svc.GRACE_SECONDS - 5)
        with mock.patch("django.utils.timezone.now", return_value=just_after):
            self.client.post(reverse("assessment_take", args=[attempt.pk]),
                             {f"q{self.q1.pk}": "1", f"q{self.q2.pk}": ["0", "2"], "auto": "1"})
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 3)
        self.assertTrue(attempt.timed_out)

    def test_opening_an_expired_attempt_closes_it(self):
        self.login(self.student)
        attempt, _ = self.start()
        later = attempt.deadline + timedelta(minutes=5)
        with mock.patch("django.utils.timezone.now", return_value=later):
            response = self.client.get(reverse("assessment_take", args=[attempt.pk]))
        self.assertRedirects(response, reverse("assessment_result", args=[attempt.pk]))
        attempt.refresh_from_db()
        self.assertTrue(attempt.timed_out)

    def test_other_students_cannot_touch_my_attempt(self):
        self.login(self.student)
        attempt, _ = self.start()
        other = User.objects.create_user("o2", email="o2@gmail.com")
        Enrollment.objects.create(course=self.course, email="o2@gmail.com")
        self.login(other)
        self.assertEqual(self.client.get(reverse("assessment_take", args=[attempt.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("assessment_save", args=[attempt.pk]), "{}", content_type="application/json").status_code, 404)

    def test_hidden_answers_and_staff_results(self):
        self.exam.show_answers = False
        self.exam.save()
        self.login(self.student)
        attempt, _ = self.start()
        self.client.post(reverse("assessment_take", args=[attempt.pk]), {})
        self.assertContains(self.client.get(reverse("assessment_result", args=[attempt.pk])), "not shown")
        self.assertEqual(self.client.get(reverse("assessment_results", args=["exam"])).status_code, 302)   # staff only
        self.login(self.staff)
        self.assertContains(self.client.get(reverse("assessment_results", args=["exam"])), "stu@gmail.com")
        csv = self.client.get(reverse("assessment_results_csv", args=["exam"])).content.decode()
        self.assertIn("stu@gmail.com", csv)

    def test_question_order_is_stable_per_attempt(self):
        self.exam.shuffle_questions = True
        self.exam.save()
        self.login(self.student)
        attempt, _ = self.start()
        first = [q.pk for q in svc.ordered_questions(attempt)]
        attempt.refresh_from_db()
        self.assertEqual(first, [q.pk for q in svc.ordered_questions(attempt)])
        self.assertEqual(sorted(first), sorted([self.q1.pk, self.q2.pk]))


class LoadAssessmentsTests(AssessmentCase):
    YAML = """\
slug: from-yaml
title: From YAML
description: Loaded from a file.
time_limit_minutes: 15
pass_percentage: 70
max_attempts: 2
questions:
  - text: Which command lists files?
    choices: |
      *ls
      cd
    explanation: ls lists.
  - text: Pick all.
    choices: |
      *a
      *b
      c
    points: 2
"""

    def load(self, text):
        import tempfile
        from io import StringIO
        from pathlib import Path

        from django.core.management import call_command
        from django.test import override_settings

        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "c1" / "assessments"
            folder.mkdir(parents=True)
            (folder / "exam.yaml").write_text(text, encoding="utf-8")
            with override_settings(COURSES_SRC_ROOT=Path(root)):
                call_command("load_assessments", "c1", stdout=StringIO())

    def test_load_creates_then_updates_in_place(self):
        self.load(self.YAML)
        loaded = Assessment.objects.get(slug="from-yaml")
        self.assertEqual((loaded.course, loaded.time_limit_minutes, loaded.questions.count()), (self.course, 15, 2))
        first_ids = list(loaded.questions.values_list("pk", flat=True))
        svc.start_attempt(loaded, self.student)               # an attempt exists: reloading must keep it
        self.load(self.YAML.replace("15", "25"))
        loaded.refresh_from_db()
        self.assertEqual(loaded.time_limit_minutes, 25)
        self.assertEqual(list(loaded.questions.values_list("pk", flat=True)), first_ids)
        self.assertEqual(AssessmentAttempt.objects.count(), 1)

    def test_bad_question_is_rejected(self):
        from django.core.management.base import CommandError
        with self.assertRaises(CommandError):
            self.load(self.YAML.replace("*ls", "ls"))        # no correct choice


class ChoiceShufflingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("s", email="s@x.com", password="pw")
        self.exam = Assessment.objects.create(title="E", slug="e", is_published=True, time_limit_minutes=30)
        self.q = AssessmentQuestion.objects.create(assessment=self.exam, text="Pick c", choices="a\nb\n*c\nd\ne\nf", order=1)

    def start(self):
        attempt, _ = svc.start_attempt(self.exam, self.user)
        return attempt

    def test_each_attempt_gets_a_permutation_that_is_kept(self):
        attempt = self.start()
        order = attempt.choice_order[str(self.q.pk)]
        self.assertEqual(sorted(order), list(range(6)))
        self.assertEqual(svc.choice_sequence(attempt, self.q), order)
        shown = [i for i, _, _ in __import__("assessments.views", fromlist=["x"])._form_items(attempt)[0]["choices"]]
        self.assertEqual(shown, order)

    def test_orders_differ_between_students(self):
        seen = set()
        for n in range(12):
            other = User.objects.create_user(f"u{n}", email=f"u{n}@x.com", password="pw")
            attempt, _ = svc.start_attempt(self.exam, other)
            seen.add(tuple(attempt.choice_order[str(self.q.pk)]))
        self.assertGreater(len(seen), 1)

    def test_grading_uses_the_original_index_not_the_position(self):
        attempt = self.start()
        done = svc.finalize(attempt.pk, answers={str(self.q.pk): [2]})   # original index 2 = "c", wherever it was shown
        self.assertEqual((done.score, done.max_score), (1, 1))
        wrong = svc.finalize(self.start_other().pk, answers={str(self.q.pk): [0]})
        self.assertEqual(wrong.score, 0)

    def start_other(self):
        other = User.objects.create_user("o", email="o@x.com", password="pw")
        return svc.start_attempt(self.exam, other)[0]

    def test_turning_it_off_keeps_the_written_order(self):
        self.exam.shuffle_choices = False
        self.exam.save()
        attempt = self.start()
        self.assertEqual(attempt.choice_order, {})
        self.assertEqual(svc.choice_sequence(attempt, self.q), list(range(6)))

    def test_old_attempts_without_an_order_still_work(self):
        attempt = self.start()
        attempt.choice_order = {}
        attempt.save()
        self.assertEqual(svc.choice_sequence(attempt, self.q), list(range(6)))


class AdminShareLinkTests(TestCase):
    def test_admin_shows_the_student_link_and_copy_button(self):
        staff = User.objects.create_superuser("root", "root@x.com", "pw")
        exam = Assessment.objects.create(title="Share me", slug="share-me", is_published=False)
        self.client.force_login(staff)
        listing = self.client.get("/admin/assessments/assessment/").content.decode()
        self.assertIn('data-copy-share="/assessments/share-me/"', listing)
        edit = self.client.get(f"/admin/assessments/assessment/{exam.pk}/change/").content.decode()
        self.assertIn("/assessments/share-me/", edit)
        self.assertIn("Not visible to students until it is published", edit)
        self.assertIn("admin-assessment-share.js", edit)
