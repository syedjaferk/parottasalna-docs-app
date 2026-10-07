import mimetypes
from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousFileOperation
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils._os import safe_join

from .models import Course
from .services import accessible_courses, user_can_access


def home(request):
    if not request.user.is_authenticated:
        # Public landing page (indexable) instead of a redirect.
        return render(request, "courses/login.html", {"next": ""})
    return render(request, "courses/dashboard.html", {"courses": accessible_courses(request.user)})


def login_page(request):
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "courses/login.html", {"next": request.GET.get("next", "")})


@login_required
def course_docs(request, slug, path=""):
    """Authorise, then hand back one file of the course's built Sphinx site."""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    if not user_can_access(request.user, course):
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
        "Disallow: /courses/",
        "Disallow: /logout/",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


def sitemap_xml(request):
    return render(request, "sitemap.xml", {"home_url": request.build_absolute_uri(reverse("home"))},
                  content_type="application/xml")
