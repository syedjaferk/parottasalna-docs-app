import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .catalog import problem_ids
from .models import ProblemProgress


class PrepTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("s", "s@example.com", "x")
        self.pid = sorted(problem_ids())[0]

    def post(self, name, body):
        return self.client.post(reverse(name), json.dumps(body), content_type="application/json")

    def test_pages_and_data_need_login(self):
        for name in ("prep_tracker", "prep_patterns"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 302)
        self.assertEqual(self.client.get(reverse("prep_progress")).status_code, 401)
        self.assertEqual(self.client.get(reverse("prep_data", args=["catalog"])).status_code, 302)

    def test_pages_render(self):
        self.client.force_login(self.user)
        for name in ("prep_tracker", "prep_patterns"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)
        for f in ("catalog", "pattern_guides"):
            self.assertEqual(self.client.get(reverse("prep_data", args=[f])).status_code, 200)
        self.assertEqual(self.client.get("/prep/data/settings.json").status_code, 404)
        self.assertEqual(self.client.get("/prep/data/mat_hr.json").status_code, 404)

    def test_progress_roundtrip(self):
        self.client.force_login(self.user)
        self.assertEqual(self.post("prep_progress_set", {"id": self.pid, "solved": True, "note": "hi"}).status_code, 200)
        data = self.client.get(reverse("prep_progress")).json()["progress"]
        self.assertEqual(data[self.pid], {"s": True, "b": False, "n": "hi"})
        self.post("prep_progress_set", {"id": self.pid, "solved": False, "note": ""})
        self.assertFalse(ProblemProgress.objects.exists())  # empty rows are dropped

    def test_unknown_problem_rejected(self):
        self.client.force_login(self.user)
        self.assertEqual(self.post("prep_progress_set", {"id": "x:y", "solved": True}).status_code, 404)

    def test_import_and_clear(self):
        self.client.force_login(self.user)
        res = self.post("prep_progress_import", {"progress": {self.pid: {"s": True, "b": True, "n": ""}, "bad:id": {"s": True}}}).json()
        self.assertEqual(res["imported"], 1)
        res = self.post("prep_progress_clear", {"what": "bookmarks"}).json()
        self.assertEqual(res["progress"][self.pid]["b"], False)
        self.assertTrue(res["progress"][self.pid]["s"])
        self.assertEqual(self.post("prep_progress_clear", {"what": "all"}).json()["progress"], {})

    def test_progress_is_per_user(self):
        other = get_user_model().objects.create_user("o", "o@example.com", "x")
        ProblemProgress.objects.create(user=other, problem_id=self.pid, solved=True)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("prep_progress")).json()["progress"], {})
