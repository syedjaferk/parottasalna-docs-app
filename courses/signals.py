from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import Enrollment


@receiver(user_logged_in)
def link_enrollments(sender, request, user, **kwargs):
    """On login, attach the user to any enrollments created for their email beforehand."""
    if user.email:
        Enrollment.objects.filter(email__iexact=user.email, user__isnull=True).update(user=user)
