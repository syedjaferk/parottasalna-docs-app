"""Import blog posts from the Obsidian vault.

    python manage.py import_blog                      # uses BLOG_SRC_ROOT
    python manage.py import_blog /path/to/second-brain --prune

Only notes with post frontmatter (layout: post, title, date) are imported. If BLOG_WORDPRESS_URL is
set, the live WordPress site is read once to (1) repair code blocks whose line breaks were lost in
the export and (2) remember each post's original URL for the canonical link.
"""
import html
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from blog.models import Post, PostAsset, Tag
from blog.vault import ASSET_EXTENSIONS, post_link_slug, wordpress_entry
from courses import branding
from blog.render import (
    excerpt_of,
    parse_post,
    reading_minutes,
    render_body,
    repair_code_blocks,
    wikilink_candidates,
)

SKIP_DIRS = {".git", ".obsidian", "Templates", "node_modules"}


def title_key(title: str) -> str:
    """Compare titles loosely: HTML entities decoded, case and punctuation ignored."""
    return re.sub(r"[^0-9a-z]+", "", html.unescape(title).casefold())


def wordpress_session() -> requests.Session:
    """HTTP session that retries brief network failures (DNS blips, timeouts, 5xx) with back-off."""
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    session = requests.Session()
    retry = Retry(total=4, backoff_factor=1.5, status_forcelist=(429, 500, 502, 503, 504), allowed_methods={"GET"})
    session.mount("https://", HTTPAdapter(max_retries=retry, pool_maxsize=8))
    session.mount("http://", HTTPAdapter(max_retries=retry, pool_maxsize=8))
    session.headers["User-Agent"] = "parottasalna-blog-importer"
    return session


def fetch_wordpress(base_url: str, log) -> dict:
    """{slug or title key: {"link": url, "pres": [inner html of each <pre>]}} from the WordPress REST API."""
    pre = re.compile(r"<pre\b[^>]*>(.*?)</pre>", re.S | re.I)
    posts, page = {}, 1
    session = wordpress_session()
    while True:
        response = session.get(
            f"{base_url.rstrip('/')}/wp-json/wp/v2/posts",
            params={"per_page": 100, "page": page, "_fields": "slug,link,title,content"},
            timeout=30,
        )
        if response.status_code == 400 and page > 1:      # WordPress says "past the last page"
            break
        response.raise_for_status()
        batch = response.json()
        for item in batch:
            entry = {"link": item.get("link", ""), "pres": pre.findall(item.get("content", {}).get("rendered", ""))}
            posts[item["slug"]] = entry
            posts.setdefault("title:" + title_key(item.get("title", {}).get("rendered", "")), entry)
        if page >= int(response.headers.get("X-WP-TotalPages", page)) or not batch:
            break
        page += 1
    log(f"WordPress: read {sum(1 for k in posts if not k.startswith('title:'))} posts from {base_url}")
    return posts


