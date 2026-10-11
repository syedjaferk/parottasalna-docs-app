import json
from io import BytesIO
from unittest import mock
from urllib.error import HTTPError

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from courses.models import Course
from jobs.models import Job

User = get_user_model()
BACKEND = "django.contrib.auth.backends.ModelBackend"


def fake_calendly(responses):
    """Patch urlopen so each URL path prefix returns the given JSON."""
    def opener(req, timeout=None):
        for prefix, body in responses.items():
            if prefix in req.full_url:
                return BytesIO(json.dumps(body).encode())
        raise AssertionError(f"unexpected Calendly URL {req.full_url}")
    return mock.patch("panel.calendly.urlopen", side_effect=opener)


EVENT = "https://api.calendly.com/scheduled_events/EV1"
RESPONSES = {
    "/users/me": {"resource": {"uri": "https://api.calendly.com/users/ME"}},
    "/scheduled_events?": {"collection": [{
        "uri": EVENT, "name": "30 Minute Meeting",
        "start_time": "2030-01-15T04:30:00.000000Z", "end_time": "2030-01-15T05:00:00.000000Z",
        "location": {"type": "google_conference", "join_url": "https://meet.google.com/abc-defg-hij"},
    }]},
    "/scheduled_events/EV1/invitees": {"collection": [{
        "name": "Priya", "email": "priya@example.com",
        "questions_and_answers": [{"question": "What do you want to discuss?", "answer": "Career switch to DevOps"}],
    }]},
}


class PanelTests(TestCase):
    def setUp(self):
        cache.clear()
        self.staff = User.objects.create_user("admin", is_staff=True)
        self.student = User.objects.create_user("stu", email="stu@example.com")

    def test_staff_only(self):
        self.assertEqual(self.client.get(reverse("panel_home")).status_code, 302)
        self.client.force_login(self.student, backend=BACKEND)
        self.assertEqual(self.client.get(reverse("panel_home")).status_code, 302)   # admin login
        self.assertNotContains(self.client.get("/privacy/"), "Panel")

    @override_settings(CALENDLY_TOKEN="")
    def test_pending_jobs_failed_builds_and_badge(self):
        Job.objects.create(title="Pending Dev", company="Acme", location="Chennai", description="x",
                           apply_url="https://acme.example", posted_by=self.student)
        Course.objects.create(slug="broken", title="Broken course", build_status=Course.BuildStatus.FAILED)
        self.client.force_login(self.staff, backend=BACKEND)
        page = self.client.get(reverse("panel_home"))
        self.assertContains(page, "Pending Dev")
        self.assertContains(page, "Broken course")
        self.assertContains(page, "Calendly isn't connected")
        self.assertContains(page, '<span class="badge" aria-label="2 waiting">2</span>')    # header badge

    @override_settings(CALENDLY_TOKEN="")
    def test_approve_from_panel_returns_to_panel(self):
        job = Job.objects.create(title="Dev", company="Acme", location="X", description="x",
                                 apply_url="https://acme.example", posted_by=self.student)
        self.client.force_login(self.staff, backend=BACKEND)
        r = self.client.post(reverse("job_moderate", args=[job.pk]),
                             {"action": "approve", "next": reverse("panel_home") + "#jobs"})
        self.assertRedirects(r, reverse("panel_home") + "#jobs", fetch_redirect_response=False)
        r = self.client.post(reverse("job_moderate", args=[job.pk]),
                             {"action": "approve", "next": "https://evil.example/"})
        self.assertRedirects(r, reverse("job_review"), fetch_redirect_response=False)   # no open redirect

    @override_settings(CALENDLY_TOKEN="test-token")
    def test_upcoming_calls_from_calendly(self):
        self.client.force_login(self.staff, backend=BACKEND)
        with fake_calendly(RESPONSES) as opener:
            page = self.client.get(reverse("panel_home"))
            self.assertContains(page, "Priya")
            self.assertContains(page, "Career switch to DevOps")
            self.assertContains(page, "https://meet.google.com/abc-defg-hij")
            sent = opener.call_args_list[0][0][0]
            self.assertEqual(sent.get_header("Authorization"), "Bearer test-token")
            calls_made = opener.call_count
            self.client.get(reverse("panel_home"))                      # cached: no new requests
            self.assertEqual(opener.call_count, calls_made)
            self.client.get(reverse("panel_home") + "?refresh=calls")   # refresh: asks again
            self.assertGreater(opener.call_count, calls_made)

    @override_settings(CALENDLY_TOKEN="bad")
    def test_calendly_errors_are_shown_not_raised(self):
        self.client.force_login(self.staff, backend=BACKEND)
        err = HTTPError("https://api.calendly.com/users/me", 401, "Unauthorized", {}, None)
        with mock.patch("panel.calendly.urlopen", side_effect=err):
            self.assertContains(self.client.get(reverse("panel_home")), "Calendly rejected the token")
