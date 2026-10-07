"""Builds a course's markdown into static HTML with Sphinx (+ MyST), safely and atomically."""
import contextlib
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

from django.conf import settings
from django.db import close_old_connections, connections
from django.utils import timezone

from . import branding
from .models import Course

try:  # POSIX only; on other platforms builds simply aren't locked.
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

LOG_LIMIT = 20_000


# Blue brand colours for the Furo theme, kept in step with templates/base.html.
FURO_LIGHT = {
    "color-brand-primary": "#1d4ed8",
    "color-brand-content": "#2563eb",
    "color-brand-visited": "#1e40af",
    "color-announcement-background": "#1e3a8a",
    "color-announcement-text": "#ffffff",
    "color-sidebar-background": "#f3f7ff",
    "color-sidebar-background-border": "#dbe4f3",
    "color-sidebar-item-background--hover": "#e8f0ff",
    "color-sidebar-search-background": "#ffffff",
    "color-highlighted-background": "#dbeafe",
    "color-inline-code-background": "#eef4ff",
    "color-admonition-title--note": "#2563eb",
    "color-admonition-title-background--note": "#e8f0ff",
    "font-stack": "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
    "font-stack--monospace": "'JetBrains Mono', SFMono-Regular, Menlo, Consolas, monospace",
}
FURO_DARK = {
    "color-brand-primary": "#93c5fd",
    "color-brand-content": "#60a5fa",
    "color-brand-visited": "#a5b4fc",
    "color-background-primary": "#0b1326",
    "color-background-secondary": "#0e1a33",
    "color-background-border": "#1f2d4d",
    "color-announcement-background": "#13275a",
    "color-announcement-text": "#e6edfb",
    "color-sidebar-background": "#0e1a33",
    "color-sidebar-background-border": "#1f2d4d",
    "color-sidebar-item-background--hover": "#15284f",
    "color-sidebar-search-background": "#0b1326",
    "color-highlighted-background": "#1e3a8a",
    "color-inline-code-background": "#15284f",
    "color-admonition-title--note": "#60a5fa",
    "color-admonition-title-background--note": "#15284f",
}

# Extra polish on top of Furo. Written next to the generated conf.py, never taken from course content.
PORTAL_CSS = """
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap");

.announcement { font-size: .9rem; }
.announcement a { color: inherit; font-weight: 600; text-decoration: none; }
.announcement a:hover { text-decoration: underline; }

.sidebar-brand-text { font-weight: 800; letter-spacing: -0.01em; }
.sidebar-tree .caption, .sidebar-tree :not(.caption) > .caption-text {
  text-transform: uppercase; letter-spacing: .06em; font-size: .72rem; color: var(--color-brand-content);
}
.sidebar-tree .current-page > .reference { font-weight: 600; color: var(--color-brand-primary); }
.sidebar-tree .reference { border-radius: 8px; margin: 1px 8px; }

article h1 { font-weight: 800; letter-spacing: -0.02em; }
article h1::after {
  content: ""; display: block; width: 64px; height: 4px; margin-top: .6rem; border-radius: 4px;
  background: linear-gradient(90deg, #2563eb, #38bdf8);
}
article h2 { font-weight: 700; padding-bottom: .3rem; border-bottom: 1px solid var(--color-background-border); }
article h3 { font-weight: 600; }

.highlight { border-radius: 10px; }
div.highlight pre { border-radius: 10px; padding: 1rem 1.1rem; }
div[class*="highlight-"] { border-radius: 10px; border: 1px solid var(--color-background-border); }
code.literal { border-radius: 5px; padding: .1em .35em; border: 1px solid var(--color-background-border); }

.admonition { border-radius: 10px; overflow: hidden; box-shadow: 0 1px 3px rgba(15, 27, 51, .06); }

table.docutils { border-radius: 10px; overflow: hidden; border: 1px solid var(--color-background-border); }
table.docutils th { background: var(--color-sidebar-item-background--hover); }

.related-pages a { border-radius: 10px; padding: .75rem 1rem; border: 1px solid var(--color-background-border); }
.related-pages a:hover { border-color: var(--color-brand-content); }

img { border-radius: 8px; }

.sidebar-logo-container { margin: .5rem auto .25rem; }
.sidebar-logo { width: 72px; height: 72px; border-radius: 50%; object-fit: cover; box-shadow: 0 6px 20px rgba(56, 189, 248, .4); }
.footer .icons a { transition: color .15s; }
.footer .icons a:hover { color: var(--color-brand-primary); }
"""

