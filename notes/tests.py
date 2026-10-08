import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from courses.models import Course, Enrollment

from .models import Note

User = get_user_model()
MODEL_BACKEND = "django.contrib.auth.backends.ModelBackend"


class NotesTestCase(TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        override = override_settings(DOCS_BUILD_ROOT=root)
        override.enable()
        self.addCleanup(override.disable)
        for slug in ("c1", "open"):
            html = root / slug / "html" / "sub"
            html.mkdir(parents=True)
            (html.parent / "index.html").write_text("<title>Welcome - C1 | Brand</title>")
            (html.parent / "intro.html").write_text("<title>Intro &amp; setup - C1 | Brand</title>")
            (html / "part.html").write_text("<title>Part two - C1 | Brand</title>")
        self.course = Course.objects.create(slug="c1", title="C1", build_status="ok")
        self.common = Course.objects.create(slug="open", title="Open", is_common=True, build_status="ok")
        Enrollment.objects.create(course=self.course, email="stu@gmail.com")
        Enrollment.objects.create(course=self.course, email="two@gmail.com")
        self.student = User.objects.create_user("stu", email="stu@gmail.com")
        self.other = User.objects.create_user("two", email="two@gmail.com")
        self.reader = User.objects.create_user("reader", email="reader@gmail.com")  # no enrolments
        self.client = self.client_class(enforce_csrf_checks=True)

    def login(self, user):
        self.client.force_login(user, backend=MODEL_BACKEND)

    def feed(self, slug="c1", page="intro"):
        return self.client.get(f"/courses/{slug}/notes.json", {"page": page})

    def post(self, url, data, slug="c1"):
        token = self.feed(slug).cookies.get("csrftoken")
        return self.client.post(url, data, HTTP_X_CSRFTOKEN=token.value if token else "")

    def create(self, slug="c1", **data):
        fields = {"page": "intro", "anchor": "setup", "quote": "Docker runs containers", "body": "Remember this"}
        fields.update(data)
        return self.post(f"/courses/{slug}/notes/new/", fields, slug=slug)


class NoteApiTests(NotesTestCase):
    def test_create_list_update_delete(self):
        self.login(self.student)
        response = self.create()
        self.assertEqual(response.status_code, 201)
        note_id = response.json()["id"]
        data = self.feed().json()
        self.assertTrue(data["enabled"])
        self.assertEqual([n["body"] for n in data["notes"]], ["Remember this"])
        self.assertEqual(data["notes"][0]["quote"], "Docker runs containers")
        self.assertEqual(data["course_count"], 1)
        self.assertEqual(self.feed(page="sub/part").json()["notes"], [])
        self.assertEqual(self.post(f"/courses/c1/notes/{note_id}/", {"body": "Edited"}).json()["body"], "Edited")
        self.assertEqual(self.post(f"/courses/c1/notes/{note_id}/delete/", {}).status_code, 200)
        self.assertFalse(Note.objects.exists())

    def test_notes_on_the_landing_page_are_allowed(self):
        self.login(self.student)
        self.assertEqual(self.create(page="index", anchor="").status_code, 201)

    def test_validation(self):
        self.login(self.student)
        for bad in ({"page": "nope"}, {"page": "../secret"}, {"anchor": "a b<script>"}, {"body": "   "},
                    {"body": "x" * 10001}):
            self.assertEqual(self.create(**bad).status_code, 400, bad)
        long_quote = self.create(quote="q" * 5000)
        self.assertEqual(len(long_quote.json()["quote"]), 1000)

    def test_other_students_notes_are_invisible_and_untouchable(self):
        self.login(self.student)
        note_id = self.create().json()["id"]
        self.login(self.other)
        self.assertEqual(self.feed().json()["notes"], [])
        self.assertEqual(self.post(f"/courses/c1/notes/{note_id}/", {"body": "hacked"}).status_code, 404)
        self.assertEqual(self.post(f"/courses/c1/notes/{note_id}/delete/", {}).status_code, 404)
        self.assertEqual(Note.objects.get(pk=note_id).body, "Remember this")
        # The same id through another course is not found either.
        self.login(self.student)
        Enrollment.objects.create(course=self.common, email="stu@gmail.com")
        self.assertEqual(self.post(f"/courses/open/notes/{note_id}/delete/", {}, slug="open").status_code, 404)

    def test_not_enrolled_readers_get_no_notes_and_store_nothing(self):
        self.login(self.reader)
        self.assertEqual(self.feed("open").json(), {"enabled": False})
        self.assertEqual(self.create(slug="open").status_code, 404)
        self.assertEqual(self.feed("c1").status_code, 404)  # can't even read this course
        self.client.logout()
        self.assertEqual(self.feed("open").json(), {"enabled": False})
        self.assertEqual(self.client.post("/courses/open/notes/new/", {}).status_code, 403)  # CSRF first
        self.assertFalse(Note.objects.exists())

    def test_writes_need_csrf_and_login_and_responses_are_not_cached(self):
        self.login(self.student)
        self.assertEqual(self.client.post("/courses/c1/notes/new/", {"page": "intro", "body": "x"}).status_code, 403)
        self.assertIn("no-store", self.feed()["Cache-Control"])
        self.client.logout()
        self.assertEqual(self.create().status_code, 401)

    def test_staff_can_keep_notes(self):
        staff = User.objects.create_user("adm", email="adm@gmail.com", is_staff=True)
        self.login(staff)
        self.assertEqual(self.create().status_code, 201)


class MyNotesPageTests(NotesTestCase):
    def setUp(self):
        super().setUp()
        Note.objects.create(user=self.student, course=self.course, page="sub/part", body="Second **bold**")
        Note.objects.create(user=self.student, course=self.course, page="intro", anchor="setup",
                            quote="a quoted line", body="First <script>alert(1)</script>")
        Note.objects.create(user=self.other, course=self.course, page="intro", body="Someone else's note")

    def test_page_groups_in_course_order_and_escapes_html(self):
        self.login(self.student)
        response = self.client.get("/courses/c1/notes/")
        html = response.content.decode()
        self.assertContains(response, "2 notes")
        self.assertLess(html.index("Intro &amp; setup"), html.index("Part two"))
        self.assertIn("<strong>bold</strong>", html)
        self.assertNotIn("<script>alert(1)", html)
        self.assertNotIn("Someone else", html)
        self.assertIn("/courses/c1/docs/intro.html#setup", html)

    def test_markdown_export(self):
        self.login(self.student)
        response = self.client.get("/courses/c1/notes.md")
        self.assertEqual(response["Content-Disposition"], 'attachment; filename="notes-c1.md"')
        text = response.content.decode()
        self.assertIn("## Intro & setup", text)
        self.assertIn("> a quoted line", text)
        self.assertNotIn("Someone else", text)

    def test_only_trackable_users_see_the_page(self):
        self.login(self.reader)
        self.assertEqual(self.client.get("/courses/c1/notes/").status_code, 404)
        self.assertEqual(self.client.get("/courses/open/notes/").status_code, 404)
        self.client.logout()
        self.assertEqual(self.client.get("/courses/c1/notes/").status_code, 302)  # to sign-in