class Command(BaseCommand):
    help = "Import blog posts from an Obsidian vault into the blog."

    def add_arguments(self, parser):
        parser.add_argument("source", nargs="?", help="Vault folder (default: BLOG_SRC_ROOT)")
        parser.add_argument("--prune", action="store_true", help="Delete posts that are no longer in the vault")
        parser.add_argument("--no-wordpress", action="store_true",
                            help="Don't contact WordPress (no code repair, no canonical links)")

    def handle(self, source, prune, no_wordpress, **options):
        root = Path(source or settings.BLOG_SRC_ROOT).expanduser().resolve()
        if not root.is_dir():
            raise CommandError(f"Vault folder not found: {root}")
        if root != Path(settings.BLOG_SRC_ROOT).expanduser().resolve():
            self.stderr.write(self.style.WARNING(
                f"Images are served from BLOG_SRC_ROOT ({settings.BLOG_SRC_ROOT}); set it to {root} "
                "so posts' local images load."))

        parsed = []
        for path in sorted(root.rglob("*.md")):
            if SKIP_DIRS & set(path.relative_to(root).parts):
                continue
            post = parse_post(path)
            if post:
                parsed.append(post)
        if not parsed:
            raise CommandError(f"No blog posts (with 'layout: post' frontmatter) found in {root}")

        # Unique slugs, and a title → slug map for [[wikilinks]].
        seen = set()
        for post in parsed:
            base, n = post.slug, 2
            while post.slug in seen:
                post.slug, n = f"{base}-{n}", n + 1
            seen.add(post.slug)
        by_title = {p.title.casefold(): p.slug for p in parsed}

        def link_for_title(title):
            slug = by_title.get(title.strip().casefold())
            return f"/blog/{slug}/" if slug else None

        # Local images: every image file in the vault, findable by path or (for ![[name.png]]) by file name.
        images_by_name = {}
        for path in root.rglob("*"):
            if path.suffix.lower() in ASSET_EXTENSIONS and not (SKIP_DIRS & set(path.relative_to(root).parts)):
                images_by_name.setdefault(path.name.casefold(), path)

        def make_asset_resolver(post_path, used):
            def asset_url(ref):
                ref = unquote(ref.split("?")[0].split("#")[0]).strip()
                if not ref:
                    return None
                candidates = [post_path.parent / ref, root / ref.lstrip("/")]
                found = next((c.resolve() for c in candidates if c.is_file()), None)
                if found is None and "/" not in ref:
                    found = images_by_name.get(ref.casefold())
                if found is None or found.suffix.lower() not in ASSET_EXTENSIONS:
                    return None
                try:
                    rel = found.resolve().relative_to(root).as_posix()
                except ValueError:                 # outside the vault: never serve it
                    return None
                if SKIP_DIRS & set(rel.split("/")):
                    return None
                used.add(rel)
                return "/blog/media/" + quote(rel)
            return asset_url

        wordpress_host = urlparse(settings.BLOG_WORDPRESS_URL or branding.WEBSITE).netloc.removeprefix("www.")
        slug_by_stem = {p.path.stem: p.slug for p in parsed}
        slug_by_stem.update({p.slug: p.slug for p in parsed})

        tag_slugs = {slugify(t) for p in parsed for t in p.tags}

        def post_href(url):
            """Map a link to the old WordPress/Hashnode blog on our domain to the same page here."""
            slug = post_link_slug(url, wordpress_host)
            if slug in slug_by_stem:
                return f"/blog/{slug_by_stem[slug]}/"
            parts = urlparse(html.unescape(url))
            if parts.netloc.removeprefix("www.") != wordpress_host:
                return None
            path = unquote(parts.path).strip("/")
            if path == "":
                return "/blog/"                                        # the old blog's home page
            if path.startswith("tag/") and slugify(path[4:]) in tag_slugs:
                return f"/blog/?tag={slugify(path[4:])}"
            if path.startswith("category/"):
                return f"/blog/?category={slugify(path.rsplit('/', 1)[-1])}"
            if "/" not in path and path in slug_by_stem:              # Hashnode-style /<slug>#heading
                return f"/blog/{slug_by_stem[path]}/"
            return None

        wordpress = {}
        if settings.BLOG_WORDPRESS_URL and not no_wordpress:
            try:
                wordpress = fetch_wordpress(settings.BLOG_WORDPRESS_URL, self.stdout.write)
            except (requests.RequestException, ValueError) as exc:
                self.stderr.write(self.style.WARNING(f"WordPress not reachable ({exc}); importing without it."))

        created = updated = repaired_total = assets_total = 0
        with transaction.atomic():
            for post in parsed:
                wp = wordpress_entry(wordpress, post)
                body, repaired = repair_code_blocks(post.body, wp["pres"]) if wp else (post.body, 0)
                repaired_total += repaired
                used = set()
                body_html = render_body(body, link_for_title, make_asset_resolver(post.path, used), post_href)
                related = []
                for inner in post.related_titles:
                    slug = next((by_title[t.casefold()] for t, _ in wikilink_candidates(inner)
                                 if t.casefold() in by_title), None)
                    if slug and slug != post.slug and slug not in related:
                        related.append(slug)
                obj, was_created = Post.objects.update_or_create(
                    slug=post.slug,
                    defaults={
                        "title": post.title,
                        "published_at": post.published_at,
                        "category": post.category,
                        "category_slug": slugify(post.category),
                        "body_html": body_html,
                        "excerpt": excerpt_of(body_html),
                        "reading_minutes": reading_minutes(body_html),
                        "related_slugs": related,
                        "source_path": str(post.path.relative_to(root)),
                        # Only overwrite the original URL when WordPress was actually consulted.
                        **({"wordpress_url": wp["link"] if wp else ""} if wordpress else {}),
                    },
                )
                obj.assets.exclude(path__in=used).delete()
                PostAsset.objects.bulk_create([PostAsset(post=obj, path=path) for path in used], ignore_conflicts=True)
                assets_total += len(used)
                tags = []
                for name in post.tags:
                    tag_slug = slugify(name)
                    if tag_slug:
                        tag, _ = Tag.objects.get_or_create(slug=tag_slug, defaults={"name": name})
                        tags.append(tag)
                obj.tags.set(tags)
                created += was_created
                updated += not was_created

            removed = 0
            if prune:
                removed, _ = Post.objects.exclude(slug__in=seen).delete()
            Tag.objects.filter(posts__isnull=True).delete()

        self.stdout.write(self.style.SUCCESS(
            f"Imported {len(parsed)} posts ({created} new, {updated} updated"
            f"{f', {removed} removed' if prune else ''}); repaired {repaired_total} code blocks; "
            f"{assets_total} local images."
        ))