# Wraps Furo's base.html: brand SEO tags on every docs page and "| Parottasalna" in titles.
BASE_TEMPLATE = """{% extends "!base.html" %}
{%- block htmltitle -%}
  {%- if pagename == master_doc -%}
    <title>{{ docstitle|striptags|e }} | {{ brand_name|e }}</title>
  {%- else -%}
    <title>{{ title|striptags|e }} - {{ docstitle|striptags|e }} | {{ brand_name|e }}</title>
  {%- endif -%}
{%- endblock -%}
{%- block extrahead -%}
{{ super() }}
<meta name="description" content="{{ docstitle|striptags|e }} \u2014 {{ brand_description|e }}">
<meta name="keywords" content="{{ brand_keywords|e }}">
<meta name="author" content="{{ brand_author|e }}">
<meta name="robots" content="noindex, follow">
<meta name="theme-color" content="{{ brand_theme_color|e }}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{{ brand_name|e }}">
<meta property="og:title" content="{{ title|striptags|e }} - {{ docstitle|striptags|e }}">
<meta property="og:description" content="{{ brand_description|e }}">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">{{ brand_json_ld }}</script>
{%- endblock -%}
"""


def _footer_icons():
    return [
        {
            "name": link["name"],
            "url": link["url"],
            "html": f'<svg viewBox="0 0 24 24" fill="currentColor" stroke="none"><path d="{link["icon"]}"/></svg>',
            "class": "",
        }
        for link in branding.SOCIAL_LINKS
    ]


def _conf_py(course: Course) -> str:
    # Generated config: we never execute a conf.py from course content.
    extensions = ["myst_parser"]
    if importlib.util.find_spec("sphinx_copybutton"):
        extensions.append("sphinx_copybutton")
    context = {
        "brand_name": branding.NAME,
        "brand_description": branding.META_DESCRIPTION,
        "brand_keywords": ", ".join(branding.KEYWORDS),
        "brand_author": branding.AUTHOR,
        "brand_theme_color": branding.THEME_COLOR,
        "brand_json_ld": branding.json_ld(""),
    }
    conf = f"""
project = {course.title!r}
html_title = {course.title!r}
root_doc = "index"
extensions = {extensions!r}
source_suffix = {{".md": "markdown", ".rst": "restructuredtext"}}
myst_enable_extensions = ["colon_fence", "deflist", "tasklist"]
myst_heading_anchors = 3
html_theme = {settings.SPHINX_THEME!r}
html_static_path = ["_static"]
templates_path = ["_templates"]
html_favicon = "_static/favicon.ico"
html_logo = "_static/logo.png"
html_context = {context!r}
html_css_files = ["portal.css"]
html_show_sourcelink = False
html_show_copyright = False
html_copy_source = False
copybutton_prompt_text = r">>> |\\.\\.\\. |\\$ "
copybutton_prompt_is_regexp = True
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**/.git", "**/.*"]
"""
    if settings.SPHINX_THEME == "furo":
        options = {
            "announcement": (
                '<a href="/">&larr; Back to my courses</a> &nbsp;·&nbsp; '
                f'{branding.CADENCE} <a href="{branding.YOUTUBE_SUBSCRIBE}" target="_blank" '
                f'rel="noopener">Subscribe to {branding.NAME} on YouTube</a>'
            ),
            "footer_icons": _footer_icons(),
            "light_css_variables": FURO_LIGHT,
            "dark_css_variables": FURO_DARK,
            "sidebar_hide_name": False,
            "navigation_with_keys": True,
        }
        conf += f"html_theme_options = {options!r}\n"
    return conf


def _write_conf(conf_dir: Path, course: Course):
    (conf_dir / "conf.py").write_text(_conf_py(course), encoding="utf-8")
    static = conf_dir / "_static"
    static.mkdir()
    (static / "portal.css").write_text(PORTAL_CSS, encoding="utf-8")
    brand_dir = Path(settings.BASE_DIR) / "static" / "brand"
    shutil.copyfile(brand_dir / "favicon.ico", static / "favicon.ico")
    shutil.copyfile(brand_dir / "logo-192.png", static / "logo.png")
    templates = conf_dir / "_templates"
    templates.mkdir()
    if settings.SPHINX_THEME == "furo":
        (templates / "base.html").write_text(BASE_TEMPLATE, encoding="utf-8")


