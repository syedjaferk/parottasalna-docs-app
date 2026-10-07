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


class GitBookImportTests(TestCase):
    def test_summary_groups_nesting_and_external_links(self):
        from .gitbook import parse_summary

        groups = parse_summary(
            "# Table of contents\n\n* [Intro](README.md)\n  * [Child](a/child.md)\n* [Why on\\_start](b.md)\n\n"
            "## Tasks\n\n* [Task 1](t1.md)\n\n***\n\n* [Live](https://youtu.be/abcdefghijk)\n"
        )
        self.assertEqual([g.caption for g in groups], ["", "Tasks", ""])
        self.assertEqual(groups[0].entries[0].children[0].target, "a/child.md")
        self.assertEqual(groups[0].entries[1].title, "Why on_start")
        self.assertTrue(groups[2].entries[0].is_external)

    def test_page_conversion(self):
        from .gitbook import PageConverter

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gitbook" / "assets").mkdir(parents=True)
            (root / ".gitbook" / "assets" / "image (4).png").write_bytes(b"png")
            page = (
                "---\ndescription: Short intro\n---\n\n# Title <a href=\"#title\" id=\"title\"></a>\n\n"
                '<figure><img src="../.gitbook/assets/image (4).png" alt=""><figcaption></figcaption></figure>\n\n'
                '{% embed url="https://youtu.be/nXgUBanjZP8?si=x" %}\n\n'
                '{% tabs %}\n{% tab title="1. Question" %}\nAsk\n{% endtab %}\n'
                '{% tab title="Solution" %}\n```sql\nSELECT 1;\n```\n{% endtab %}\n{% endtabs %}\n\n'
                '<pre class="language-sql"><code class="lang-sql"><strong>SELECT a &#x26; b\n</strong>FROM t;\n</code></pre>\n\n'
                "See [intro](../README.md) and [gone](../gone.md).\n\n---\n"
            )
            converter = PageConverter(root, "sub/page.md", {"README.md": "introduction.md", "sub/page.md": "sub/page.md"})
            out = converter.convert(page)
        self.assertIn("# Title\n\n*Short intro*", out)
        self.assertIn("![](/_assets/image-4.png)", out)
        self.assertEqual(list(converter.assets), ["image-4.png"])
        self.assertIn("youtube-nocookie.com/embed/nXgUBanjZP8", out)
        self.assertIn("**1. Question**\n\nAsk", out)
        self.assertIn('<details class="solution">\n<summary>Solution</summary>', out)
        self.assertIn("```sql\nSELECT a & b\nFROM t;\n```", out)
        self.assertIn("[intro](../introduction.md)", out)
        self.assertIn("and gone.", out)
        self.assertFalse(out.rstrip().endswith("---"))

    def test_convert_space_writes_index_and_skips_empty_pages(self):
        from .gitbook import convert_space

        with tempfile.TemporaryDirectory() as tmp:
            src, out = Path(tmp) / "src", Path(tmp) / "out"
            (src / "a").mkdir(parents=True)
            (src / "README.md").write_text("# Intro\n\nHello")
            (src / "a" / "README.md").write_text("# Section\n\nText")
            (src / "a" / "child.md").write_text("# Child\n\nText")
            (src / "page.md").write_text("# Page\n")
            (src / "SUMMARY.md").write_text(
                "* [Intro](README.md)\n* [Section](a/README.md)\n  * [Child](a/child.md)\n* [Page](page.md)\n"
            )
            report = convert_space(src, out, title="My Course", description="About it")
            index = (out / "index.md").read_text()
            section = (out / "a" / "README.md").read_text()
        self.assertEqual(report["skipped"], ["page.md"])
        self.assertIn("# My Course\n\nAbout it", index)
        self.assertIn("Intro <introduction>", index)
        self.assertIn("Section <a/README>", index)
        self.assertIn("Child <child>", section)


class CommonCourseTests(TestCase):
    def setUp(self):
        self.batch = Course.objects.create(slug="batch", title="Batch Course")
        self.common = Course.objects.create(slug="common", title="Common Course", is_common=True)
        Enrollment.objects.create(course=self.batch, email="stu@gmail.com")
        self.student = User.objects.create_user("stu", email="stu@gmail.com")
        self.other = User.objects.create_user("other", email="other@gmail.com")

    def test_common_course_needs_no_enrollment(self):
        self.assertEqual(set(accessible_courses(self.other).values_list("slug", flat=True)), {"common"})
        self.assertEqual(
            set(accessible_courses(self.student).values_list("slug", flat=True)), {"batch", "common"}
        )

    def test_inactive_common_course_is_hidden(self):
        Course.objects.filter(pk=self.common.pk).update(is_active=False)
        self.assertFalse(accessible_courses(self.other).exists())

    def test_dashboard_separates_enrolled_and_common(self):
        self.client.force_login(self.student, backend=MODEL_BACKEND)
        response = self.client.get("/")
        self.assertEqual([c.slug for c in response.context["enrolled_courses"]], ["batch"])
        self.assertEqual([c.slug for c in response.context["common_courses"]], ["common"])
        self.assertContains(response, "My enrolled courses")
        self.assertContains(response, "Common courses")

    def test_common_course_does_not_open_signup(self):
        adapter = PortalSocialAccountAdapter()
        self.assertFalse(adapter.is_open_for_signup(RequestFactory().get("/"), fake_login("stranger@gmail.com")))


class PublicCommonCourseTests(TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.override = override_settings(DOCS_BUILD_ROOT=root, USE_X_ACCEL_REDIRECT=False)
        self.override.enable()
        self.addCleanup(self.override.disable)
        for slug in ("open", "batch"):
            (root / slug / "html" / "sub").mkdir(parents=True)
            (root / slug / "html" / "index.html").write_text("<h1>Index</h1>")
            (root / slug / "html" / "sub" / "page.html").write_text("<h1>Page</h1>")
            (root / slug / "html" / "search.html").write_text("search")
        Course.objects.create(slug="open", title="Open", is_common=True, build_status="ok")
        Course.objects.create(slug="batch", title="Batch", build_status="ok")

    def test_anonymous_can_read_common_docs(self):
        response = self.client.get("/courses/open/docs/sub/page.html")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"<h1>Page</h1>")

    def test_anonymous_still_redirected_for_enrolled_and_unknown_courses(self):
        for url in ("/courses/batch/docs/", "/courses/nope/docs/"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login/?next=", response["Location"])

    def test_anonymous_quiz_feed_for_common_course(self):
        data = self.client.get("/courses/open/quizzes.json").json()
        self.assertFalse(data["signed_in"])
        self.assertEqual(self.client.get("/courses/batch/quizzes.json").status_code, 404)

    def test_landing_lists_free_courses(self):
        response = self.client.get("/")
        self.assertContains(response, "Free courses")
        self.assertContains(response, 'href="/courses/open/docs/"')
        self.assertNotContains(response, "/courses/batch/docs/")

    def test_robots_and_sitemap_include_public_docs(self):
        robots = self.client.get("/robots.txt").content.decode()
        self.assertIn("Allow: /courses/open/docs/", robots)
        self.assertNotIn("Allow: /courses/batch/", robots)
        sitemap = self.client.get("/sitemap.xml").content.decode()
        self.assertIn("<loc>http://testserver/courses/open/docs/</loc>", sitemap)
        self.assertIn("<loc>http://testserver/courses/open/docs/sub/page.html</loc>", sitemap)
        self.assertNotIn("search.html", sitemap)
        self.assertNotIn("/courses/batch/", sitemap)
