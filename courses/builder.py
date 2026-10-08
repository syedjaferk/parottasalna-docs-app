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


# Styling on top of the Shibuya theme. Written next to the generated conf.py, never taken from
# course content. Brand blue matches templates/base.html.
PORTAL_CSS = """
@import url("https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap");

/* Brand accent (Shibuya's blue scale, pulled toward the portal's #2563eb) */
:root[data-accent-color] { --accent-9: #2563eb; --accent-10: #1d4ed8; --accent-11: #1d4ed8; --accent-a10: #1d4ed8; }
html.dark[data-accent-color] { --accent-9: #3b82f6; --accent-10: #60a5fa; --accent-11: #93c5fd; --accent-a10: #93c5fd; }
:root { --sy-f-text: Inter, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
        --sy-f-heading: Inter, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
        --sy-f-mono: "JetBrains Mono", SFMono-Regular, Menlo, Consolas, monospace; }

/* Announcement bar */
.announcement { background: linear-gradient(90deg, #1e3a8a, #2563eb); color: #fff; font-size: .9rem; }
.announcement a { color: #fff; font-weight: 600; text-decoration: none; }
.announcement a:hover { text-decoration: underline; }

/* Header brand */
.sy-head-brand img { border-radius: 50%; }
.sy-head-brand strong { font-weight: 800; letter-spacing: -0.01em; }

/* Reading comfort */
.yue { font-size: 1.0625rem; line-height: 1.8; }
.yue p { margin: 0 0 1.15em; }
.yue li + li { margin-top: .4em; }
.yue h1 { font-weight: 800; letter-spacing: -0.02em; }
.yue h1::after { content: ""; display: block; width: 64px; height: 4px; margin-top: .7rem; border-radius: 4px;
  background: linear-gradient(90deg, #2563eb, #38bdf8); }
.yue h2 { font-weight: 700; margin-top: 2.6rem; }
.yue h3 { font-weight: 650; margin-top: 2rem; }
.yue img { border-radius: 10px; }
.yue div[class*="highlight-"] { margin: 1.3em 0 1.5em; }
.yue mark { border-radius: 4px; padding: 0 .2em; }

/* Course diagrams: inline SVG coloured from theme variables, so they follow light/dark mode */
figure.diagram { margin: 1.75rem 0; padding: 1rem; border-radius: 14px; border: 1px solid var(--sy-c-border);
  background: var(--sy-c-background); overflow-x: auto; }
figure.diagram svg { display: block; width: 100%; height: auto; min-width: 520px; margin: 0 auto; }
figure.diagram figcaption { margin-top: .6rem; font-size: .9rem; color: var(--sy-c-light); text-align: center; }
.dg text { fill: var(--sy-c-text); font-family: var(--sy-f-text); font-size: 15px; }
.dg text.small { font-size: 13px; fill: var(--sy-c-light); }
.dg text.bold { font-weight: 700; }
.dg text.code { font-family: var(--sy-f-mono); font-size: 14px; }
.dg text.title { font-size: 14px; font-weight: 700; letter-spacing: .04em; fill: var(--sy-c-light); }
.dg .box { fill: var(--sy-c-surface); stroke: var(--sy-c-border); stroke-width: 1.5; }
.dg .blue { fill: rgba(37, 99, 235, .10); stroke: #2563eb; stroke-width: 1.5; }
.dg .green { fill: rgba(16, 185, 129, .12); stroke: #10b981; stroke-width: 1.5; }
.dg .amber { fill: rgba(245, 158, 11, .14); stroke: #f59e0b; stroke-width: 1.5; }
.dg .red { fill: rgba(239, 68, 68, .10); stroke: #ef4444; stroke-width: 1.5; }
.dg .purple { fill: rgba(139, 92, 246, .12); stroke: #8b5cf6; stroke-width: 1.5; }
.dg .ghost { fill: none; stroke: var(--sy-c-border); stroke-width: 1.5; stroke-dasharray: 6 5; }
.dg .bar { fill: #2563eb; } .dg .bar.dim { fill: var(--sy-c-border); } .dg .bar.green { fill: #10b981; stroke: none; }
.dg .bar.amber { fill: #f59e0b; stroke: none; }
.dg .arrow { fill: none; stroke: var(--sy-c-light); stroke-width: 1.8; }
.dg .arrow.dashed { stroke-dasharray: 6 5; }
.dg .arrow.blue { stroke: #2563eb; fill: none; } .dg .arrow.green { stroke: #10b981; fill: none; }
.dg .arrow.red { stroke: #ef4444; fill: none; }
.dg .head { fill: var(--sy-c-light); } .dg .head.blue { fill: #2563eb; stroke: none; }
.dg .head.green { fill: #10b981; stroke: none; } .dg .head.red { fill: #ef4444; stroke: none; }
.dg .line { stroke: var(--sy-c-border); stroke-width: 1.5; } .dg .line.cut { stroke: #ef4444; stroke-width: 2; stroke-dasharray: 5 4; }
.dg .circle-a { fill: rgba(37, 99, 235, .12); stroke: #2563eb; stroke-width: 1.5; }
.dg .circle-b { fill: rgba(16, 185, 129, .12); stroke: #10b981; stroke-width: 1.5; }

/* Imported GitBook content: video embeds and collapsible solutions */
.video-embed { position: relative; aspect-ratio: 16 / 9; margin: 1.25rem 0; border-radius: 12px; overflow: hidden;
  background: #000; box-shadow: 0 10px 30px rgba(15, 27, 51, .18); }
.video-embed iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
details.solution { margin: .75rem 0 1.75rem; border: 1px solid var(--sy-c-border); border-radius: 10px; background: var(--sy-c-surface); }
details.solution > summary { cursor: pointer; padding: .6rem 1rem; font-weight: 600; color: var(--sy-c-link); }
details.solution > summary::before { content: "💡 Show "; }
details.solution[open] > summary::before { content: "💡 "; }
details.solution[open] > summary { border-bottom: 1px solid var(--sy-c-border); }
details.solution > :not(summary) { margin-left: 1rem; margin-right: 1rem; }
details.source { margin: .6rem 0; border: 1px solid var(--sy-c-border); border-radius: 10px; background: var(--sy-c-surface); }
details.source > summary { cursor: pointer; padding: .55rem 1rem; font-weight: 600; font-family: var(--sy-f-mono); font-size: .9rem;
  color: var(--sy-c-text); }
details.source > summary::before { content: "📄 "; }
details.source[open] > summary { border-bottom: 1px solid var(--sy-c-border); }
details.source > :not(summary) { margin: .5rem .75rem; }

/* Chapter completion (progress.js) */
.page-progress { margin: 2.5rem 0 1rem; padding: 1.1rem 1.25rem; border-radius: 14px; display: flex; align-items: center;
  justify-content: space-between; gap: 1rem; flex-wrap: wrap; border: 1px solid var(--sy-c-border); background: var(--sy-c-surface); }
.page-progress.is-done { border-color: rgba(16, 185, 129, .45); background: rgba(16, 185, 129, .08); }
.page-progress .pp-text strong { display: block; font-size: 1rem; color: var(--sy-c-heading); }
.page-progress .pp-text span { font-size: .88rem; color: var(--sy-c-light); }
.page-progress .pp-actions { display: flex; gap: .5rem; flex-wrap: wrap; align-items: center; }
.pp-btn { font: inherit; font-weight: 700; font-size: .92rem; cursor: pointer; padding: .55rem 1rem; border-radius: 10px; border: 0;
  background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff !important; text-decoration: none !important; display: inline-block; }
.pp-btn:hover { filter: brightness(1.05); }
.pp-btn[disabled] { opacity: .6; cursor: wait; }
.pp-btn.ghost { background: transparent; color: var(--sy-c-light) !important; border: 1px solid var(--sy-c-border); font-weight: 600; }
.pp-btn.next { background: #10b981; }
.done-chip { display: inline-flex; align-items: center; gap: .35rem; margin: -.25rem .4rem 1rem 0; padding: .3rem .8rem; border-radius: 999px;
  font-size: .85rem; font-weight: 600; background: rgba(16, 185, 129, .12); color: #059669; border: 1px solid rgba(16, 185, 129, .35); }
.globaltoc a.reference.is-done::after { content: "✓"; margin-left: .4rem; font-weight: 800; color: #10b981; }
.sidebar-progress { margin: 0 0 1.25rem; padding: .75rem .9rem; border-radius: 12px; font-size: .82rem; font-weight: 600;
  color: var(--sy-c-text); background: var(--sy-c-surface); border: 1px solid var(--sy-c-border); }
.sidebar-progress .bar { height: 6px; border-radius: 999px; background: var(--sy-c-border); overflow: hidden; margin-top: .45rem; }
.sidebar-progress .bar span { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, #2563eb, #10b981); }

/* Quiz card injected by quiz.js */
.quiz-chip { display: inline-flex; align-items: center; gap: .4rem; margin: -.25rem 0 1rem; padding: .3rem .8rem; border-radius: 999px;
  font-size: .85rem; font-weight: 600; text-decoration: none !important; background: var(--accent-a3, rgba(37, 99, 235, .1));
  color: var(--sy-c-link); border: 1px solid var(--sy-c-border); }
.quiz-chip:hover { border-color: var(--sy-c-link); }
.quiz-card { margin: 2.5rem 0 1rem; padding: 1.4rem 1.5rem; border-radius: 16px; color: #fff;
  background: linear-gradient(120deg, #1e3a8a 0%, #2563eb 60%, #38bdf8 100%); box-shadow: 0 14px 40px rgba(30, 58, 138, .25); }
.quiz-card h2 { margin: 0 0 .25rem !important; padding: 0 !important; border: 0 !important; color: #fff !important; font-size: 1.3rem; }
.quiz-card > p { margin: 0 0 1rem; opacity: .9; }
.quiz-card .quiz-item { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
  padding: .8rem 1rem; border-radius: 12px; background: rgba(255, 255, 255, .12); border: 1px solid rgba(255, 255, 255, .2); }
.quiz-card .quiz-item + .quiz-item { margin-top: .6rem; }
.quiz-card .quiz-item strong { display: block; color: #fff; }
.quiz-card .quiz-item small { opacity: .85; }
.quiz-card .quiz-actions { display: flex; gap: .5rem; flex-wrap: wrap; }
.quiz-card a.quiz-btn { display: inline-block; padding: .5rem 1rem; border-radius: 10px; font-weight: 700; text-decoration: none;
  background: #fff; color: #1d4ed8 !important; }
.quiz-card a.quiz-btn.ghost { background: transparent; color: #fff !important; border: 1px solid rgba(255, 255, 255, .5); }
.quiz-card a.quiz-btn:hover { filter: brightness(.95); }
.quiz-card .quiz-all { display: inline-block; margin-top: .9rem; color: #fff !important; font-size: .9rem; opacity: .9; }

/* Footer social icons (inline SVG, no third-party icon service) */
.portal-socials { display: flex; gap: .75rem; align-items: center; }
.portal-socials a { color: var(--sy-c-foot-text, var(--sy-c-light)); display: inline-flex; }
.portal-socials a:hover { color: var(--sy-c-link); }
.portal-socials svg { width: 20px; height: 20px; }
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
    document.querySelectorAll(".globaltoc a.reference").forEach(function (a) {
      a.classList.toggle("is-done", state.done.has(pageOf(a.href)));
    });
    var holder = document.querySelector(".sidebar-progress");
    if (!state.total) { if (holder) holder.remove(); return; }
    if (!holder) {
      holder = el("div", { class: "sidebar-progress" });
      var anchor = document.querySelector(".globaltoc");
      if (anchor) anchor.insertAdjacentElement("beforebegin", holder); else return;
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
      var next = document.querySelector(".navigation-next a");
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


# Wraps the theme's base.html: brand SEO tags on every docs page and "| Parottasalna" in titles.
# (Shibuya already adds og:type, og:title and twitter:card, so those aren't repeated here.)
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
<meta property="og:site_name" content="{{ brand_name|e }}">
<meta property="og:description" content="{{ brand_description|e }}">
<script type="application/ld+json">{{ brand_json_ld }}</script>
<meta name="portal-quiz-feed" content="{{ quiz_feed_url|e }}">
<meta name="portal-page" content="{{ pagename|e }}">
<meta name="portal-progress" content="{{ progress_url|e }}">
<meta name="portal-docs-root" content="{{ docs_root|e }}">
{%- endblock -%}
"""


