from django.templatetags.static import static
from django.urls import reverse
from django.utils.safestring import mark_safe

from . import branding


def brand(request):
    """Brand details plus absolute URLs needed for canonical / Open Graph tags on every page."""
    site_url = request.build_absolute_uri(reverse("home"))
    logo_url = request.build_absolute_uri(static("brand/logo-512.png"))
    return {
        "brand": branding,
        "site_url": site_url,
        "canonical_url": request.build_absolute_uri(request.path),
        "og_image_url": request.build_absolute_uri(static("brand/og-image.png")),
        "brand_json_ld": mark_safe(branding.json_ld(site_url, logo_url)),
    }
