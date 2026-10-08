"""Make the Obsidian vault independent of WordPress (used by the localize_blog_vault command).

For every post it:
  * puts back code blocks whose line breaks were lost in the WordPress export (from the live site),
  * downloads WordPress-hosted images into <vault>/attachments/YYYY/MM/ and points the post at them,
  * turns links to other parottasalna.com posts into [[wikilinks]].

Only the post files and the attachments folder are written. Running it again is a no-op.
"""
import hashlib
import html
import os
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urlparse

from .render import parse_post, repair_code_blocks

ATTACHMENTS = "attachments"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif"}
# Files a post may link to (images, plus downloadable documents such as infographic PDFs).
ASSET_EXTENSIONS = IMAGE_EXTENSIONS | {".pdf"}
# WordPress/Jetpack image proxy for images hosted elsewhere, e.g. i0.wp.com/cdn.hashnode.com/....png
_PROXY = re.compile(r"^https?://i\d\.wp\.com/(?!(?:www\.)?parottasalna\.com/wp-content/)([^?#\s]+)", re.I)
_UPLOAD_PATH = re.compile(r"/wp-content/uploads/(\d{4}/\d{2}/[^?#\"']+)")
_IMG_SRC = re.compile(r'(<img\b[^>]*?\bsrc=")([^"]+)(")', re.I)
_HREF = re.compile(r'(<a\b[^>]*?\bhref=")([^"]+)("[^>]*>)(.*?)(</a>)', re.I | re.S)
_SRCSET = re.compile(r'\s(?:srcset|sizes|data-orig-file|data-medium-file|data-large-file)="[^"]*"', re.I)


@dataclass
class Report:
    files_changed: int = 0
    code_blocks: int = 0
    images_downloaded: int = 0
    images_relinked: int = 0
    links_relinked: int = 0
    failed_downloads: list = field(default_factory=list)
    external_post_links: int = 0


def upload_path(url: str, allowed=IMAGE_EXTENSIONS) -> str | None:
    """Where a WordPress-hosted file goes inside attachments/ (or None if it isn't one we copy).

    '.../wp-content/uploads/2024/08/a.png?resize=..'  → '2024/08/a.png'
    'https://i0.wp.com/cdn.hashnode.com/res/x/Abc.png' → 'external/<hash>-Abc.png'  (proxied images)
    """
    url = unquote(html.unescape(url)).strip()
    proxied = _PROXY.match(url)
    if proxied:
        name = Path(proxied.group(1)).name
        if Path(name).suffix.lower() not in IMAGE_EXTENSIONS:
            return None
        digest = hashlib.sha1(proxied.group(1).encode()).hexdigest()[:10]
        return f"external/{digest}-{re.sub(r'[^A-Za-z0-9._-]+', '-', name)}"
    match = _UPLOAD_PATH.search(url)
    if not match:
        return None
    rel = match.group(1)
    return rel if Path(rel).suffix.lower() in allowed and ".." not in rel.split("/") else None


def source_urls(url: str, rel: str, wordpress_url: str) -> list[str]:
    """URLs to try when downloading: the original location first, then the referenced one."""
    url = html.unescape(url).strip()
    proxied = _PROXY.match(url)
    if proxied:
        return [f"https://{proxied.group(1)}", url]
    return [url, f"{wordpress_url.rstrip('/')}/wp-content/uploads/{rel}"]


def post_link_slug(url: str, wordpress_host: str) -> str | None:
    """'https://parottasalna.com/2024/12/26/some-slug/' → 'some-slug' (only for the WordPress host)."""
    parsed = urlparse(html.unescape(url))
    if parsed.netloc.removeprefix("www.") != wordpress_host:
        return None
    match = re.fullmatch(r"/\d{4}/\d{2}/\d{2}/([^/]+)/?", parsed.path)
    return unquote(match.group(1)) if match else None


