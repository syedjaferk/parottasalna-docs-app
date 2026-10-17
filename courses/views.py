import mimetypes
from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
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
from books.library import get_book
from jobs.models import Job
from live.services import sessions_for
from smells.services import daily_context
from streaks.services import has_streak, record_action, summary as streak_summary

from .models import Course, LearningPath, PageProgress
from .security import api_login_required, no_store
from .services import (
    accessible_courses,
    can_track,
    chapters,
    course_progress,
    doc_pages,
    enrol_decision,
    enrol_user,
    is_enrolled,
    public_courses,
    record_visit,
    dropoff,
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
    return render(request, "courses/login.html", {
        "next": next_url, "free_courses": free, "live": sessions_for(request.user),
        "open_signup": settings.OPEN_SIGNUP,
    })


def _front_door(request):
    """The public home page: who it is for, what is free, and the flagship learning paths."""
    free = cache.get_or_set(
        "landing:free_courses",
        lambda: list(public_courses().filter(build_status=Course.BuildStatus.OK)), 60)
    return render(request, "landing/home.html", {
        "paths": LearningPath.objects.filter(is_active=True)[:3], "free_courses": free,
        "live": sessions_for(request.user)})


def home(request):
    if not request.user.is_authenticated:
        # Public landing page (indexable) instead of a redirect.
        return _front_door(request)
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
        "has_enrolment": any(c.tracked for c in courses),
        "streak": streak_summary(request.user) if has_streak(request.user) else None,
        "live": sessions_for(request.user),
        "daily_smell": daily_context(request.user),
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
        if request.user.is_authenticated and request.method == "GET":
            record_visit(request.user, course, rel.as_posix()[: -len(".html")])
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
    return render(request, "courses/privacy.html", {
        "contact_email": settings.CONTACT_EMAIL, "resume_retention_days": settings.RESUME_RETENTION_DAYS,
    })


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /$",
        "Allow: /courses/$",
        "Allow: /pricing/$",
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
    urls.append({"loc": request.build_absolute_uri(reverse("book_index")), "priority": "0.6", "lastmod": None})
    for chapter in get_book().chapters:
        urls.append({"loc": request.build_absolute_uri(chapter.get_absolute_url()), "priority": "0.5", "lastmod": None})
    urls.append({"loc": request.build_absolute_uri(reverse("job_list")), "priority": "0.6", "lastmod": None})
    for job in Job.visible().only("pk", "title", "company", "updated_at"):
        urls.append({"loc": request.build_absolute_uri(job.get_absolute_url()), "priority": "0.4",
                     "lastmod": job.updated_at})
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
        record_action(request.user)  # counts toward the reading streak
    else:
        PageProgress.objects.filter(user=request.user, course=course, page=page).delete()
    done = PageProgress.objects.filter(user=request.user, course=course, page__in=pages).count()
    return no_store(JsonResponse({"page": page, "completed": completed == "true", "done": done, "total": len(pages)}))


# --- Course catalogue ------------------------------------------------------------------------------

def _course_state(request, course, open_cohorts):
    """What the catalogue button should say for this visitor: a dict with a `code` and the target URL."""
    user = request.user
    if user.is_authenticated and (is_enrolled(user, course) or user.is_staff) and user_can_access(user, course):
        return {"code": "enrolled", "label": "Continue learning" if course.build_status == "ok" else "Enrolled"}
    allowed, reason = enrol_decision(user, course)
    if allowed:
        return {"code": "enrol", "label": "Enrol free" if reason == "free" else "Enrol with Pro"}
    if reason == "login" and course.access == Course.Access.FREE:
        read = course.is_common and course.build_status == Course.BuildStatus.OK
        return {"code": "login", "label": "Sign in to enrol", "can_read": read}
    if reason == "login" and course.access == Course.Access.PRO:
        return {"code": "pro", "label": "Unlock with Pro"}
    if reason == "login":
        reason = "invite"  # invite-only: signed-out visitors see the same call to action as everyone else
    if reason == "needs_pro":
        return {"code": "pro", "label": "Unlock with Pro"}
    if course.pk in open_cohorts:
        return {"code": "cohort", "label": "Join the next batch"}
    return {"code": "invite", "label": "Invite only"}


@require_safe
def catalog(request):
    """Every listed course, with the right call to action for this visitor."""
    from billing.models import Cohort

    open_cohorts = set(Cohort.objects.filter(status=Cohort.Status.OPEN, is_listed=True)
                       .exclude(course=None).values_list("course_id", flat=True))
    courses = list(Course.objects.filter(is_active=True, is_listed=True))
    for course in courses:
        course.state = _course_state(request, course, open_cohorts)
        course.outcome_list = [line.strip() for line in course.outcomes.splitlines() if line.strip()][:3]
    groups = [
        ("Free courses", "Enrol in one click and track your progress.", [c for c in courses if c.access == Course.Access.FREE]),
        ("Pro courses", "Included with a Pro membership.", [c for c in courses if c.access == Course.Access.PRO]),
        ("Cohort and invite-only courses", "Taught live in batches. Join a batch to be enrolled.",
         [c for c in courses if c.access == Course.Access.INVITE]),
    ]
    return render(request, "courses/catalog.html", {"groups": [g for g in groups if g[2]], "total": len(courses)})


@require_safe
def course_detail(request, slug):
    from billing.models import Cohort

    course = get_object_or_404(Course, slug=slug, is_active=True, is_listed=True)
    open_cohorts = set(Cohort.objects.filter(status=Cohort.Status.OPEN, course=course).values_list("course_id", flat=True))
    return render(request, "courses/course_detail.html", {
        "course": course, "state": _course_state(request, course, open_cohorts),
        "outcomes": [line.strip() for line in course.outcomes.splitlines() if line.strip()],
        "chapter_count": len(chapters(course)) if course.build_status == Course.BuildStatus.OK else 0,
    })


@require_POST
def enroll(request, slug):
    """Enrol the signed-in user in a course, if its access rules allow it. This is what grants the permission."""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    if not request.user.is_authenticated:
        return redirect_to_login(reverse("course_detail", args=[slug]))
    enrolment, reason = enrol_user(request.user, course)
    notes = {
        "enrolled": "You are already enrolled in this course.",
        "needs_pro": "This course is part of Pro. Pick a plan to unlock it.",
        "invite": "This course is invite-only. Join a batch to be enrolled.",
        "no_email": "Your account has no email address, so we cannot enrol you.",
    }
    if enrolment:
        messages.success(request, f"You are enrolled in {course.title}.")
        return redirect("course_docs", slug=slug) if course.build_status == Course.BuildStatus.OK else redirect("course_detail", slug=slug)
    messages.info(request, notes.get(reason, "Could not enrol you in this course."))
    return redirect("pricing" if reason == "needs_pro" else "course_detail", **({} if reason == "needs_pro" else {"slug": slug}))


@require_safe
@staff_member_required
def insights(request, slug=None):
    """Staff-only: where do learners stop reading? One course's chapter funnel, or the list of courses."""
    if slug is None:
        courses = Course.objects.filter(is_active=True).annotate(
            readers=Count("page_visits__user", distinct=True), finishers=Count("page_progress__user", distinct=True))
        return render(request, "courses/insights_index.html", {"courses": courses})
    course = get_object_or_404(Course, slug=slug, is_active=True)
    return render(request, "courses/insights.html", {"course": course, "rows": dropoff(course)})


# --- Learning paths --------------------------------------------------------------------------------

def _path_steps(path, user):
    """Steps in order, skipping a tool whose page does not exist on this site, with a done/enrolled flag."""
    from django.urls import Resolver404, resolve

    done_pages = {}
    if user.is_authenticated:
        for course_id, n in PageProgress.objects.filter(user=user).values_list("course_id").annotate(n=Count("id")):
            done_pages[course_id] = n
    rows = []
    for step in path.steps.select_related("course"):
        row = {"step": step, "href": "", "state": "", "title": step.label, "course": step.course}
        if step.kind == "course":
            course = step.course
            if course is None or not course.is_active:
                continue
            row["href"] = reverse("course_detail", args=[course.slug])
            if user.is_authenticated and is_enrolled(user, course):
                row["state"] = "enrolled"
                row["done"] = done_pages.get(course.pk, 0)
        else:
            try:
                resolve(step.url)
            except Resolver404:
                continue
            row["href"] = step.url
        rows.append(row)
    return rows


@require_safe
def paths(request):
    items = [(p, _path_steps(p, request.user)) for p in LearningPath.objects.filter(is_active=True)]
    return render(request, "courses/paths.html", {"items": items})


@require_safe
def path_detail(request, slug):
    path = get_object_or_404(LearningPath, slug=slug, is_active=True)
    return render(request, "courses/path_detail.html", {"path": path, "rows": _path_steps(path, request.user)})
