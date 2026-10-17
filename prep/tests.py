import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from . import catalog as catalog_module
from .catalog import problem_ids
from .models import Attempt, CatalogProblem, PatternGuide, PlacementQuestion, PrepProfile, ProblemProgress
from .seed import DATA_DIR, seed_prep


class SeededTestCase(TestCase):
    """The prep content lives in the database, so load the JSON seed files before each test class."""

    @classmethod
    def setUpTestData(cls):
        seed_prep()
        super().setUpTestData()

    def setUp(self):
        catalog_module.invalidate()     # rolled-back rows from an earlier test must not linger in the cache
        super().setUp()


class PrepTests(SeededTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("s", "s@example.com", "x")
        self.pid = sorted(problem_ids())[0]

    def post(self, name, body):
        return self.client.post(reverse(name), json.dumps(body), content_type="application/json")

    def test_pages_and_data_need_login(self):
        for name in ("prep_home", "prep_tracker", "prep_patterns", "prep_placement"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 302)
        self.assertEqual(self.client.get(reverse("prep_progress")).status_code, 401)
        self.assertEqual(self.client.get(reverse("prep_data", args=["catalog"])).status_code, 302)

    def test_pages_render(self):
        self.client.force_login(self.user)
        for name in ("prep_home", "prep_tracker", "prep_patterns", "prep_placement"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)
        for f in ("catalog", "pattern_guides"):
            self.assertEqual(self.client.get(reverse("prep_data", args=[f])).status_code, 200)
        self.assertEqual(self.client.get("/prep/data/settings.json").status_code, 404)
        self.assertEqual(self.client.get("/prep/data/mat_hr.json").status_code, 404)

    def test_progress_roundtrip(self):
        self.client.force_login(self.user)
        self.assertEqual(self.post("prep_progress_set", {"id": self.pid, "solved": True, "note": "hi"}).status_code, 200)
        data = self.client.get(reverse("prep_progress")).json()["progress"]
        entry = data[self.pid]
        self.assertEqual((entry["s"], entry["b"], entry["n"], entry["st"]), (True, False, "hi", 1))   # a plain tick starts the cycle
        self.assertTrue(entry["nr"])
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


class SchedulingTests(SeededTestCase):
    def test_cold_solves_climb_the_stages(self):
        from datetime import date
        from .scheduling import apply_attempt
        today = date(2026, 10, 17)
        stage, due = apply_attempt(0, "cold", 4, today)
        self.assertEqual((stage, due), (1, date(2026, 10, 18)))            # re-solve after 1 day
        stage, due = apply_attempt(stage, "cold", 4, today)
        self.assertEqual((stage, due), (2, date(2026, 10, 24)))            # then 1 week
        stage, due = apply_attempt(stage, "cold", 5, today)
        self.assertEqual((stage, due), (3, date(2026, 11, 11)))            # then 3-4 weeks
        self.assertEqual(apply_attempt(stage, "cold", 5, today), (4, None))   # mastered

    def test_hint_fail_and_low_confidence_restart_the_queue(self):
        from datetime import date
        from .scheduling import apply_attempt
        today = date(2026, 10, 17)
        self.assertEqual(apply_attempt(3, "hint", 4, today), (1, date(2026, 10, 18)))
        self.assertEqual(apply_attempt(3, "fail", None, today), (0, date(2026, 10, 18)))
        self.assertEqual(apply_attempt(3, "cold", 2, today), (1, date(2026, 10, 18)))   # barely solved = not solid


class LogAttemptTests(SeededTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("s", "s@example.com", "x")
        self.client.force_login(self.user)
        self.pid = sorted(problem_ids())[0]

    def log(self, **body):
        return self.client.post(reverse("prep_progress_log"), json.dumps({"id": self.pid, **body}), content_type="application/json")

    def test_cold_then_review_then_fail(self):
        res = self.log(outcome="cold", confidence=4, note="sort first").json()["entry"]
        self.assertEqual((res["s"], res["st"], res["at"], res["n"]), (True, 1, 1, "sort first"))
        self.assertEqual(Attempt.objects.get().is_review, False)
        res = self.log(outcome="cold", confidence=5).json()["entry"]
        self.assertEqual(res["st"], 2)
        self.assertTrue(Attempt.objects.first().is_review)
        res = self.log(outcome="fail").json()["entry"]
        self.assertEqual((res["s"], res["st"]), (True, 0))                 # stays solved, goes back in the queue

    def test_first_failure_is_not_solved_but_is_queued(self):
        res = self.log(outcome="fail").json()["entry"]
        self.assertEqual((res["s"], res["st"], res["at"]), (False, 0, 1))
        self.assertTrue(res["nr"])

    def test_rejects_bad_input(self):
        self.assertEqual(self.log(outcome="nope").status_code, 400)
        self.assertEqual(self.client.post(reverse("prep_progress_log"), json.dumps({"id": "x:y", "outcome": "cold"}), content_type="application/json").status_code, 400)
        self.assertIsNone(self.log(outcome="cold", confidence=9).json()["entry"]["cf"])   # out of range is ignored

    def test_unticking_resets_the_schedule(self):
        self.log(outcome="cold", confidence=4)
        self.client.post(reverse("prep_progress_set"), json.dumps({"id": self.pid, "solved": False}), content_type="application/json")
        row = ProblemProgress.objects.filter(problem_id=self.pid).first()
        self.assertTrue(row is None or (not row.solved and row.next_review is None))


class PlanTests(SeededTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("s", "s@example.com", "x")
        self.client.force_login(self.user)

    def plan(self):
        return self.client.get(reverse("prep_next")).json()

    def test_new_student_gets_five_problems_from_five_patterns(self):
        plan = self.plan()
        self.assertEqual(len(plan["next"]), 5)
        self.assertEqual(len({n["pattern"] for n in plan["next"]}), 5)
        self.assertEqual(plan["reviews"], [])
        self.assertFalse(plan["placement"]["taken"])
        self.assertGreaterEqual(sum(n["difficulty"] <= 1 for n in plan["next"]), 4)   # mostly easy first

    def test_due_reviews_appear_when_the_date_arrives(self):
        from datetime import timedelta
        from django.utils import timezone
        pid = sorted(problem_ids())[0]
        ProblemProgress.objects.create(user=self.user, problem_id=pid, solved=True, stage=1, next_review=timezone.localdate() - timedelta(days=2), note="insight")
        (r,) = self.plan()["reviews"]
        self.assertEqual((r["id"], r["overdue"], r["note"]), (pid, 2, "insight"))

    def test_binge_guard_rotates_a_pattern_out(self):
        from django.utils import timezone
        from .catalog import catalog
        cat = catalog()
        name = "Sliding Window"
        ids = [cat["problems"][i]["id"] for i in cat["by_pattern"][name][:3]]
        for k, pid in enumerate(ids):
            ProblemProgress.objects.create(user=self.user, problem_id=pid, solved=True, solved_at=timezone.now(), stage=1)
        plan = self.plan()
        self.assertNotIn(name, [n["pattern"] for n in plan["next"]])
        self.assertIn(name, plan["rotated"])

    def test_solved_problems_are_never_suggested_again(self):
        first = self.plan()["next"][0]["id"]
        ProblemProgress.objects.create(user=self.user, problem_id=first, solved=True, stage=1)
        self.assertNotIn(first, [n["id"] for n in self.plan()["next"]])


class PlacementTests(SeededTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("s", "s@example.com", "x")
        self.client.force_login(self.user)

    def test_questions_do_not_leak_answers(self):
        qs = self.client.get(reverse("prep_placement_questions")).json()["questions"]
        self.assertGreaterEqual(len(qs), 15)
        self.assertTrue(all(set(q) == {"id", "q", "options"} for q in qs))

    def test_perfect_and_empty_submissions(self):
        from .services import placement_questions
        perfect = {q["id"]: q["answer"] for q in placement_questions()}
        res = self.client.post(reverse("prep_placement_submit"), json.dumps({"answers": perfect}), content_type="application/json").json()
        self.assertEqual((res["score"], res["level"]), (res["total"], "advanced"))
        res = self.client.post(reverse("prep_placement_submit"), json.dumps({"answers": {}}), content_type="application/json").json()
        self.assertEqual((res["score"], res["level"]), (0, "beginner"))
        self.assertEqual(PrepProfile.objects.count(), 1)                   # retaking replaces the result

    def test_familiar_patterns_get_credit_so_weak_ones_come_first(self):
        from .services import placement_questions
        qs = placement_questions()
        answers = {q["id"]: q["answer"] for q in qs if q["pattern"] == "Hash Map"}     # only Hash Map is known
        self.client.post(reverse("prep_placement_submit"), json.dumps({"answers": answers}), content_type="application/json")
        plan = self.client.get(reverse("prep_next")).json()
        row = next(r for r in plan["patterns"] if r["name"] == "Hash Map")
        self.assertTrue(row["familiar"])
        self.assertNotEqual(plan["next"][0]["pattern"], "Hash Map")        # explore the unfamiliar ones first


def _json(name):
    return json.loads((DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))


class SeedTests(SeededTestCase):
    def test_database_content_matches_the_seed_files(self):
        self.assertEqual(json.loads(catalog_module.catalog_json()), _json("catalog"))
        self.assertEqual(catalog_module.pattern_guides(), _json("pattern_guides"))
        self.assertEqual(catalog_module.placement_questions(), _json("placement"))

    def test_seeding_twice_changes_nothing(self):
        counts = (CatalogProblem.objects.count(), PatternGuide.objects.count(), PlacementQuestion.objects.count())
        report = seed_prep()
        self.assertTrue(all(c == u == d == 0 for c, u, d in report.values()), report)
        self.assertEqual(counts, (CatalogProblem.objects.count(), PatternGuide.objects.count(), PlacementQuestion.objects.count()))

    def test_seed_repairs_edits_and_removes_stale_rows(self):
        CatalogProblem.objects.filter(pid=self.pid()).update(title="edited")
        CatalogProblem.objects.create(position=99999, pid="x:gone", title="gone", platform="x")
        report = seed_prep()
        self.assertEqual((report["problems"][1], report["problems"][2]), (1, 1))
        self.assertNotEqual(CatalogProblem.objects.get(pid=self.pid()).title, "edited")

    def pid(self):
        return sorted(problem_ids())[0]

    def test_admin_edit_shows_up_in_the_catalog(self):
        row = CatalogProblem.objects.get(pid=self.pid())
        catalog_module.catalog()                       # warm the cache
        row.title = "Renamed in admin"
        row.save()
        cat = catalog_module.catalog()
        self.assertEqual(cat["problems"][cat["by_id"][row.pid]]["t"], "Renamed in admin")

    def test_data_endpoint_serves_the_database_content(self):
        user = get_user_model().objects.create_user("d", "d@example.com", "x")
        self.client.force_login(user)
        res = self.client.get(reverse("prep_data", args=["catalog"]))
        self.assertEqual(res["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(json.loads(res.content), _json("catalog"))
        self.assertEqual(self.client.get(reverse("prep_data", args=["pattern_guides"])).json(), _json("pattern_guides"))
