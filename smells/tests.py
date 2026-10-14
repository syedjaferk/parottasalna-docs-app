import datetime
import json
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from .models import CodeSmell, SmellAnswer
from .services import smell_for

User = get_user_model()
BACKEND = "django.contrib.auth.backends.ModelBackend"


class SmellTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("load_smells", stdout=StringIO())
        cls.user = User.objects.create_user("stu", email="stu@gmail.com")

    def test_dataset_is_valid(self):
        self.assertGreaterEqual(CodeSmell.objects.count(), 30)
        for smell in CodeSmell.objects.select_related("quiz"):
            smell.quiz.clean()

    def test_load_is_idempotent_and_dump_round_trips(self):
        call_command("load_smells", stdout=StringIO())
        out = StringIO()
        call_command("dump_smells", stdout=out)
        data = json.loads(out.getvalue())
        self.assertEqual(len(data["code_smells"]), CodeSmell.objects.count())
        CodeSmell.objects.all().delete()
        path = self._tmp(out.getvalue())
        call_command("load_smells", path, stdout=StringIO())
        self.assertEqual(CodeSmell.objects.count(), len(data["code_smells"]))

    def _tmp(self, text):
        import tempfile
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        f.write(text)
        f.close()
        return f.name

    def test_rotation_changes_daily_and_cycles(self):
        a = smell_for(datetime.date(2026, 3, 1))
        b = smell_for(datetime.date(2026, 3, 2))
        self.assertNotEqual(a.pk, b.pk)
        n = CodeSmell.objects.count()
        self.assertEqual(a.pk, smell_for(datetime.date(2026, 3, 1) + datetime.timedelta(days=n)).pk)

    def test_api_requires_login(self):
        self.assertEqual(self.client.get("/smells/today.json").status_code, 401)
        self.assertEqual(self.client.post("/smells/answer/", {}).status_code, 401)

    def test_today_hides_answer_and_answer_is_recorded_once(self):
        self.client.force_login(self.user, backend=BACKEND)
        today = self.client.get("/smells/today.json").json()["smell"]
        self.assertNotIn("answer", today["quiz"])
        smell = CodeSmell.objects.get(slug=today["slug"])
        right = smell.quiz.answer
        wrong = (right + 1) % len(smell.quiz.choices)
        r = self.client.post("/smells/answer/", {"slug": smell.slug, "choice": wrong}).json()
        self.assertFalse(r["correct"])
        self.assertEqual(r["answer"], right)
        r = self.client.post("/smells/answer/", {"slug": smell.slug, "choice": right}).json()
        self.assertTrue(r["already_answered"])
        self.assertFalse(r["correct"])  # first answer stands
        self.assertEqual(SmellAnswer.objects.filter(user=self.user).count(), 1)

    def test_rejects_other_days_and_bad_choices(self):
        self.client.force_login(self.user, backend=BACKEND)
        today = self.client.get("/smells/today.json").json()["smell"]
        other = CodeSmell.objects.exclude(slug=today["slug"]).first()
        self.assertEqual(self.client.post("/smells/answer/", {"slug": other.slug, "choice": 0}).status_code, 404)
        self.assertEqual(self.client.post("/smells/answer/", {"slug": today["slug"], "choice": 99}).status_code, 400)
        self.assertEqual(self.client.post("/smells/answer/", {"slug": today["slug"], "choice": "x"}).status_code, 400)

    def test_dashboard_shows_card(self):
        self.client.force_login(self.user, backend=BACKEND)
        html = self.client.get("/").content.decode()
        self.assertIn("Code smell of the day", html)
