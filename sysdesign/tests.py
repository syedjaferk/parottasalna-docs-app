import json

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from .catalog import list_problems
from .models import Problem, ProblemProgress
from .seed import DATA_DIR, load_problems

STEP_TYPES = {"choice", "multi", "estimate", "reflect"}


class SeededTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_problems()
        super().setUpTestData()


class ProblemDataTests(SeededTestCase):
    def test_every_step_is_well_formed(self):
        self.assertTrue(list_problems())
        for problem in list_problems():
            ids = [s["id"] for s in problem["steps"]]
            self.assertEqual(len(ids), len(set(ids)), problem["slug"])
            for step in problem["steps"]:
                self.assertIn(step["type"], STEP_TYPES, step["id"])
                for key in ("phase", "title", "prompt", "explain"):
                    self.assertTrue(step.get(key), f"{step['id']} missing {key}")
                if step["type"] in {"choice", "multi"}:
                    correct = [o for o in step["options"] if o["correct"]]
                    self.assertTrue(correct, step["id"])
                    if step["type"] == "choice":
                        self.assertEqual(len(correct), 1, step["id"])
                if step["type"] == "estimate":
                    self.assertGreater(step["answer"], 0)
                    self.assertGreater(step["factor"], 1)
                if step["type"] == "reflect":
                    self.assertTrue(step["points"] and step["model"], step["id"])


class LoaderTests(TestCase):
    def test_loader_is_idempotent_and_keeps_admin_choices(self):
        self.assertEqual(load_problems(), (1, 0))
        self.assertEqual(load_problems(), (0, 0))
        Problem.objects.filter(slug="tinyurl").update(is_published=False, is_pro=True, position=7)
        self.assertEqual(load_problems(), (0, 0))
        p = Problem.objects.get(slug="tinyurl")
        self.assertEqual((p.is_published, p.is_pro, p.position), (False, True, 7))

    def test_loader_restores_edited_content(self):
        load_problems()
        Problem.objects.filter(slug="tinyurl").update(title="Changed")
        self.assertEqual(load_problems(), (0, 1))
        self.assertEqual(Problem.objects.get(slug="tinyurl").title, json.loads((DATA_DIR / "tinyurl.json").read_text())["title"])

    def test_management_command(self):
        call_command("load_sysdesign", verbosity=0)
        self.assertEqual(Problem.objects.count(), 1)


class PlaygroundViewTests(SeededTestCase):
    def test_index_is_public(self):
        res = self.client.get(reverse("sysdesign_index"))
        self.assertContains(res, "TinyURL")

    def test_unpublished_problem_is_hidden(self):
        Problem.objects.update(is_published=False)
        self.assertNotContains(self.client.get(reverse("sysdesign_index")), "TinyURL")
        self.assertEqual(self.client.get("/system-design/tinyurl/").status_code, 404)

    def test_problem_page_renders_statement_and_steps(self):
        res = self.client.get(reverse("sysdesign_problem", args=["tinyurl"]))
        self.assertContains(res, "What we expect from you")
        self.assertContains(res, 'id="sd-data"')
        self.assertNotContains(res, "data-save-url")          # anonymous: progress stays in the browser

    def test_signed_in_page_points_the_script_at_the_api(self):
        self.client.force_login(get_user_model().objects.create_user("a", "a@example.com", "x"))
        self.assertContains(self.client.get(reverse("sysdesign_problem", args=["tinyurl"])), "data-save-url")

    def test_unknown_problem_is_404(self):
        self.assertEqual(self.client.get("/system-design/nope/").status_code, 404)


class ProgressApiTests(SeededTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("a", "a@example.com", "x")
        self.client.force_login(self.user)
        self.step = Problem.objects.get(slug="tinyurl").steps[0]["id"]
        self.get_url = reverse("sysdesign_progress", args=["tinyurl"])
        self.save_url = reverse("sysdesign_progress_save", args=["tinyurl"])

    def save(self, body, client=None):
        return (client or self.client).post(self.save_url, json.dumps(body), content_type="application/json")

    def test_requires_login(self):
        anon = Client()
        self.assertEqual(anon.get(self.get_url).status_code, 401)
        self.assertEqual(self.save({"answers": {}}, anon).status_code, 401)

    def test_save_requires_csrf_token(self):
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.user)
        self.assertEqual(self.save({"answers": {}, "current": 0}, strict).status_code, 403)

    def test_empty_then_roundtrip(self):
        self.assertEqual(self.client.get(self.get_url).json(), {"exists": False, "answers": {}, "current": 0})
        res = self.save({"answers": {self.step: {"verdict": "good"}}, "current": 1})
        self.assertEqual(res.status_code, 200)
        data = self.client.get(self.get_url).json()
        self.assertEqual((data["exists"], data["current"], data["answers"]), (True, 1, {self.step: {"verdict": "good"}}))

    def test_save_replaces_and_reset_clears(self):
        self.save({"answers": {self.step: {"verdict": "good"}}, "current": 1})
        self.save({"answers": {}, "current": 0})
        self.assertEqual(self.client.get(self.get_url).json()["answers"], {})

    def test_unknown_steps_and_bad_values_are_dropped(self):
        self.save({"answers": {"nope": {"x": 1}, self.step: "str"}, "current": 9999})
        row = ProblemProgress.objects.get()
        self.assertEqual(row.answers, {})
        self.assertLessEqual(row.current_step, len(Problem.objects.get().steps))
        self.assertEqual(self.save([1, 2]).status_code, 400)
        self.assertEqual(self.client.post(self.save_url, "{", content_type="application/json").status_code, 400)

    def test_merge_keeps_account_answers_and_adds_local_ones(self):
        steps = [s["id"] for s in Problem.objects.get().steps]
        self.save({"answers": {steps[0]: {"verdict": "good"}}, "current": 1})
        res = self.save({"answers": {steps[0]: {"verdict": "local"}, steps[1]: {"verdict": "local"}}, "current": 2, "merge": True}).json()
        self.assertEqual(res["answers"], {steps[0]: {"verdict": "good"}, steps[1]: {"verdict": "local"}})
        self.assertEqual(res["current"], 2)

    def test_progress_is_per_user(self):
        self.save({"answers": {self.step: {"verdict": "good"}}, "current": 1})
        other = Client()
        other.force_login(get_user_model().objects.create_user("o", "o@example.com", "x"))
        self.assertFalse(other.get(self.get_url).json()["exists"])

    def test_unknown_or_unpublished_problem_is_404(self):
        self.assertEqual(self.client.get("/system-design/nope/progress.json").status_code, 404)
        Problem.objects.update(is_published=False)
        self.assertEqual(self.client.get(self.get_url).status_code, 404)
