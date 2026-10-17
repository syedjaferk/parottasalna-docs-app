import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def mini(text):
    """Escape, then turn **bold** and `code` into tags. Only these two are supported, so the output is safe."""
    out = escape(str(text))
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    return mark_safe(out)
