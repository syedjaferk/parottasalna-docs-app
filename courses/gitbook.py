"""Convert a GitBook space (README.md + SUMMARY.md + .gitbook/assets) into a MyST/Sphinx course folder."""
import html
import posixpath
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT_README = "introduction.md"  # the space's README becomes this chapter; index.md is generated
ASSETS_DIR = "_assets"


@dataclass
class Entry:
    title: str
    target: str  # relative .md path or external URL
    children: list = field(default_factory=list)

    @property
    def is_external(self):
        return self.target.startswith(("http://", "https://"))


@dataclass
class Group:
    caption: str
    entries: list = field(default_factory=list)


_ITEM = re.compile(r"^(?P<indent>\s*)[*-]\s+\[(?P<title>.+)\]\((?P<target>[^)]+)\)\s*$")


def _unescape_md(text):
    return re.sub(r"\\([\\`*_{}\[\]()#+\-.!])", r"\1", text).strip()


def parse_summary(text):
    """SUMMARY.md -> list of Groups. '## Heading' starts a captioned group, '***' an uncaptioned one."""
    groups = [Group(caption="")]
    stack = []  # (indent, Entry)
    for line in text.splitlines():
        if line.startswith("## "):
            groups.append(Group(caption=line[3:].strip()))
            stack = []
            continue
        if line.strip() in ("***", "---", "___"):
            groups.append(Group(caption=""))
            stack = []
            continue
        match = _ITEM.match(line)
        if not match:
            continue
        entry = Entry(_unescape_md(match["title"]), unquote(match["target"].strip()))
        indent = len(match["indent"].expandtabs(2))
        while stack and stack[-1][0] >= indent:
            stack.pop()
        (stack[-1][1].children if stack else groups[-1].entries).append(entry)
        stack.append((indent, entry))
    return [g for g in groups if g.entries]


# --- page conversion -----------------------------------------------------------------------

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
_HEADING_ANCHOR = re.compile(r'\s*<a href="#[^"]*" id="[^"]*"></a>')
_FIGURE = re.compile(r"<figure>(.*?)</figure>", re.S)
_IMG = re.compile(r"<img\s+([^>]*?)/?>", re.S)
_ATTR = re.compile(r'(\w+)="([^"]*)"')
_FIGCAPTION = re.compile(r"<figcaption>(.*?)</figcaption>", re.S)
_MD_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]*\.gitbook/assets/[^)]+)\)")
_PRE = re.compile(r'<pre[^>]*>\s*<code(?: class="lang-([\w+-]+)")?[^>]*>(.*?)</code>\s*</pre>', re.S)
_EMBED = re.compile(r'{%\s*embed\s+url="([^"]+)"\s*%}(?:\s*(.*?)\s*{%\s*endembed\s*%})?', re.S)
_TABS = re.compile(r"{%\s*tabs\s*%}(.*?){%\s*endtabs\s*%}", re.S)
_TAB = re.compile(r'{%\s*tab\s+title="([^"]*)"\s*%}(.*?){%\s*endtab\s*%}', re.S)
_HINT = re.compile(r'{%\s*hint\s+style="(\w+)"\s*%}(.*?){%\s*endhint\s*%}', re.S)
_MD_LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)\)")
_TAGS = re.compile(r"<[^>]+>")


def youtube_id(url):
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.").removeprefix("m.")
    if host == "youtu.be":
        return parsed.path.strip("/").split("/")[0] or None
    if host in ("youtube.com", "youtube-nocookie.com"):
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] in ("live", "embed", "shorts"):
            return parts[1]
    return None


def _embed(match):
    url, caption = match[1], (match[2] or "").strip()
    video = youtube_id(url)
    if video and re.fullmatch(r"[\w-]{6,20}", video):
        block = (
            f'<div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/{video}" '
            'title="YouTube video" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" '
            'allow="accelerometer; encrypted-media; gyroscope; '
            'picture-in-picture; fullscreen" allowfullscreen></iframe></div>'
        )
        return f"\n{block}\n\n{caption}\n" if caption else f"\n{block}\n"
    return f"\n🔗 [{caption or url}]({url})\n"


def _tabs(match):
    parts = []
    for title, body in _TAB.findall(match[1]):
        body = body.strip("\n")
        if re.search(r"solution|answer", title, re.I):
            parts.append(f'<details class="solution">\n<summary>{html.escape(title)}</summary>\n\n{body}\n\n</details>')
        else:
            parts.append(f"**{title}**\n\n{body}")
    return "\n\n".join(parts)


def _hint(match):
    kind = {"info": "note", "success": "tip", "warning": "warning", "danger": "danger"}.get(match[1], "note")
    return f":::{{{kind}}}\n{match[2].strip()}\n:::"


def _pre(match):
    lang, body = match[1] or "", match[2]
    code = html.unescape(_TAGS.sub("", body)).rstrip("\n")
    return f"\n```{lang}\n{code}\n```\n"