# Shibuya runs relative nav URLs through pathto() (docs-relative); ours are site-relative ("/").
NAV_LINKS_TEMPLATE = """<ul>
  {%- for link in theme_nav_links %}
  <li class="link"><a href="{{ link.url|e }}"{% if link.external %} target="_blank" rel="noopener"{% endif %}><span>{{ link.title|e }}</span></a></li>
  {%- endfor %}
</ul>
"""

# Footer: copyright line plus brand social icons as inline SVG (Shibuya's icons load from a CDN).
FOOT_COPYRIGHT_TEMPLATE = """<div class="sy-foot-copyright"><p>&copy; {{ brand_name|e }} \u00b7 {{ brand_author|e }} \u00b7 <a href="/privacy/">Privacy Policy</a></p></div>
"""


def _foot_socials_template():
    links = "".join(
        f'<a href="{link["url"]}" target="_blank" rel="noopener" aria-label="{link["name"]}" title="{link["name"]}">'
        f'<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="{link["icon"]}"/></svg></a>'
        for link in branding.SOCIAL_LINKS
    )
    return f'<div class="portal-socials">{links}</div>\n'


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
    if settings.SPHINX_THEME == "shibuya":
        nav_links = [{"title": "All courses", "url": "/"}]
        if not course.is_common:  # common-course readers mostly aren't enrolled, so no quizzes
            nav_links.append({"title": "Quizzes", "url": reverse("quiz_list", args=[course.slug])})
        nav_links.append({"title": "YouTube", "url": branding.YOUTUBE, "external": True})
        options = {
            "accent_color": "blue",
            "announcement": (
                f'{branding.CADENCE} <a href="{branding.YOUTUBE_SUBSCRIBE}" target="_blank" '
                f'rel="noopener">Subscribe to {branding.NAME} on YouTube</a>'
            ),
            "nav_links": nav_links,
            "globaltoc_expand_depth": 1,
            # No "Open in ChatGPT/Claude" links: they would send students' page URLs to third parties.
            "show_ai_links": False,
            # Social icons come from our own footer template (inline SVG, no icon CDN).
            "nav_socials": [],
            "foot_socials": [],
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
    if settings.SPHINX_THEME == "shibuya":
        (templates / "base.html").write_text(BASE_TEMPLATE, encoding="utf-8")
        (templates / "components").mkdir()
        (templates / "partials").mkdir()
        (templates / "components" / "nav-links.html").write_text(NAV_LINKS_TEMPLATE, encoding="utf-8")
        (templates / "components" / "foot-copyright.html").write_text(FOOT_COPYRIGHT_TEMPLATE, encoding="utf-8")
        (templates / "partials" / "foot-socials.html").write_text(_foot_socials_template(), encoding="utf-8")


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
