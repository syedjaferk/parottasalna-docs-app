from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

from .models import Enrollment


def verified_email(sociallogin):
    """The Google-verified email for this login, lowercased, or None."""
    for address in sociallogin.email_addresses:
        if address.verified and address.email:
            return address.email.strip().lower()
    return None


class PortalAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # No username/password registration. Accounts come from Google only.
        return False


class PortalSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """Attach Google to a pre-created user (e.g. the first superuser) with the same email."""
        if sociallogin.is_existing:
            return
        email = verified_email(sociallogin)
        if not email:
            return
        User = get_user_model()
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user:
            sociallogin.connect(request, user)

    def is_open_for_signup(self, request, sociallogin):
        """Only let brand-new users in if an admin has enrolled their email in a course."""
        email = verified_email(sociallogin)
        return bool(email) and Enrollment.objects.filter(email=email).exists()