class PageConverter:
    """Rewrites one GitBook page. Collects the assets it references in `self.assets`."""

    def __init__(self, src_root: Path, page_path: str, rename: dict):
        self.src_root = src_root
        self.page_path = page_path  # path of the page relative to the space root (source name)
        self.page_dir = posixpath.dirname(page_path)
        self.rename = rename  # {source relative path: output relative path}
        self.assets = {}  # {output asset name: source file}

    def _asset(self, src):
        src = unquote(src.split("?")[0].split("#")[0])
        resolved = posixpath.normpath(posixpath.join(self.page_dir, src))
        source = self.src_root / resolved
        if not source.is_file():
            return None
        stem = re.sub(r"[^\w.-]+", "-", source.stem).strip("-").lower() or "image"
        name = f"{stem}{source.suffix.lower()}"
        # Keep names unique if two different files collapse to the same safe name.
        while name in self.assets and self.assets[name] != source:
            stem += "-x"
            name = f"{stem}{source.suffix.lower()}"
        self.assets[name] = source
        return f"/{ASSETS_DIR}/{name}"

    def _image(self, src, alt, caption):
        path = self._asset(src) if ".gitbook/assets" in src or not src.startswith("http") else None
        target = path or src
        alt = html.unescape(alt).replace("\n", " ").strip()
        caption = html.unescape(_TAGS.sub("", caption)).strip()
        if caption:
            return f"\n```{{figure}} {target}\n:alt: {alt or caption}\n\n{caption}\n```\n"
        return f"\n![{alt}]({target})\n"

    def _figure(self, match):
        inner = match[1]
        img = _IMG.search(inner)
        if not img:
            return match[0]
        attrs = dict(_ATTR.findall(img[1]))
        caption = _FIGCAPTION.search(inner)
        return self._image(attrs.get("src", ""), attrs.get("alt", ""), caption[1] if caption else "")

    def _link(self, match):
        text, target = match[1], match[2]
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return match[0]
        path, _, anchor = target.partition("#")
        if not path.endswith(".md"):
            return match[0]
        resolved = posixpath.normpath(posixpath.join(self.page_dir, unquote(path)))
        new = self.rename.get(resolved)
        if new is None:
            return text  # page isn't part of the course: keep the text, drop the dead link
        rel = posixpath.relpath(new, self.page_dir or ".")
        return f"[{text}]({rel}{'#' + anchor if anchor else ''})"

    def convert(self, text):
        description = ""
        front = _FRONTMATTER.match(text)
        if front:
            text = text[front.end():]
            desc = re.search(r"^description:\s*(.+)$", front[1], re.M)
            description = desc[1].strip().strip("'\"") if desc else ""
        text = _HEADING_ANCHOR.sub("", text)
        text = _PRE.sub(_pre, text)
        text = _FIGURE.sub(self._figure, text)
        text = _MD_IMAGE.sub(lambda m: self._image(m[2], m[1], ""), text)
        text = _EMBED.sub(_embed, text)
        text = _TABS.sub(_tabs, text)
        text = _HINT.sub(_hint, text)
        text = _MD_LINK.sub(self._link, text)
        if description:
            text = re.sub(r"^(# .+\n)", lambda m: f"{m[1]}\n*{description}*\n", text, count=1, flags=re.M)
        # Sphinx rejects a document that ends with a horizontal rule.
        text = re.sub(r"(\n\s*(?:-{3,}|\*{3,}|_{3,})\s*)+\Z", "", text.rstrip())
        return text.strip() + "\n"


# --- whole space ---------------------------------------------------------------------------

def _toctree(entries, caption="", maxdepth=2, page_dir=""):
    lines = ["```{toctree}", f":maxdepth: {maxdepth}"]
    if caption:
        lines.append(f":caption: {caption}")
    lines.append("")
    for entry in entries:
        if entry.is_external:
            lines.append(f"{entry.title} <{entry.target}>")
        else:
            doc = posixpath.relpath(entry.output[:-3], page_dir or ".")
            lines.append(f"{entry.title} <{doc}>")
    lines.append("```")
    return "\n".join(lines)


def _walk(entries):
    for entry in entries:
        yield entry
        yield from _walk(entry.children)


def _is_empty(path: Path):
    body = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("# ")]
    return not body


def convert_space(src: Path, out: Path, title: str, description: str = ""):
    """Write a Sphinx-ready course folder to `out` (replacing it). Returns a short report dict."""
    summary = src / "SUMMARY.md"
    if not summary.is_file():
        raise ValueError(f"{src} has no SUMMARY.md; is it a GitBook space?")
    groups = parse_summary(summary.read_text(encoding="utf-8"))

    # Drop missing and empty placeholder pages, then decide output names.
    skipped = []
    for group in groups:
        group.entries = _prune(group.entries, src, skipped)
    groups = [g for g in groups if g.entries]
    rename = {}
    for entry in (e for g in groups for e in _walk(g.entries) if not e.is_external):
        entry.output = ROOT_README if entry.target == "README.md" else entry.target
        rename[entry.target] = entry.output

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    assets = {}
    pages = 0
    for entry in (e for g in groups for e in _walk(g.entries) if not e.is_external):
        converter = PageConverter(src, entry.target, rename)
        text = converter.convert((src / entry.target).read_text(encoding="utf-8"))
        if entry.children:
            text += "\n" + _toctree(entry.children, maxdepth=1, page_dir=posixpath.dirname(entry.output)) + "\n"
        dest = out / entry.output
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        assets.update(converter.assets)
        pages += 1

    if assets:
        (out / ASSETS_DIR).mkdir()
        for name, source in assets.items():
            shutil.copyfile(source, out / ASSETS_DIR / name)

    index = [f"# {title}", ""]
    if description:
        index += [description, ""]
    for position, group in enumerate(groups):
        caption = group.caption or ("Lessons" if position == 0 else "")
        index += [_toctree(group.entries, caption=caption), ""]
    (out / "index.md").write_text("\n".join(index), encoding="utf-8")

    return {"pages": pages, "assets": len(assets), "skipped": skipped}


def _prune(entries, src, skipped):
    kept = []
    for entry in entries:
        entry.children = _prune(entry.children, src, skipped)
        if entry.is_external:
            kept.append(entry)
            continue
        path = src / entry.target
        if not path.is_file() or (_is_empty(path) and not entry.children):
            skipped.append(entry.target)
            continue
        kept.append(entry)
    return kept
