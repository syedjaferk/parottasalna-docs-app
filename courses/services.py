import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import Course

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


def accessible_courses(user):
    """Active courses this user may open."""
    if not user.is_authenticated:
        return Course.objects.none()
    active = Course.objects.filter(is_active=True)
    if user.is_staff:
        return active
    if not user.email:
        return Course.objects.none()
    return active.filter(enrollments__email__iexact=user.email).distinct()


def user_can_access(user, course) -> bool:
    if not course.is_active:
        return False
    return accessible_courses(user).filter(pk=course.pk).exists()
