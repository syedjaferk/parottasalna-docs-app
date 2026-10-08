import html
import re

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_safe

from courses.models import Course
from courses.security import api_login_required, no_store
from courses.services import can_track, chapters, user_can_access

from .models import BODY_MAX, NOTES_PER_COURSE_MAX, QUOTE_MAX, Note

_ANCHOR = re.compile(r"[A-Za-z0-9_.:-]{0,200}")


def _notable_pages(course):
    """Pages a note can belong to, in course order: the landing page plus every chapter."""
    return ["index", *chapters(course)]


def _tracked_course(request, slug):
    """The course, if this user may keep notes in it; else None (nothing is stored)."""
    course = Course.objects.filter(slug=slug, is_active=True).first()
    if course is None or not can_track(request.user, course):
        return None
    return course


def _clean(request, course, require_page):
    """Validate a create/update POST. Returns (fields, error)."""
    fields = {}
    if require_page:
        page = request.POST.get("page", "")
        if page not in set(_notable_pages(course)):
            return None, "Unknown page"
        anchor = request.POST.get("anchor", "")
        if not _ANCHOR.fullmatch(anchor):
            return None, "Invalid section"
        fields.update(page=page, anchor=anchor, quote=request.POST.get("quote", "").strip()[:QUOTE_MAX])
    body = request.POST.get("body", "").strip()
    if not body:
        return None, "The note is empty"
    if len(body) > BODY_MAX:
        return None, f"Notes can be at most {BODY_MAX} characters"
    fields["body"] = body
    return fields, None


@require_safe
@ensure_csrf_cookie  # the docs page POSTs new notes with this token
def notes_json(request, slug):
    """This user's notes for one docs page. `enabled` is false for anyone not enrolled."""
    course = Course.objects.filter(slug=slug, is_active=True).first()
    if course is None or not user_can_access(request.user, course):
        raise Http404
    if not can_track(request.user, course):
        return no_store(JsonResponse({"enabled": False}))
    page = request.GET.get("page", "")
    notes = Note.objects.filter(user=request.user, course=course, page=page)
    return no_store(JsonResponse({
        "enabled": True,
        "create_url": reverse("note_create", args=[course.slug]),
        "all_url": reverse("course_notes", args=[course.slug]),
        "course_count": Note.objects.filter(user=request.user, course=course).count(),
        "notes": [note.as_json() for note in notes],
    }))


@require_POST
@api_login_required
def note_create(request, slug):
    course = _tracked_course(request, slug)
    if course is None:
        return JsonResponse({"error": "Not found"}, status=404)
    fields, error = _clean(request, course, require_page=True)
    if error:
        return JsonResponse({"error": error}, status=400)
    if Note.objects.filter(user=request.user, course=course).count() >= NOTES_PER_COURSE_MAX:
        return JsonResponse({"error": "You have reached the note limit for this course"}, status=400)
    note = Note.objects.create(user=request.user, course=course, **fields)
    return no_store(JsonResponse(note.as_json(), status=201))


@require_POST
@api_login_required
def note_update(request, slug, pk):
    course = _tracked_course(request, slug)
    # Filtering by user means another student's note id is simply "not found".
    note = course and Note.objects.filter(pk=pk, user=request.user, course=course).first()
    if not note:
        return JsonResponse({"error": "Not found"}, status=404)
    fields, error = _clean(request, course, require_page=False)
    if error:
        return JsonResponse({"error": error}, status=400)
    note.body = fields["body"]
    note.save(update_fields=["body", "updated_at"])
    return no_store(JsonResponse(note.as_json()))


@require_POST
@api_login_required
def note_delete(request, slug, pk):
    course = _tracked_course(request, slug)
    deleted = course and Note.objects.filter(pk=pk, user=request.user, course=course).delete()[0]
    if not deleted:
        return JsonResponse({"error": "Not found"}, status=404)
    return no_store(JsonResponse({"deleted": pk}))


def _grouped(request, course):
    """[(page, title, notes)] in course order, only pages that have notes."""
    order = {page: i for i, page in enumerate(_notable_pages(course))}
    by_page = {}
    for note in Note.objects.filter(user=request.user, course=course):
        by_page.setdefault(note.page, []).append(note)
    titles = _page_titles(course, by_page)
    return [(page, titles.get(page, page), by_page[page])
            for page in sorted(by_page, key=lambda p: (order.get(p, len(order)), p))]


def _page_titles(course, pages):
    """Read each page's <title> from the built HTML (first part, before the course name)."""
    titles = {}
    for page in pages:
        path = course.html_dir / f"{page}.html"
        try:
            head = path.read_text(encoding="utf-8", errors="ignore")[:4000]
        except OSError:
            continue
        match = re.search(r"<title>(.*?)</title>", head, re.S)
        if match:
            title = re.sub(r"\s+", " ", match.group(1)).strip()
            titles[page] = html.unescape(title.rsplit(" - ", 1)[0].split(" | ")[0])
    return titles


@login_required
@require_safe
def course_notes(request, slug):
    """All of this user's notes in one course, grouped by chapter."""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    if not can_track(request.user, course):
        raise Http404
    groups = _grouped(request, course)
    response = render(request, "notes/course_notes.html", {
        "course": course,
        "groups": groups,
        "total": sum(len(notes) for _, _, notes in groups),
        "docs_root": reverse("course_docs", args=[course.slug]),
    })
    return no_store(response)


@login_required
@require_safe
def course_notes_markdown(request, slug):
    """Download every note in a course as one Markdown file."""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    if not can_track(request.user, course):
        raise Http404
    base = request.build_absolute_uri(reverse("course_docs", args=[course.slug]))
    lines = [f"# My notes · {course.title}", "", f"_Exported {timezone.localdate():%d %b %Y}_", ""]
    for page, title, notes in _grouped(request, course):
        lines += [f"## {title}", "", f"<{base}{page}.html>", ""]
        for note in notes:
            if note.quote:
                lines += ["> " + line for line in note.quote.splitlines()] + [""]
            lines += [note.body, "", f"_{note.updated_at:%d %b %Y}_ · <{base}{page}.html#{note.anchor}>"
                      if note.anchor else f"_{note.updated_at:%d %b %Y}_", "", "---", ""]
    response = HttpResponse("\n".join(lines), content_type="text/markdown; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="notes-{course.slug}.md"'
    return no_store(response)