@contextlib.contextmanager
def _course_lock(directory: Path):
    if fcntl is None:
        yield True
        return
    with open(directory / ".build.lock", "w") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            yield False
            return
        try:
            yield True
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def _finish(course_id, status, log):
    fields = {"build_status": status, "build_log": log[-LOG_LIMIT:]}
    if status == Course.BuildStatus.OK:
        fields["last_built_at"] = timezone.now()
    Course.objects.filter(pk=course_id).update(**fields)


def _swap(new_dir: Path, live_dir: Path, old_dir: Path):
    shutil.rmtree(old_dir, ignore_errors=True)
    if live_dir.exists():
        live_dir.rename(old_dir)
    new_dir.rename(live_dir)
    shutil.rmtree(old_dir, ignore_errors=True)


def build_course(course_id: int) -> bool:
    """Build one course. Returns True on success. The previous good build stays live on failure."""
    course = Course.objects.get(pk=course_id)
    out_root = Path(settings.DOCS_BUILD_ROOT) / course.slug
    out_root.mkdir(parents=True, exist_ok=True)

    with _course_lock(out_root) as acquired:
        if not acquired:
            return False  # another build of this course is already running

        Course.objects.filter(pk=course_id).update(build_status=Course.BuildStatus.BUILDING)

        try:
            src = course.src_dir
        except Exception as exc:  # unsafe source_dir
            _finish(course_id, Course.BuildStatus.FAILED, f"Invalid source_dir: {exc}")
            return False
        if not src.is_dir():
            _finish(course_id, Course.BuildStatus.FAILED, f"Source folder not found: {src}")
            return False
        if not (src / "index.md").exists() and not (src / "index.rst").exists():
            _finish(course_id, Course.BuildStatus.FAILED, "The source folder needs an index.md.")
            return False

        new_dir = out_root / "html.new"
        shutil.rmtree(new_dir, ignore_errors=True)

        with tempfile.TemporaryDirectory() as conf_dir:
            _write_conf(Path(conf_dir), course)
            cmd = [
                sys.executable, "-m", "sphinx",
                "-b", "html",
                "-c", conf_dir,
                "-d", str(out_root / "doctrees"),
                "--keep-going",
                str(src), str(new_dir),
            ]
            # Minimal environment: don't leak SECRET_KEY / OAuth secrets to the build process.
            env = {k: os.environ[k] for k in ("PATH", "HOME", "LANG", "LC_ALL", "VIRTUAL_ENV")
                   if k in os.environ}
            try:
                proc = subprocess.run(
                    cmd, capture_output=True, text=True, env=env,
                    timeout=settings.SPHINX_BUILD_TIMEOUT,
                )
            except subprocess.TimeoutExpired:
                shutil.rmtree(new_dir, ignore_errors=True)
                _finish(course_id, Course.BuildStatus.FAILED, "Build timed out.")
                return False
            except OSError as exc:
                _finish(course_id, Course.BuildStatus.FAILED, f"Could not start Sphinx: {exc}")
                return False

        log = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0 or not (new_dir / "index.html").exists():
            shutil.rmtree(new_dir, ignore_errors=True)
            _finish(course_id, Course.BuildStatus.FAILED, log or "Sphinx failed with no output.")
            return False

        _swap(new_dir, out_root / "html", out_root / "html.old")
        _finish(course_id, Course.BuildStatus.OK, log)
        return True


def build_in_background(course_ids):
    """Fire-and-forget builds from a request. Swap for Celery/RQ if you scale out."""
    ids = list(course_ids)
    Course.objects.filter(pk__in=ids).update(build_status=Course.BuildStatus.BUILDING)

    def run():
        close_old_connections()
        try:
            for course_id in ids:
                try:
                    build_course(course_id)
                except Exception as exc:  # never leave a course stuck on "building"
                    _finish(course_id, Course.BuildStatus.FAILED, f"Unexpected error: {exc}")
        finally:
            connections.close_all()

    threading.Thread(target=run, daemon=True).start()
