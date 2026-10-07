import tempfile
from pathlib import Path
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.test import RequestFactory, TestCase, override_settings

from .adapters import PortalAccountAdapter, PortalSocialAccountAdapter
from .models import Course, Enrollment
from .services import accessible_courses, parse_emails

User = get_user_model()
MODEL_BACKEND = "django.contrib.auth.backends.ModelBackend"


def fake_login(email, verified=True):
    return SimpleNamespace(
        email_addresses=[SimpleNamespace(email=email, verified=verified)], is_existing=False
    )


class ParseEmailsTests(TestCase):
    def test_splits_lowercases_dedupes_and_flags_invalid(self):
        valid, invalid = parse_emails("A@gmail.com, b@gmail.com;\n a@GMAIL.com  nope")
        self.assertEqual(valid, ["a@gmail.com", "b@gmail.com"])
        self.assertEqual(invalid, ["nope"])


class AdapterTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(slug="c1", title="C1")
        Enrollment.objects.create(course=self.course, email="Student@Gmail.com")
        self.adapter = PortalSocialAccountAdapter()
        self.request = RequestFactory().get("/")

    def test_enrolled_verified_email_may_sign_up(self):
        self.assertTrue(self.adapter.is_open_for_signup(self.request, fake_login("student@gmail.com")))

    def test_unknown_email_is_rejected(self):
        self.assertFalse(self.adapter.is_open_for_signup(self.request, fake_login("who@gmail.com")))

    def test_unverified_email_is_rejected(self):
        self.assertFalse(
            self.adapter.is_open_for_signup(self.request, fake_login("student@gmail.com", False))
        )

    def test_local_signup_is_closed(self):
        self.assertFalse(PortalAccountAdapter().is_open_for_signup(self.request))


class LinkingTests(TestCase):
    def test_login_links_enrollment_to_user(self):
        course = Course.objects.create(slug="c1", title="C1")
        enrollment = Enrollment.objects.create(course=course, email="s@gmail.com")
        user = User.objects.create_user("s", email="S@gmail.com")
        user_logged_in.send(sender=User, request=None, user=user)
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.user, user)


class DocsAccessTests(TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.override = override_settings(DOCS_BUILD_ROOT=root, USE_X_ACCEL_REDIRECT=False)
        self.override.enable()
        self.addCleanup(self.override.disable)

        html = root / "c1" / "html"
        (html / "_static").mkdir(parents=True)
        (html / "index.html").write_text("<h1>Hello</h1>")
        (html / "_static" / "site.css").write_text("body{}")
        (html / ".buildinfo").write_text("secret")
        (root / "secret.txt").write_text("top secret")

        self.course = Course.objects.create(slug="c1", title="C1", build_status="ok")
        self.student = User.objects.create_user("stu", email="stu@gmail.com")
        self.outsider = User.objects.create_user("out", email="out@gmail.com")
        self.staff = User.objects.create_user("adm", email="adm@gmail.com", is_staff=True)
        Enrollment.objects.create(course=self.course, email="STU@gmail.com")

    def get(self, user, path="/courses/c1/docs/"):
        if user:
            self.client.force_login(user, backend=MODEL_BACKEND)
        return self.client.get(path)

    def test_anonymous_is_redirected_to_login(self):
        response = self.get(None)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_enrolled_user_gets_index_and_assets(self):
        response = self.get(self.student)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"<h1>Hello</h1>")
        css = self.client.get("/courses/c1/docs/_static/site.css")
        self.assertEqual(css.status_code, 200)
        self.assertEqual(css["Content-Type"], "text/css")

    def test_non_enrolled_user_gets_404(self):
        self.assertEqual(self.get(self.outsider).status_code, 404)

    def test_staff_can_open_any_course(self):
        self.assertEqual(self.get(self.staff).status_code, 200)

    def test_inactive_course_is_hidden(self):
        Course.objects.filter(pk=self.course.pk).update(is_active=False)
        self.assertEqual(self.get(self.student).status_code, 404)

    def test_path_traversal_is_blocked(self):
        self.assertEqual(self.get(self.student, "/courses/c1/docs/../../secret.txt").status_code, 404)

    def test_dotfiles_are_blocked(self):
        self.assertEqual(self.get(self.student, "/courses/c1/docs/.buildinfo").status_code, 404)

    @override_settings(USE_X_ACCEL_REDIRECT=True)
    def test_x_accel_header_is_set(self):
        response = self.get(self.student)
        self.assertEqual(response["X-Accel-Redirect"], "/protected-docs/c1/html/index.html")

    def test_dashboard_lists_only_accessible_courses(self):
        other = Course.objects.create(slug="c2", title="C2")
        titles = set(accessible_courses(self.student).values_list("slug", flat=True))
        self.assertEqual(titles, {"c1"})
        self.assertNotIn(other.slug, titles)


class BrandSeoTests(TestCase):
    def test_landing_page_is_public_and_indexable(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'content="index, follow')
        self.assertContains(response, '<link rel="canonical" href="http://testserver/">')
        self.assertContains(response, 'property="og:image" content="http://testserver/static/brand/og-image.png"')
        self.assertContains(response, '"@type": "EducationalOrganization"')
        self.assertContains(response, "https://www.youtube.com/@parottasalnatech")

    def test_private_pages_are_noindex(self):
        user = User.objects.create_user("s", email="s@gmail.com")
        self.client.force_login(user, backend=MODEL_BACKEND)
        response = self.client.get("/")
        self.assertContains(response, 'content="noindex, follow"')
        self.assertContains(response, "Parottasalna")

    def test_robots_and_sitemap(self):
        robots = self.client.get("/robots.txt")
        self.assertEqual(robots["Content-Type"], "text/plain")
        self.assertIn(b"Disallow: /courses/", robots.content)
        self.assertIn(b"Sitemap: http://testserver/sitemap.xml", robots.content)
        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap["Content-Type"], "application/xml")
        self.assertIn(b"<loc>http://testserver/</loc>", sitemap.content)

    def test_json_ld_cannot_break_out_of_script(self):
        from .branding import json_ld

        self.assertNotIn("<", json_ld("http://x/</script>"))
