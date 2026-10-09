import mimetypes
from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import SuspiciousFileOperation
from django.db.models import Count, Q
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils._os import safe_join
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_safe

from blog.models import Post

from .models import Course, PageProgress
from .security import api_login_required, no_store
from .services import (
    accessible_courses,
    can_track,
    chapters,
    course_progress,
    doc_pages,
    public_courses,
    user_can_access,
)


def _landing(request, next_url=""):
    # The page itself can't be cached (its sign-in form carries a per-visitor CSRF token), so
    # cache just its database query.
    free = cache.get_or_set(
        "landing:free_courses",
        lambda: list(public_courses().filter(build_status=Course.BuildStatus.OK)),
        60,
    )
    return render(request, "courses/login.html", {"next": next_url, "free_courses": free})


def home(request):
    if not request.user.is_authenticated:
        # Public landing page (indexable) instead of a redirect.
        return _landing(request)
    courses = list(accessible_courses(request.user).annotate(
        quiz_count=Count("quizzes", filter=Q(quizzes__is_published=True), distinct=True),
        deck_count=Count("decks", filter=Q(decks__is_published=True), distinct=True),
    ))
    progress = course_progress(request.user, courses)
    for course in courses:
        course.tracked = course.pk in progress  # enrolled (or staff): progress bar + quizzes
        course.done, course.total = progress.get(course.pk, (0, 0))
        course.percent = round(100 * course.done / course.total) if course.total else 0
    return render(request, "courses/dashboard.html", {
        "courses": courses,
        "enrolled_courses": [c for c in courses if not c.is_common],
        "common_courses": [c for c in courses if c.is_common],
    })


def login_page(request):
    if request.user.is_authenticated:
        return redirect("home")
    return _landing(request, request.GET.get("next", ""))


def course_docs(request, slug, path=""):
    """Authorise, then hand back one file of the course's built Sphinx site.

    Common courses are public; everything else needs a signed-in, enrolled user.
    """
    course = Course.objects.filter(slug=slug, is_active=True).first()
    if course is None or not user_can_access(request.user, course):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())  # same for unknown slugs: reveal nothing
        raise Http404  # 404, not 403: don't reveal which courses exist

    html_root = course.html_dir.resolve()
    if not html_root.is_dir():
        return render(request, "courses/docs_not_built.html", {"course": course}, status=404)

    relative = path or "index.html"
    try:
        target = Path(safe_join(html_root, relative)).resolve()
    except SuspiciousFileOperation:
        raise Http404
    if target.is_dir():
        target = target / "index.html"
    if not target.is_file() or not target.is_relative_to(html_root):
        raise Http404

    rel = target.relative_to(html_root)
    if any(part.startswith(".") for part in rel.parts):  # .buildinfo etc.
        raise Http404

    content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
    if settings.USE_X_ACCEL_REDIRECT:
        response = HttpResponse(content_type=content_type)
        response["X-Accel-Redirect"] = (
            f"{settings.X_ACCEL_PREFIX}{course.slug}/html/{quote(rel.as_posix())}"
        )
    else:
        response = FileResponse(open(target, "rb"), content_type=content_type)
    if target.suffix == ".html":
        # Pages: always revalidate, so a rebuilt chapter shows up straight away.
        response["Cache-Control"] = "private, no-cache"
    else:
        # CSS/JS/images: each page links them with a ?v=<hash> that changes on every rebuild, so
        # browsers can keep them for a day instead of re-checking ~17 files on every page view.
        # "private": never stored by shared caches, since most courses need a login.
        response["Cache-Control"] = "private, max-age=86400"
    return response


def privacy(request):
    """Public privacy policy (linked from every page and from Google's OAuth consent screen)."""
    return render(request, "courses/privacy.html", {"contact_email": settings.CONTACT_EMAIL})


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /$",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        *[f"Allow: /courses/{slug}/docs/" for slug in public_courses().values_list("slug", flat=True)],
        "Disallow: /courses/",
        "Disallow: /logout/",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


def sitemap_xml(request):
    urls = [
        {"loc": request.build_absolute_uri(reverse("home")), "priority": "1.0", "lastmod": None},
        {"loc": request.build_absolute_uri(reverse("privacy")), "priority": "0.3", "lastmod": None},
        {"loc": request.build_absolute_uri(reverse("blog_index")), "priority": "0.8", "lastmod": None},
    ]
    for post in Post.objects.filter(is_published=True).only("slug", "imported_at"):
        urls.append({"loc": request.build_absolute_uri(post.get_absolute_url()), "priority": "0.5",
                     "lastmod": post.imported_at})
    for course in public_courses().filter(build_status=Course.BuildStatus.OK):
        for page in doc_pages(course):
            path = "" if page == "index.html" else page
            urls.append({
                "loc": request.build_absolute_uri(reverse("course_docs", args=[course.slug]) + quote(path)),
                "priority": "0.8" if not path else "0.6",
                "lastmod": course.last_built_at,
            })
    return render(request, "sitemap.xml", {"urls": urls}, content_type="application/xml")


def _accessible_course(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    if not user_can_access(request.user, course):
        raise Http404
    return course


@require_safe
@ensure_csrf_cookie  # the docs page POSTs "Mark as complete" with this token
def progress_json(request, slug):
    """Which pages this user has completed, for the docs' "Mark as complete" button and sidebar ticks.

    `tracking` is false for anyone not enrolled in the course: the docs then show no progress UI at all.
    """
    course = _accessible_course(request, slug)
    if not can_track(request.user, course):
        return no_store(JsonResponse({"tracking": False}))
    pages = chapters(course)
    done = set(PageProgress.objects.filter(user=request.user, course=course).values_list("page", flat=True))
    return no_store(JsonResponse({
        "tracking": True,
        "update_url": reverse("course_progress_update", args=[course.slug]),
        "total": len(pages),
        "completed": sorted(done & set(pages)),
    }))


@require_POST
@api_login_required
def progress_update(request, slug):
    """Mark/unmark one page. Server-side checks: CSRF, signed in, enrolled, page belongs to the course."""
    course = Course.objects.filter(slug=slug, is_active=True).first()
    if course is None or not can_track(request.user, course):
        return JsonResponse({"error": "Not found"}, status=404)  # not enrolled: nothing is stored
    pages = set(chapters(course))
    page = request.POST.get("page", "")
    completed = request.POST.get("completed")
    if page not in pages or completed not in ("true", "false"):
        return JsonResponse({"error": "Invalid page or completed value"}, status=400)
    if completed == "true":
        PageProgress.objects.get_or_create(user=request.user, course=course, page=page)
    else:
        PageProgress.objects.filter(user=request.user, course=course, page=page).delete()
    done = PageProgress.objects.filter(user=request.user, course=course, page__in=pages).count()
    return no_store(JsonResponse({"page": page, "completed": completed == "true", "done": done, "total": len(pages)}))
