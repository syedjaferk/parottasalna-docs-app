import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q

from .models import Course, PageProgress

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
    return active.filter(Q(is_common=True) | Q(enrollments__email__iexact=user.email)).distinct()


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
