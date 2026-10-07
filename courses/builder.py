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
from django.urls import reverse
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

/* Imported GitBook content: video embeds and collapsible solutions */
.video-embed { position: relative; aspect-ratio: 16 / 9; margin: 1.25rem 0; border-radius: 12px; overflow: hidden;
  background: #000; box-shadow: 0 10px 30px rgba(15, 27, 51, .18); }
.video-embed iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
details.solution { margin: .75rem 0 1.75rem; border: 1px solid var(--color-background-border); border-radius: 10px;
  background: var(--color-background-secondary); }
details.solution > summary { cursor: pointer; padding: .6rem 1rem; font-weight: 600; color: var(--color-brand-primary); }
details.solution > summary::before { content: "💡 Show "; }
details.solution[open] > summary::before { content: "💡 "; }
details.solution[open] > summary { border-bottom: 1px solid var(--color-background-border); }
details.solution > :not(summary) { margin-left: 1rem; margin-right: 1rem; }

/* Chapter completion (progress.js) */
.page-progress { margin: 2rem 0 1rem; padding: 1.1rem 1.25rem; border-radius: 14px; display: flex; align-items: center;
  justify-content: space-between; gap: 1rem; flex-wrap: wrap; border: 1px solid var(--color-background-border);
  background: var(--color-background-secondary); }
.page-progress.is-done { border-color: rgba(16, 185, 129, .45); background: rgba(16, 185, 129, .08); }
.page-progress .pp-text strong { display: block; font-size: 1rem; }
.page-progress .pp-text span { font-size: .88rem; color: var(--color-foreground-secondary); }
.page-progress .pp-actions { display: flex; gap: .5rem; flex-wrap: wrap; align-items: center; }
.pp-btn { font: inherit; font-weight: 700; font-size: .92rem; cursor: pointer; padding: .55rem 1rem; border-radius: 10px; border: 0;
  background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; text-decoration: none; display: inline-block; }
.pp-btn:hover { filter: brightness(1.05); }
.pp-btn[disabled] { opacity: .6; cursor: wait; }
.pp-btn.ghost { background: transparent; color: var(--color-foreground-secondary); border: 1px solid var(--color-background-border); font-weight: 600; }
.pp-btn.next { background: #10b981; }
.done-chip { display: inline-flex; align-items: center; gap: .35rem; margin: -.25rem .4rem 1rem 0; padding: .3rem .8rem; border-radius: 999px;
  font-size: .85rem; font-weight: 600; background: rgba(16, 185, 129, .12); color: #059669; border: 1px solid rgba(16, 185, 129, .35); }
.sidebar-tree a.reference.is-done::after { content: "✓"; margin-left: .4rem; font-weight: 800; color: #10b981; }
.sidebar-progress { margin: .25rem var(--sidebar-item-spacing-horizontal, 1rem) .75rem; font-size: .8rem; color: var(--color-foreground-secondary); }
.sidebar-progress .bar { height: 6px; border-radius: 999px; background: var(--color-background-border); overflow: hidden; margin-top: .35rem; }
.sidebar-progress .bar span { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, #2563eb, #10b981); }

/* Quiz card injected by quiz.js */
.quiz-chip { display: inline-flex; align-items: center; gap: .4rem; margin: -.25rem 0 1rem; padding: .3rem .8rem; border-radius: 999px;
  font-size: .85rem; font-weight: 600; text-decoration: none; background: var(--color-sidebar-item-background--hover);
  color: var(--color-brand-primary); border: 1px solid var(--color-background-border); }
.quiz-chip:hover { border-color: var(--color-brand-content); }
.quiz-card { margin: 2.5rem 0 1rem; padding: 1.4rem 1.5rem; border-radius: 16px; color: #fff;
  background: linear-gradient(120deg, #1e3a8a 0%, #2563eb 60%, #38bdf8 100%); box-shadow: 0 14px 40px rgba(30, 58, 138, .25); }
.quiz-card h2 { margin: 0 0 .25rem !important; padding: 0 !important; border: 0 !important; color: #fff; font-size: 1.3rem; }
.quiz-card > p { margin: 0 0 1rem; opacity: .9; }
.quiz-card .quiz-item { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
  padding: .8rem 1rem; border-radius: 12px; background: rgba(255, 255, 255, .12); border: 1px solid rgba(255, 255, 255, .2); }
.quiz-card .quiz-item + .quiz-item { margin-top: .6rem; }
.quiz-card .quiz-item strong { display: block; }
.quiz-card .quiz-item small { opacity: .85; }
.quiz-card .quiz-actions { display: flex; gap: .5rem; flex-wrap: wrap; }
.quiz-card a.quiz-btn { display: inline-block; padding: .5rem 1rem; border-radius: 10px; font-weight: 700; text-decoration: none;
  background: #fff; color: #1d4ed8; }
.quiz-card a.quiz-btn.ghost { background: transparent; color: #fff; border: 1px solid rgba(255, 255, 255, .5); }
.quiz-card a.quiz-btn:hover { filter: brightness(.95); }
.quiz-card .quiz-all { display: inline-block; margin-top: .9rem; color: #fff; font-size: .9rem; opacity: .9; }
"""

# Adds the "Check your understanding" card to docs pages that have a quiz. Quizzes are
# fetched at view time, so adding one in the admin doesn't need a docs rebuild.
QUIZ_JS = r"""
(function () {
  var feed = document.querySelector('meta[name="portal-quiz-feed"]');
  var page = document.querySelector('meta[name="portal-page"]');
  var article = document.querySelector("article[role=main]") || document.querySelector("article");
  if (!feed || !page || !article) return;

  function el(tag, attrs, text) {
    var node = document.createElement(tag);
    for (var key in attrs || {}) node.setAttribute(key, attrs[key]);
    if (text) node.textContent = text;
    return node;
  }

  fetch(feed.content, { credentials: "same-origin", headers: { Accept: "application/json" } })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) {
      if (!data || !data.quizzes.length) return;
      var isIndex = page.content === "index";
      var quizzes = data.quizzes.filter(function (q) { return q.chapter === page.content; });
      if (!quizzes.length && !isIndex) return;

      var card = el("section", { class: "quiz-card", id: "chapter-quiz" });
      if (quizzes.length) {
        card.appendChild(el("h2", null, "\ud83d\udcdd Check your understanding"));
        card.appendChild(el("p", null, "Finished this chapter? Take the quiz to test what you learned."));
        quizzes.forEach(function (q) {
          var row = el("div", { class: "quiz-item" });
          var info = el("div");
          info.appendChild(el("strong", null, q.title));
          var meta = q.questions + " question" + (q.questions === 1 ? "" : "s");
          if (q.best) meta += " \u00b7 Your best: " + q.best.score + "/" + q.best.max_score + " (" + q.best.percentage + "%)";
          info.appendChild(el("small", null, meta));
          row.appendChild(info);
          var actions = el("div", { class: "quiz-actions" });
          if (q.best) actions.appendChild(el("a", { class: "quiz-btn ghost", href: q.best.url }, "View result"));
          if (q.can_attempt) actions.appendChild(el("a", { class: "quiz-btn", href: q.url }, q.best ? "Retake quiz" : "Take the quiz"));
          row.appendChild(actions);
          card.appendChild(row);
        });
        var h1 = article.querySelector("h1");
        if (h1) {
          var chip = el("a", { class: "quiz-chip", href: "#chapter-quiz" }, "\ud83d\udcdd Quiz available for this chapter");
          h1.insertAdjacentElement("afterend", chip);
        }
      } else {
        card.appendChild(el("h2", null, "\ud83d\udcdd Course quizzes"));
        card.appendChild(el("p", null, data.quizzes.length + " quiz" + (data.quizzes.length === 1 ? "" : "zes") + " available. Test yourself after each session."));
      }
      card.appendChild(el("a", { class: "quiz-all", href: data.list_url }, "See all quizzes \u2192"));
      var progressBox = document.getElementById("page-progress");
      if (progressBox) article.insertBefore(card, progressBox); else article.appendChild(card);
    })
    .catch(function () {});
})();
"""

# "Mark as complete" for each chapter, plus ticks and a progress bar in the sidebar.
PROGRESS_JS = r"""
(function () {
  function meta(name) {
    var node = document.querySelector('meta[name="' + name + '"]');
    return node ? node.content : "";
  }
  var url = meta("portal-progress"), page = meta("portal-page"), root = meta("portal-docs-root");
  var article = document.querySelector("article[role=main]") || document.querySelector("article");
  if (!url || !article) return;

  function el(tag, attrs, text) {
    var node = document.createElement(tag);
    for (var key in attrs || {}) node.setAttribute(key, attrs[key]);
    if (text) node.textContent = text;
    return node;
  }
  function csrf() {
    var match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  }
  function pageOf(href) {
    var link = new URL(href, location.href), base = new URL(root, location.href).pathname;
    if (link.origin !== location.origin || link.pathname.indexOf(base) !== 0) return null;
    var rel = link.pathname.slice(base.length);
    if (rel === "" || rel.slice(-1) === "/") rel += "index.html";
    return decodeURIComponent(rel).replace(/\.html$/, "");
  }

  var isChapter = page !== "index";
  var box = isChapter ? el("section", { class: "page-progress", id: "page-progress" }) : null;
  if (box) article.appendChild(box);
  var state = null;

  function renderSidebar() {
    document.querySelectorAll(".sidebar-tree a.reference").forEach(function (a) {
      a.classList.toggle("is-done", state.done.has(pageOf(a.href)));
    });
    var holder = document.querySelector(".sidebar-progress");
    if (!state.total) { if (holder) holder.remove(); return; }
    if (!holder) {
      holder = el("div", { class: "sidebar-progress" });
      var anchor = document.querySelector(".sidebar-search-container") || document.querySelector(".sidebar-brand");
      if (anchor) anchor.insertAdjacentElement("afterend", holder); else return;
    }
    var count = state.done.size, pct = Math.round(100 * count / state.total);
    holder.textContent = count === state.total ? "\ud83c\udfc6 Course completed!" : count + " of " + state.total + " chapters completed";
    var bar = el("div", { class: "bar" }), fill = el("span");
    fill.style.width = pct + "%";
    bar.appendChild(fill);
    holder.appendChild(bar);
  }

  function renderChip() {
    var chip = document.querySelector(".done-chip");
    if (chip) chip.remove();
    var h1 = article.querySelector("h1");
    if (isChapter && h1 && state.done.has(page)) h1.insertAdjacentElement("afterend", el("span", { class: "done-chip" }, "\u2713 Completed"));
  }

  function renderBox() {
    if (!box) return;
    box.textContent = "";
    var text = el("div", { class: "pp-text" }), actions = el("div", { class: "pp-actions" });
    var done = state.done.has(page);
    box.classList.toggle("is-done", done);
    if (done) {
      text.appendChild(el("strong", null, "\u2705 You've completed this chapter"));
      text.appendChild(el("span", null, state.done.size + " of " + state.total + " chapters done in this course."));
      var next = document.querySelector(".related-pages a.next-page");
      if (next) {
        var title = next.querySelector(".title");
        actions.appendChild(el("a", { class: "pp-btn next", href: next.href }, "Next: " + (title ? title.textContent.trim() : "chapter") + " \u2192"));
      }
      actions.appendChild(button("Mark as not complete", "pp-btn ghost", false));
    } else {
      text.appendChild(el("strong", null, "Finished reading?"));
      text.appendChild(el("span", null, "Mark this chapter as complete to track your progress."));
      actions.appendChild(button("\u2713 Mark as complete", "pp-btn", true));
    }
    box.appendChild(text);
    box.appendChild(actions);
  }

  function button(label, cls, completed) {
    var btn = el("button", { class: cls, type: "button" }, label);
    btn.addEventListener("click", function () {
      btn.disabled = true;
      var body = new URLSearchParams({ page: page, completed: completed ? "true" : "false" });
      fetch(state.update_url, {
        method: "POST", credentials: "same-origin", body: body,
        headers: { "X-CSRFToken": csrf(), "Accept": "application/json" }
      })
        .then(function (r) { if (!r.ok) throw r.status; return r.json(); })
        .then(function (res) {
          if (res.completed) state.done.add(page); else state.done.delete(page);
          render();
        })
        .catch(function (status) {
          btn.disabled = false;
          btn.textContent = status === 401 || status === 403
            ? "Session expired \u2014 refresh and sign in" : "Couldn't save \u2014 try again";
        });
    });
    return btn;
  }

  function render() { renderSidebar(); renderChip(); renderBox(); }

  fetch(url, { credentials: "same-origin", headers: { Accept: "application/json" } })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) {
      // Not enrolled in this course (or signed out): no progress UI, nothing stored.
      if (!data || !data.tracking) { if (box) box.remove(); return; }
      state = data;
      state.done = new Set(data.completed);
      render();
    })
    .catch(function () { if (box) box.remove(); });
})();
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
<meta name="robots" content="{{ brand_robots|e }}">
<meta name="theme-color" content="{{ brand_theme_color|e }}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{{ brand_name|e }}">
<meta property="og:title" content="{{ title|striptags|e }} - {{ docstitle|striptags|e }}">
<meta property="og:description" content="{{ brand_description|e }}">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">{{ brand_json_ld }}</script>
<meta name="portal-quiz-feed" content="{{ quiz_feed_url|e }}">
<meta name="portal-page" content="{{ pagename|e }}">
<meta name="portal-progress" content="{{ progress_url|e }}">
<meta name="portal-docs-root" content="{{ docs_root|e }}">
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
        "quiz_feed_url": reverse("quiz_feed", args=[course.slug]),
        "progress_url": reverse("course_progress", args=[course.slug]),
        "docs_root": reverse("course_docs", args=[course.slug]),
        # Common courses are public, so let search engines index them.
        "brand_robots": "index, follow" if course.is_common else "noindex, follow",
    }
    conf = f"""
project = {course.title!r}
html_title = {course.title!r}
root_doc = "index"
extensions = {extensions!r}
source_suffix = {{".md": "markdown", ".rst": "restructuredtext"}}
myst_enable_extensions = ["colon_fence", "deflist", "tasklist"]
myst_heading_anchors = 3
# Imported GitBook pages often jump from H1 to H3; that's fine to read, so don't warn.
suppress_warnings = ["myst.header"]
html_theme = {settings.SPHINX_THEME!r}
html_static_path = ["_static"]
templates_path = ["_templates"]
html_favicon = "_static/favicon.ico"
html_logo = "_static/logo.png"
html_context = {context!r}
html_css_files = ["portal.css"]
html_js_files = ["progress.js", "quiz.js"]
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
                '<a href="/">&larr; All courses</a> &nbsp;·&nbsp; '
                + ("" if course.is_common else
                   f'<a href="{reverse("quiz_list", args=[course.slug])}">📝 Quizzes</a> &nbsp;·&nbsp; ')
                + f'{branding.CADENCE} <a href="{branding.YOUTUBE_SUBSCRIBE}" target="_blank" '
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
    (static / "quiz.js").write_text(QUIZ_JS, encoding="utf-8")
    (static / "progress.js").write_text(PROGRESS_JS, encoding="utf-8")
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
