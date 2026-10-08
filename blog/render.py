"""Turn Obsidian vault posts (WordPress-exported HTML or Markdown) into safe HTML for the blog.

Blog pages are served from the app's own domain, next to the signed-in session cookie, so every
post is sanitised with nh3: only formatting tags survive, scripts and event handlers are removed,
and the only embeds allowed are YouTube videos (switched to youtube-nocookie.com).
"""
import html
import math
import re
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from pathlib import Path

import nh3
import yaml
from django.utils.text import slugify
from markdown_it import MarkdownIt

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
_RELATED = re.compile(r"\n#{2,3}\s*Related Posts\s*\n(?P<list>.*)\Z", re.S | re.I)
_WIKILINK = re.compile(r"(!?)\[\[([^\[\]]+)\]\]")
_PRE = re.compile(r"(<pre\b[^>]*>)(.*?)(</pre>)", re.S | re.I)
_IFRAME = re.compile(r"<iframe\b[^>]*>.*?</iframe>", re.S | re.I)
_YOUTUBE_SRC = re.compile(r'src="https?://(?:www\.)?youtube(?:-nocookie)?\.com/embed/([\w-]{6,20})[^"]*"', re.I)
_TAGS = re.compile(r"<[^>]+>")
# Code that must never be touched by wikilink conversion: HTML <pre>/<code>, Markdown fences and `inline`.
_CODE_SPANS = re.compile(r"(<pre\b.*?</pre>|<code\b.*?</code>|^```.*?^```|`[^`\n]+`)", re.S | re.I | re.M)

_md = MarkdownIt("commonmark", {"html": True, "linkify": False}).enable("table")

ALLOWED_TAGS = {
    "p", "br", "hr", "h1", "h2", "h3", "h4", "h5", "h6", "strong", "b", "em", "i", "u", "s", "del", "mark",
    "sub", "sup", "small", "a", "ul", "ol", "li", "blockquote", "pre", "code", "kbd", "img", "figure",
    "figcaption", "table", "thead", "tbody", "tr", "th", "td", "div", "span", "iframe", "details", "summary",
}
ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "img": {"src", "alt", "title", "width", "height"},
    "iframe": {"src", "title", "allow", "allowfullscreen", "loading", "referrerpolicy"},
    "th": {"colspan", "rowspan"},
    "td": {"colspan", "rowspan"},
    "ol": {"start"},
}


def wikilink_candidates(inner: str):
    """Possible (target, label) readings of [[inner]], most literal first.

    Post titles often contain '#' and '|' themselves ("Learning Notes #35 - ACID | Postgres"), so the
    whole text is tried as a title before Obsidian's [[target#heading|alias]] syntax.
    """
    inner = inner.strip()
    yield inner, inner
    if "|" in inner:
        target, alias = inner.rsplit("|", 1)
        yield target.strip(), alias.strip()
        yield target.split("#", 1)[0].strip(), alias.strip()
    if "#" in inner:
        yield inner.split("#", 1)[0].strip(), inner


@dataclass
class ParsedPost:
    path: Path
    slug: str
    title: str
    published_at: datetime
    category: str
    tags: list
    body: str                       # raw body, without the Related Posts section
    related_titles: list = field(default_factory=list)


def _as_datetime(value) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime.combine(value, time(), tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.strip().replace(" ", "T", 1))
        except ValueError:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    return None


