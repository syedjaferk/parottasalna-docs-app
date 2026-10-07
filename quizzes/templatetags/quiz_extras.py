from django import template
from django.utils.safestring import mark_safe
from markdown_it import MarkdownIt

register = template.Library()

# Raw HTML is disabled, so authors' markdown can't inject markup or scripts.
_md = MarkdownIt("commonmark", {"html": False, "linkify": False})


@register.filter
def markdown(text):
    return mark_safe(_md.render(text or ""))


@register.filter
def markdown_inline(text):
    return mark_safe(_md.renderInline(text or ""))


@register.filter
def get_item(mapping, key):
    return mapping.get(key) if mapping else None
