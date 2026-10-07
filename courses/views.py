import mimetypes
from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import SuspiciousFileOperation
from django.db.models import Count, Q
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils._os import safe_join

from .models import Course
from .services import accessible_courses, public_courses, user_can_access


def _landing(request, next_url=""):
    free = public_courses().filter(build_status=Course.BuildStatus.OK)
    return render(request, "courses/login.html", {"next": next_url, "free_courses": free})


def home(request):
    if not request.user.is_authenticated:
        # Public landing page (indexable) instead of a redirect.
        return _landing(request)
    courses = list(accessible_courses(request.user).annotate(
        quiz_count=Count("quizzes", filter=Q(quizzes__is_published=True), distinct=True)
    ))
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
    response["Cache-Control"] = "private, no-cache"
    return response


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


def _public_doc_pages(course):
    """Relative paths of a public course's built pages (skipping Sphinx's search/index pages)."""
    root = course.html_dir
    if not root.is_dir():
        return []
    skip = {"search.html", "genindex.html", "py-modindex.html"}
    return sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob("*.html")
        if p.name not in skip and not any(part.startswith(("_", ".")) for part in p.relative_to(root).parts)
    )


def sitemap_xml(request):
    urls = [{"loc": request.build_absolute_uri(reverse("home")), "priority": "1.0", "lastmod": None}]
    for course in public_courses().filter(build_status=Course.BuildStatus.OK):
        for page in _public_doc_pages(course):
            path = "" if page == "index.html" else page
            urls.append({
                "loc": request.build_absolute_uri(reverse("course_docs", args=[course.slug]) + quote(path)),
                "priority": "0.8" if not path else "0.6",
                "lastmod": course.last_built_at,
            })
    return render(request, "sitemap.xml", {"urls": urls}, content_type="application/xml")