def wordpress_entry(wordpress_posts: dict, post):
    """The WordPress copy of a vault post: by slug, file name, then loosely by title."""
    key = "title:" + re.sub(r"[^0-9a-z]+", "", html.unescape(post.title).casefold())
    return wordpress_posts.get(post.slug) or wordpress_posts.get(post.path.stem) or wordpress_posts.get(key)


def localize_vault(root: Path, wordpress_url: str, wordpress_posts: dict, download, dry_run=False, log=print) -> Report:
    """`download(url) -> bytes` fetches one image; `wordpress_posts` is fetch_wordpress() output."""
    report = Report()
    host = urlparse(wordpress_url).netloc.removeprefix("www.")
    posts = [p for p in (parse_post(path) for path in sorted(root.rglob("*.md"))
                         if not ({".git", ".obsidian", "Templates"} & set(path.relative_to(root).parts))) if p]
    title_by_slug = {p.path.stem: p.title for p in posts}
    title_by_slug.update({p.slug: p.title for p in posts})

    # 1. Work out every image we need, then download them in parallel (once each).
    wanted = {}                                     # upload path → first URL seen
    for post in posts:
        text = post.path.read_text(encoding="utf-8")
        for m in _IMG_SRC.finditer(text):
            rel = upload_path(m.group(2))
            if rel:
                wanted.setdefault(rel, html.unescape(m.group(2)))
        for m in _HREF.finditer(text):
            rel = upload_path(m.group(2), ASSET_EXTENSIONS)
            if rel:
                wanted.setdefault(rel, html.unescape(m.group(2)))
    attachments = root / ATTACHMENTS
    missing = {rel: url for rel, url in wanted.items() if not (attachments / rel).is_file()}
    log(f"Images: {len(wanted)} referenced, {len(missing)} to download")

    def fetch(item):
        rel, url = item
        for candidate in source_urls(url, rel, wordpress_url):
            try:
                return rel, download(candidate)
            except Exception as exc:                # try the next URL, then give up on this image
                error = exc
        return rel, error

    if missing and not dry_run:
        with ThreadPoolExecutor(max_workers=8) as pool:
            for rel, result in pool.map(fetch, missing.items()):
                if isinstance(result, bytes) and result:
                    target = attachments / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(result)
                    report.images_downloaded += 1
                else:
                    report.failed_downloads.append(rel)
    available = {rel for rel in wanted if dry_run or (attachments / rel).is_file()}

    # 2. Rewrite each post file.
    for post in posts:
        original = post.path.read_text(encoding="utf-8")
        text = original
        rel_prefix = os.path.relpath(attachments, post.path.parent).replace(os.sep, "/")

        wp = wordpress_entry(wordpress_posts, post)
        if wp:
            text, n = repair_code_blocks(text, wp["pres"])
            report.code_blocks += n

        def img(m):
            rel = upload_path(m.group(2))
            if not rel or rel not in available:
                return m.group(0)
            report.images_relinked += 1
            return f"{m.group(1)}{rel_prefix}/{rel}{m.group(3)}"

        text = _IMG_SRC.sub(img, text)
        text = re.sub(r"<img\b[^>]*>", lambda m: _SRCSET.sub("", m.group(0)), text, flags=re.I)

        def link(m):
            href = m.group(2)
            rel = upload_path(href, ASSET_EXTENSIONS)
            if rel and rel in available:              # a link to the full-size image
                report.images_relinked += 1
                return f"{m.group(1)}{rel_prefix}/{rel}{m.group(3)}{m.group(4)}{m.group(5)}"
            slug = post_link_slug(href, host)
            if slug is None:
                return m.group(0)
            title = title_by_slug.get(slug)
            if title is None:                           # a WordPress post that isn't in the vault
                report.external_post_links += 1
                return m.group(0)
            label = re.sub(r"<[^>]+>", "", m.group(4)).strip()
            report.links_relinked += 1
            return f"[[{title}|{label}]]" if label and label != title else f"[[{title}]]"

        text = _HREF.sub(link, text)
        if text != original:
            report.files_changed += 1
            if not dry_run:
                post.path.write_text(text, encoding="utf-8")
    return report