def parse_post(path: Path) -> ParsedPost | None:
    """Read one vault file. Returns None for notes that aren't blog posts (no post frontmatter)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    match = _FRONTMATTER.match(text)
    if not match:
        return None
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return None
    if not isinstance(meta, dict) or meta.get("layout", "post") != "post":
        return None
    title = str(meta.get("title") or "").strip()
    published_at = _as_datetime(meta.get("date"))
    if not title or "{{" in title or published_at is None:      # skip templates and incomplete drafts
        return None

    body = text[match.end():]
    related = []
    rel = _RELATED.search(body)
    if rel:
        related = [m.group(2).strip() for m in _WIKILINK.finditer(rel.group("list")) if not m.group(1)]
        body = body[: rel.start()]

    tags = meta.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    tags = [str(t).strip() for t in tags if t and str(t).strip()]
    return ParsedPost(
        path=path, slug=slugify(path.stem) or slugify(title), title=title, published_at=published_at,
        category=str(meta.get("category") or "").strip(), tags=tags, body=body.strip(), related_titles=related,
    )


def _normalise_code(fragment: str) -> str:
    return re.sub(r"\s+", "", html.unescape(_TAGS.sub("", fragment)))


def repair_code_blocks(body: str, intact_blocks: list[str]) -> tuple[str, int]:
    """Replace <pre> blocks that lost their line breaks with the intact copy from WordPress.

    Blocks are matched by their text with all whitespace removed, so order doesn't matter and a
    block is only replaced when the content is truly the same.
    """
    lookup = {}
    for block in intact_blocks:
        if "\n" in block.strip("\n"):
            lookup.setdefault(_normalise_code(block), block)
    repaired = 0

    def fix(match):
        nonlocal repaired
        inner = match.group(2)
        if "\n" in inner.strip("\n"):
            return match.group(0)
        intact = lookup.get(_normalise_code(inner))
        if intact is None:
            return match.group(0)
        repaired += 1
        return match.group(1) + intact + match.group(3)

    return _PRE.sub(fix, body), repaired


def _embed(match) -> str:
    """Keep YouTube embeds (privacy-enhanced domain); drop every other iframe."""
    video = _YOUTUBE_SRC.search(match.group(0))
    if not video:
        return ""
    return (f'<div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/{video.group(1)}" '
            'title="YouTube video" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" '
            'allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen" '
            'allowfullscreen></iframe></div>')


_IMG_SRC = re.compile(r'(<img\b[^>]*?\bsrc=")([^"]+)(")', re.I)
_A_HREF = re.compile(r'(<a\b[^>]*?\bhref=")([^"]+)(")', re.I)


def _is_external(url: str) -> bool:
    return bool(re.match(r"^(?:[a-z][a-z0-9+.-]*:|//|#)", url, re.I))


def render_body(body: str, link_for_title, asset_url=lambda ref: None, post_href=lambda url: None) -> str:
    """Markdown/HTML → sanitised HTML.

    link_for_title(title) → URL for [[wikilinks]];  asset_url(ref) → URL for a local image (vault file);
    post_href(url) → app URL for a link to the old WordPress post, or None to keep the link.
    """
    def wikilink(match):
        if match.group(1):                          # ![[embed]] is handled by embeds below
            return match.group(0)
        label = match.group(2).strip()
        for target, candidate_label in wikilink_candidates(match.group(2)):
            url = link_for_title(target)
            if url:
                return f'<a href="{url}">{html.escape(candidate_label)}</a>'
        # Unresolved: show the readable part only.
        for target, candidate_label in list(wikilink_candidates(label))[1:2]:
            label = candidate_label
        return html.escape(label)

    def embed(match):
        if not match.group(1):
            return match.group(0)
        ref, _, alt = match.group(2).partition("|")
        url = asset_url(ref.strip())
        if not url:
            return html.escape(alt.strip() or ref.strip())
        alt = alt.strip() if alt.strip() and not alt.strip().isdigit() else Path(ref).stem   # "|300" is a width
        return f'<img src="{html.escape(url)}" alt="{html.escape(alt)}">'

    # Convert wikilinks and ![[embeds]] only outside code, so samples like `mat = [[1, 2]]` stay as written.
    parts = _CODE_SPANS.split(body)
    body = "".join(part if i % 2 else _WIKILINK.sub(wikilink, _WIKILINK.sub(embed, part))
                   for i, part in enumerate(parts))
    # Keep <pre> blocks away from the Markdown parser: a blank line inside code would end the HTML
    # block, and lines like "# comment" would turn into headings. Stash them and put them back after.
    stash = []

    def hide(match):
        stash.append(match.group(0))
        return f"@@PREBLOCK{len(stash) - 1}@@"

    body = _PRE.sub(hide, body)
    rendered = _md.render(body)
    rendered = re.sub(r"(?:<p>)?@@PREBLOCK(\d+)@@(?:</p>)?", lambda m: stash[int(m.group(1))], rendered)
    rendered = _IFRAME.sub(_embed, rendered)

    def local_image(m):
        tag = m.group(0)
        src_match = re.search(r'\bsrc="([^"]*)"', tag, re.I)
        src = html.unescape(src_match.group(1)) if src_match else ""
        if not src_match or _is_external(src) or src.startswith("/blog/media/"):
            return tag                                   # remote, or already resolved (embeds)
        url = asset_url(src)
        if not url:
            return ""                                    # missing local file: drop the whole tag
        return tag[: src_match.start(1)] + html.escape(url) + tag[src_match.end(1):]

    def link(m):
        href = html.unescape(m.group(2))
        url = post_href(href) or (None if _is_external(href) else asset_url(href))
        return f"{m.group(1)}{html.escape(url)}{m.group(3)}" if url else m.group(0)

    rendered = _A_HREF.sub(link, re.sub(r"<img\b[^>]*>", local_image, rendered, flags=re.I))
    clean = nh3.clean(
        rendered,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes={"http", "https", "mailto"},
        link_rel="noopener noreferrer",
        strip_comments=True,
    )
    # Re-add the wrapper class for embeds (nh3 drops classes) and lazy-load images.
    clean = clean.replace('<div><iframe src="https://www.youtube-nocookie.com/', '<div class="video-embed"><iframe src="https://www.youtube-nocookie.com/')
    return clean.replace("<img ", '<img loading="lazy" ')


def plain_text(rendered_html: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(_TAGS.sub(" ", rendered_html))).strip()


def excerpt_of(rendered_html: str, limit: int = 220) -> str:
    text = plain_text(rendered_html)
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(",.;:–-")
    return cut + "…"


def reading_minutes(rendered_html: str) -> int:
    return max(1, math.ceil(len(plain_text(rendered_html).split()) / 220))
