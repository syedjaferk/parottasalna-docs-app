"""Reads the self-hosting story book from markdown files (no database).

Chapters live in settings.BOOK_ROOT as ``NN-slug.md``; images they reference live in ``BOOK_ROOT/images``.
Edit a file and the page updates (parsed copies are cached per file modification time). Chapter HTML is
sanitised with nh3 because pages are served from the portal's own domain.
"""
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import nh3
import yaml
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from markdown_it import MarkdownIt

from blog.render import ALLOWED_ATTRIBUTES, ALLOWED_TAGS, plain_text, reading_minutes

_FILENAME = re.compile(r"^(\d+)-([a-z0-9-]+)\.md$")
_H1 = re.compile(r"\A\s*#\s+(?P<title>.+?)\s*\n")
_TITLE = re.compile(r"^(?:Chapter\s+\d+\s*:\s*)?(?P<title>.+?)(?:\s+[—–]\s+(?P<topic>[^—–]+))?$")
_AUTHOR_NOTES = re.compile(r"\n#{2,3}\s*Author.s notes.*\Z", re.S | re.I)
_HEADING = re.compile(r"<h([23])>(.*?)</h\1>", re.S)
_IMG_FIGURE = re.compile(r'<p>(<img [^>]*>)\s*<em>(.*?)</em></p>', re.S)
_IMG = re.compile(r'<img src="([^"]*)"([^>]*)>')
_TAGS = re.compile(r"<[^>]+>")

_md = MarkdownIt("commonmark", {"html": False, "linkify": False}).enable("table")
ATTRIBUTES = {**ALLOWED_ATTRIBUTES, "h2": {"id"}, "h3": {"id"}, "img": {"src", "alt", "loading"}}


@dataclass
class Chapter:
    number: int
    slug: str
    title: str
    topic: str
    epigraph: str
    summary: str
    minutes: int
    body_html: str
    sections: list = field(default_factory=list)  # [(id, text)] for the contents list

    def get_absolute_url(self):
        return reverse("book_chapter", args=[self.slug])


@dataclass
class Book:
    title: str
    tamil_title: str
    tagline: str
    chapters: list


def _root() -> Path:
    return Path(settings.BOOK_ROOT)


def _image_url(root: Path, src: str):
    """Public URL for an image the chapter references, or None if the file isn't there (yet)."""
    name = Path(src).name
    if not name or not (root / "images" / name).is_file():
        return None
    return reverse("book_media", args=[name])


def _render(markdown: str, root: Path):
    html = _md.render(markdown)

    def image(m):
        url = _image_url(root, m.group(1))
        return f'<img src="{url}"{m.group(2)} loading="lazy">' if url else "<!--missing-image-->"

    html = _IMG.sub(image, html)
    # A picture on its own line followed by an italic line is a figure with a caption.
    html = _IMG_FIGURE.sub(r"<figure>\1<figcaption>\2</figcaption></figure>", html)
    html = re.sub(r"<p><!--missing-image-->\s*(<em>.*?</em>)?</p>", "", html, flags=re.S)
    html = re.sub(r"\A\s*<hr />\s*", "", html)

    sections, seen = [], set()

    def heading(m):
        level, inner = m.group(1), m.group(2)
        text = _TAGS.sub("", inner)
        base = slugify(text)[:60] or "section"
        ident, n = base, 2
        while ident in seen:
            ident, n = f"{base}-{n}", n + 1
        seen.add(ident)
        if level == "2":
            sections.append((ident, text))
        return f'<h{level} id="{ident}">{inner}</h{level}>'

    html = _HEADING.sub(heading, html)
    return nh3.clean(html, tags=ALLOWED_TAGS, attributes=ATTRIBUTES, url_schemes={"http", "https", "mailto"},
                     link_rel="noopener noreferrer"), sections


def _parse(path: Path, number: int, slug: str, root: Path) -> Chapter:
    raw = path.read_text(encoding="utf-8")
    raw = _AUTHOR_NOTES.sub("", raw)
    h1 = _H1.match(raw)
    heading = h1.group("title") if h1 else slug.replace("-", " ").title()
    parts = _TITLE.match(heading)
    title, topic = parts.group("title").strip(), (parts.group("topic") or "").strip()
    body = raw[h1.end():] if h1 else raw
    epigraph = ""
    quote = re.match(r"\s*>\s*\*\"?(.+?)\"?\*\s*\n", body)
    if quote:
        epigraph, body = quote.group(1).strip(), body[quote.end():]
    html, sections = _render(body, root)
    first_para = re.search(r"<p>(.*?)</p>", html, re.S)
    summary = plain_text(first_para.group(1))[:200] if first_para else ""
    return Chapter(number, slug, title, topic, epigraph, summary, reading_minutes(html), html, sections)


@lru_cache(maxsize=64)
def _cached(path: str, mtime: float, number: int, slug: str, root: str) -> Chapter:
    return _parse(Path(path), number, slug, Path(root))


def get_book() -> Book:
    root = _root()
    meta = {}
    if (root / "book.yaml").is_file():
        meta = yaml.safe_load((root / "book.yaml").read_text(encoding="utf-8")) or {}
    chapters = []
    for path in sorted(root.glob("*.md")):
        m = _FILENAME.match(path.name)
        if m:
            chapters.append(_cached(str(path), path.stat().st_mtime, int(m.group(1)), m.group(2), str(root)))
    return Book(meta.get("title", "Stories"), meta.get("tamil_title", ""), meta.get("tagline", ""), chapters)
