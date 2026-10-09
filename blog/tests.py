import tempfile
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import Post, Tag
from .render import parse_post, render_body, repair_code_blocks

POST = """---
layout: post
title: 'Redis Lists Explained'
date: 2024-12-26 06:54:45+00:00
category: Redis
tags:
- Redis
- Data Structures
---

<p class="wp-block-paragraph">Lists keep order. See [[Redis Sets]] and [[Unknown Post]]. Code: <code>x = [[1, 2]]</code></p>

## Related Posts
- [[Redis Sets]]
- [[Missing One]]
"""


def write_vault(root: Path):
    (root / "Redis").mkdir()
    (root / "Redis" / "redis-lists-explained.md").write_text(POST)
    (root / "Redis" / "redis-sets.md").write_text(POST.replace("Redis Lists Explained", "Redis Sets")
                                                  .replace("2024-12-26", "2024-12-27"))
    (root / "Today.md").write_text("# just a note, no frontmatter\n")
    (root / "Templates").mkdir()
    (root / "Templates" / "Post Template.md").write_text('---\nlayout: post\ntitle: "{{title}}"\ndate: 2024-01-01\n---\nx')


class RenderTests(TestCase):
    def test_parse_skips_notes_and_extracts_related(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_vault(root)
            post = parse_post(root / "Redis" / "redis-lists-explained.md")
            self.assertEqual(post.slug, "redis-lists-explained")
            self.assertEqual(post.tags, ["Redis", "Data Structures"])
            self.assertEqual(post.related_titles, ["Redis Sets", "Missing One"])
            self.assertNotIn("Related Posts", post.body)
            self.assertIsNone(parse_post(root / "Today.md"))

    def test_wikilinks_resolve_but_code_is_untouched(self):
        html = render_body("See [[Redis Sets]] and [[Nope|alias]]. `[[1, 2]]`\n\n<pre>m = [[3]]</pre>",
                           lambda t: "/blog/redis-sets/" if t == "Redis Sets" else None)
        self.assertIn('<a href="/blog/redis-sets/" rel="noopener noreferrer">Redis Sets</a>', html)
        self.assertIn("alias", html)
        self.assertIn("[[1, 2]]", html)
        self.assertIn("m = [[3]]", html)

    def test_code_with_blank_lines_and_hash_comments_stays_code(self):
        html = render_body('<p>Intro</p><pre>import os\n\n# not a heading\nx = 1</pre><p>After</p>', lambda t: None)
        self.assertNotIn("<h1>", html)
        self.assertIn("<pre>import os\n\n# not a heading\nx = 1</pre>", html)
        self.assertIn("<p>After</p>", html)

    def test_sanitiser_strips_scripts_and_handlers(self):
        html = render_body(
            '<p onclick="steal()">Hi<script>alert(1)</script></p><a href="javascript:alert(1)">x</a>'
            '<img src="https://e.com/a.png" onerror="x()">', lambda t: None)
        for bad in ("<script", "onclick", "onerror", "javascript:"):
            self.assertNotIn(bad, html)
        self.assertIn('src="https://e.com/a.png"', html)

    def test_only_youtube_iframes_survive_on_nocookie_domain(self):
        html = render_body(
            '<iframe src="https://www.youtube.com/embed/nXgUBanjZP8?feature=oembed"></iframe>'
            '<iframe src="https://evil.example/x"></iframe>', lambda t: None)
        self.assertIn('src="https://www.youtube-nocookie.com/embed/nXgUBanjZP8"', html)
        self.assertNotIn("evil.example", html)
        self.assertIn('class="video-embed"', html)

    def test_code_repair_matches_by_content(self):
        broken = "<p>a</p><pre>import os# commentx = 1</pre><pre>echo hi</pre>"
        fixed, n = repair_code_blocks(broken, ["unrelated\ncode", "import os\n\n# comment\nx = 1"])
        self.assertEqual(n, 1)
        self.assertIn("<pre>import os\n\n# comment\nx = 1</pre>", fixed)
        self.assertIn("<pre>echo hi</pre>", fixed)


@override_settings(BLOG_WORDPRESS_URL="")
class ImportTests(TestCase):
    def test_import_and_prune(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_vault(root)
            out = StringIO()
            call_command("import_blog", str(root), stdout=out)
            self.assertIn("Imported 2 posts", out.getvalue())
            post = Post.objects.get(slug="redis-lists-explained")
            self.assertEqual(post.related_slugs, ["redis-sets"])
            self.assertIn('href="/blog/redis-sets/"', post.body_html)
            self.assertEqual(set(post.tags.values_list("slug", flat=True)), {"redis", "data-structures"})
            self.assertEqual(post.category_slug, "redis")

            (root / "Redis" / "redis-sets.md").unlink()
            call_command("import_blog", str(root), "--prune", stdout=StringIO())
            self.assertEqual(list(Post.objects.values_list("slug", flat=True)), ["redis-lists-explained"])


class BlogViewTests(TestCase):
    def setUp(self):
        cache.clear()  # public blog pages are cached for 60 s (courses/cache.py)
        def make(slug, title, day, category="Redis", **kw):
            return Post.objects.create(slug=slug, title=title, category=category, category_slug=category.lower(),
                                       published_at=datetime(2025, 1, day, tzinfo=timezone.utc),
                                       body_html="<p>Body</p>", excerpt=f"About {title}", source_path=f"{slug}.md", **kw)
        self.a = make("redis-lists", "Redis Lists", 1, related_slugs=["docker-volumes"],
                      wordpress_url="https://parottasalna.com/2025/01/01/redis-lists/")
        self.b = make("docker-volumes", "Docker Volumes", 2, category="Docker")
        self.hidden = make("draft-post", "Draft", 3, is_published=False)
        self.a.tags.add(Tag.objects.create(name="Caching", slug="caching"))

    def test_index_is_public_with_filters(self):
        response = self.client.get("/blog/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Docker Volumes")
        self.assertNotContains(response, "Draft")
        self.assertNotContains(self.client.get("/blog/?category=docker"), "Redis Lists")
        self.assertContains(self.client.get("/blog/?q=volumes"), "Docker Volumes")
        self.assertNotContains(self.client.get("/blog/?tag=caching"), "Docker Volumes")

    def test_post_page_seo_and_related(self):
        response = self.client.get("/blog/redis-lists/")
        self.assertContains(response, '<link rel="canonical" href="https://parottasalna.com/2025/01/01/redis-lists/">')
        self.assertContains(response, '"@type": "BlogPosting"')
        self.assertContains(response, 'content="article"')
        self.assertEqual([p.slug for p in response.context["related"]], ["docker-volumes"])
        self.assertEqual(self.client.get("/blog/draft-post/").status_code, 404)

    @override_settings(BLOG_CANONICAL_TO_WORDPRESS=False)
    def test_self_canonical_when_wordpress_retired(self):
        self.assertContains(self.client.get("/blog/redis-lists/"),
                            '<link rel="canonical" href="http://testserver/blog/redis-lists/">')

    def test_feed_sitemap_and_nav(self):
        feed = self.client.get("/blog/feed.xml")
        self.assertEqual(feed.status_code, 200)
        self.assertIn(b"Docker Volumes", feed.content)
        self.assertNotIn(b"Draft", feed.content)
        sitemap = self.client.get("/sitemap.xml").content.decode()
        self.assertIn("<loc>http://testserver/blog/redis-lists/</loc>", sitemap)
        self.assertNotIn("draft-post", sitemap)
        self.assertContains(self.client.get("/"), 'href="/blog/"')


WP_POST = """---
layout: post
title: 'Lazy Queues | RabbitMQ'
date: 2024-12-26 06:54:45+00:00
category: RabbitMQ
---

<p>Intro <img src="https://i0.wp.com/cdn.hashnode.com/res/up/v1/Abc.png?w=800"/> <a href="https://parottasalna.com/wp-content/uploads/2024/07/sheet.pdf">PDF</a></p><figure><a href="https://parottasalna.com/wp-content/uploads/2024/08/q.png"><img src="https://i0.wp.com/parottasalna.com/wp-content/uploads/2024/08/q.png?resize=756%2C515&amp;ssl=1" srcset="https://i0.wp.com/x.png 300w" alt="queue"/></a></figure><pre>import pika# connectx = 1</pre><p>Home <a href="https://parottasalna.com/">blog</a>, <a href="https://parottasalna.com/redis-sets#heading-x">old style</a>. See <a href="https://parottasalna.com/2024/12/27/redis-sets/">the sets post</a> and <a href="https://parottasalna.com/2023/01/01/not-in-vault/">old one</a>.</p>
"""

SETS_POST = """---
layout: post
title: Redis Sets
date: 2024-12-27 06:54:45+00:00
---

<p>Sets ![[diagram.png|Set diagram]] done.</p>
"""


class LocalizeVaultTests(TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "RabbitMQ").mkdir()
        (self.root / "RabbitMQ" / "lazy-queues.md").write_text(WP_POST)
        (self.root / "redis-sets.md").write_text(SETS_POST)
        (self.root / "pics").mkdir()
        (self.root / "pics" / "diagram.png").write_bytes(b"\x89PNG local")
        (self.root / "Private.md").write_text("no frontmatter")
        (self.root / "secret.png").write_bytes(b"\x89PNG secret")
        self.wordpress = {"lazy-queues": {"link": "https://parottasalna.com/2024/12/26/lazy-queues/",
                                          "pres": ["import pika\n\n# connect\nx = 1"]}}
        self.downloads = []

    def download(self, url):
        self.downloads.append(url)
        return b"\x89PNG from wordpress"

    def localize(self, dry_run=False):
        from .vault import localize_vault

        return localize_vault(self.root, "https://parottasalna.com", self.wordpress, self.download,
                              dry_run=dry_run, log=lambda *a: None)

    def test_dry_run_writes_nothing(self):
        before = (self.root / "RabbitMQ" / "lazy-queues.md").read_text()
        report = self.localize(dry_run=True)
        self.assertEqual(report.files_changed, 1)
        self.assertEqual((self.root / "RabbitMQ" / "lazy-queues.md").read_text(), before)
        self.assertFalse((self.root / "attachments").exists())
        self.assertEqual(self.downloads, [])

    def test_localizes_code_images_and_links_then_is_idempotent(self):
        report = self.localize()
        text = (self.root / "RabbitMQ" / "lazy-queues.md").read_text()
        self.assertEqual((report.code_blocks, report.images_downloaded, report.links_relinked,
                          report.external_post_links), (1, 3, 1, 1))
        self.assertIn("https://cdn.hashnode.com/res/up/v1/Abc.png", self.downloads)       # original, not the proxy
        self.assertRegex(text, r'src="\.\./attachments/external/[0-9a-f]{10}-Abc\.png"')
        self.assertIn('href="../attachments/2024/07/sheet.pdf"', text)
        self.assertEqual((self.root / "attachments" / "2024" / "08" / "q.png").read_bytes(), b"\x89PNG from wordpress")
        self.assertIn('src="../attachments/2024/08/q.png"', text)
        self.assertIn('href="../attachments/2024/08/q.png"', text)
        self.assertNotIn("srcset", text)
        self.assertNotIn("i0.wp.com", text)
        self.assertIn("<pre>import pika\n\n# connect\nx = 1</pre>", text)
        self.assertIn("[[Redis Sets|the sets post]]", text)
        self.assertIn("https://parottasalna.com/2023/01/01/not-in-vault/", text)      # unknown post: kept
        self.assertEqual(self.localize().files_changed, 0)                              # second run: no-op
        self.assertEqual(len(self.downloads), 3)

    def test_blog_works_without_wordpress_after_localizing(self):
        self.localize()
        with override_settings(BLOG_SRC_ROOT=self.root, BLOG_WORDPRESS_URL=""):
            call_command("import_blog", str(self.root), stdout=StringIO(), stderr=StringIO())
            lazy = Post.objects.get(slug="lazy-queues")
            self.assertIn('src="/blog/media/attachments/2024/08/q.png"', lazy.body_html)
            self.assertIn('href="/blog/redis-sets/"', lazy.body_html)
            self.assertIn('href="/blog/media/attachments/2024/07/sheet.pdf"', lazy.body_html)
            self.assertRegex(lazy.body_html, r'href="/blog/"[^>]*>blog</a>')
            self.assertRegex(lazy.body_html, r'href="/blog/redis-sets/"[^>]*>old style</a>')
            self.assertEqual(self.client.get("/blog/media/attachments/2024/07/sheet.pdf")["Content-Type"], "application/pdf")
            self.assertIn("# connect\nx = 1", lazy.body_html)
            self.assertNotIn("wp.com", lazy.body_html)
            sets = Post.objects.get(slug="redis-sets")
            self.assertIn('<img loading="lazy" src="/blog/media/pics/diagram.png" alt="Set diagram">', sets.body_html)

            image = self.client.get("/blog/media/attachments/2024/08/q.png")
            self.assertEqual(image.status_code, 200)
            self.assertEqual(b"".join(image.streaming_content), b"\x89PNG from wordpress")
            self.assertEqual(image["Content-Type"], "image/png")
            for blocked in ("secret.png", "Private.md", "RabbitMQ/lazy-queues.md", "../etc/passwd",
                            "attachments/../secret.png"):
                self.assertEqual(self.client.get(f"/blog/media/{blocked}").status_code, 404, blocked)

            Post.objects.filter(slug="lazy-queues").update(is_published=False)
            self.assertEqual(self.client.get("/blog/media/attachments/2024/08/q.png").status_code, 404)

    def test_canonical_is_self_without_wordpress_even_with_stored_url(self):
        post = Post.objects.create(slug="p", title="P", published_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
                                   body_html="<p>x</p>", source_path="p.md",
                                   wordpress_url="https://parottasalna.com/2025/01/01/p/")
        with override_settings(BLOG_WORDPRESS_URL=""):
            response = self.client.get("/blog/p/")
        self.assertContains(response, '<link rel="canonical" href="http://testserver/blog/p/">')
        self.assertNotContains(response, "Originally published")
        post.refresh_from_db()


class BlogCacheTests(TestCase):
    def setUp(self):
        cache.clear()
        self.post = Post.objects.create(slug="p", title="First title", category="Redis", category_slug="redis",
                                        published_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
                                        body_html="<p>Body</p>", excerpt="x", source_path="p.md")

    def test_anonymous_copy_is_cached_but_signed_in_and_search_are_fresh(self):
        from django.contrib.auth import get_user_model

        self.assertContains(self.client.get("/blog/p/"), "First title")
        Post.objects.filter(pk=self.post.pk).update(title="Second title")
        self.assertContains(self.client.get("/blog/p/"), "First title")  # cached for anonymous visitors
        self.assertContains(self.client.get("/blog/?q=Second"), "Second title")  # search is never cached
        user = get_user_model().objects.create_user("u", email="u@gmail.com")
        self.client.force_login(user, backend="django.contrib.auth.backends.ModelBackend")
        response = self.client.get("/blog/p/")
        self.assertContains(response, "Second title")
        self.assertContains(response, "csrfmiddlewaretoken")  # signed-in pages carry a logout form
        cache.clear()
        self.client.logout()
        self.assertContains(self.client.get("/blog/p/"), "Second title")

    def test_cached_pages_never_contain_a_csrf_token(self):
        self.client.get("/blog/")
        self.assertNotContains(self.client.get("/blog/"), "csrfmiddlewaretoken")
