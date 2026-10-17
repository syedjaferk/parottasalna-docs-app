import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Count, Q

from django.db.models import F

from .models import Course, PageProgress, PageVisit

_SPLIT = re.compile(r"[,;\s]+")


def parse_emails(text):
    """Split free text into (valid_unique_lowercase_emails, invalid_tokens)."""
    valid, invalid, seen = [], [], set()
    for token in _SPLIT.split(text or ""):
        token = token.strip().lower()
        if not token:
            continue
        try:
            validate_email(token)
        except ValidationError:
            invalid.append(token)
            continue
        if token not in seen:
            seen.add(token)
            valid.append(token)
    return valid, invalid


def public_courses():
    """Common courses: readable by anyone, signed in or not."""
    return Course.objects.filter(is_active=True, is_common=True)


def accessible_courses(user):
    """Active courses this user may open."""
    if not user.is_authenticated:
        return public_courses()
    active = Course.objects.filter(is_active=True)
    if user.is_staff:
        return active
    if not user.email:
        return active.filter(is_common=True)
    courses = active.filter(Q(is_common=True) | Q(enrollments__email__iexact=user.email)).distinct()
    if not _has_pro(user):
        courses = courses.exclude(access=Course.Access.PRO)  # a lapsed membership closes Pro courses again
    return courses


def _has_pro(user) -> bool:
    from billing.services import has_pro  # imported here: billing depends on courses, not the reverse

    return has_pro(user)


def is_enrolled(user, course) -> bool:
    return bool(user.is_authenticated and user.email) and course.enrollments.filter(email__iexact=user.email).exists()


def enrol_decision(user, course):
    """Can this user enrol themselves? Returns (allowed, reason_code). Reason codes drive the catalogue button."""
    if not user.is_authenticated:
        return False, "login"
    if is_enrolled(user, course):
        return False, "enrolled"
    if course.access == Course.Access.FREE:
        return True, "free"
    if course.access == Course.Access.PRO:
        return (True, "pro") if _has_pro(user) else (False, "needs_pro")
    return False, "invite"


def enrol_user(user, course):
    """Enrol `user` in `course` if the course's access rules allow it. Returns (enrolment, reason_code)."""
    from .models import Enrollment

    allowed, reason = enrol_decision(user, course)
    if not allowed:
        return None, reason
    if not user.email:
        return None, "no_email"
    enrolment, _ = Enrollment.objects.get_or_create(
        course=course, email=user.email.strip().lower(),
        defaults={"user": user, "source": Enrollment.Source.PRO if reason == "pro" else Enrollment.Source.SELF})
    return enrolment, reason


def can_track(user, course) -> bool:
    """Progress and quiz scores are stored only for students enrolled in this course (and staff).

    Reading a common course needs no enrolment, but nothing is recorded for such readers.
    """
    if not user.is_authenticated or not course.is_active:
        return False
    if user.is_staff:
        return True
    return bool(user.email) and course.enrollments.filter(email__iexact=user.email).exists()


def user_can_access(user, course) -> bool:
    if not course.is_active:
        return False
    return accessible_courses(user).filter(pk=course.pk).exists()


_SPHINX_PAGES = {"search.html", "genindex.html", "py-modindex.html"}


def doc_pages(course):
    """Relative paths of a course's built pages, skipping Sphinx's search/index pages and assets."""
    root = course.html_dir
    if not root.is_dir():
        return []
    pages = []
    for path in root.rglob("*.html"):
        rel = path.relative_to(root)
        if path.name in _SPHINX_PAGES or any(part.startswith(("_", ".")) for part in rel.parts):
            continue
        pages.append(rel.as_posix())
    return sorted(pages)


def chapters(course):
    """Page names students can mark complete: every built page except the course landing page."""
    return [page[: -len(".html")] for page in doc_pages(course) if page != "index.html"]


def course_progress(user, courses):
    """{course_id: (completed, total)} for courses where this user's progress is tracked."""
    courses = [course for course in courses if can_track(user, course)]
    if not courses:
        return {}
    done = {}
    for course_id, page in PageProgress.objects.filter(user=user, course__in=courses).values_list("course_id", "page"):
        done.setdefault(course_id, set()).add(page)
    result = {}
    for course in courses:
        pages = set(chapters(course))
        result[course.pk] = (len(pages & done.get(course.pk, set())), len(pages))
    return result


def record_visit(user, course, page):
    """Remember that a signed-in user opened a chapter (page name without .html). Cheap upsert."""
    if not user.is_authenticated or page in ("", "index"):
        return
    updated = PageVisit.objects.filter(user=user, course=course, page=page).update(views=F("views") + 1)
    if not updated:
        PageVisit.objects.get_or_create(user=user, course=course, page=page)


def dropoff(course):
    """Per chapter, in reading order: how many learners opened it, finished it, and how many were lost.

    `reach` is the share of the first chapter's readers who got this far, so the numbers fall as people
    give up. `lost` is the share of the previous chapter's readers who never opened this one.
    """
    pages = chapters(course)
    opened, done = {}, {}
    for page, n in PageVisit.objects.filter(course=course).values_list("page").annotate(n=Count("user", distinct=True)):
        opened[page] = n
    for page, n in PageProgress.objects.filter(course=course).values_list("page").annotate(n=Count("user", distinct=True)):
        done[page] = n
    rows, first, prev = [], None, None
    for page in pages:
        readers, finished = opened.get(page, 0), done.get(page, 0)
        readers = max(readers, finished)
        first = readers if first is None else first
        lost = round(100 * (prev - readers) / prev) if prev else 0
        rows.append({"page": page, "readers": readers, "finished": finished,
                     "finish_rate": round(100 * finished / readers) if readers else 0,
                     "reach": round(100 * readers / first) if first else 0,
                     "lost": max(lost, 0), "alarm": bool(prev and lost >= 30 and prev >= 5)})
        prev = readers
    return rows
