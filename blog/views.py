import json
import mimetypes
from pathlib import Path

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.utils._os import safe_join
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_safe

from courses import branding
from courses.cache import cache_for_anonymous

from .models import Post, PostAsset, Tag

PER_PAGE = 12


def published():
    return Post.objects.filter(is_published=True)


@require_safe
@cache_for_anonymous(60)
def blog_index(request):
    posts = published().prefetch_related("tags")
    q = request.GET.get("q", "").strip()[:100]
    category = request.GET.get("category", "").strip()
    tag_slug = request.GET.get("tag", "").strip()
    active_tag = None
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(category__icontains=q))
    if category:
        posts = posts.filter(category_slug=category)
    if tag_slug:
        active_tag = Tag.objects.filter(slug=tag_slug).first()
        posts = posts.filter(tags__slug=tag_slug)
    page = Paginator(posts, PER_PAGE).get_page(request.GET.get("page"))
    categories = (published().exclude(category="").values("category", "category_slug")
                  .annotate(n=Count("id")).order_by("-n", "category")[:14])
    active_category = next((c["category"] for c in categories if c["category_slug"] == category), None) \
        or published().filter(category_slug=category).values_list("category", flat=True).first()
    filtered = bool(q or category or tag_slug)
    return render(request, "blog/index.html", {
        "page": page,
        "q": q,
        "categories": categories,
        "category": category,
        "active_category": active_category,
        "active_tag": active_tag,
        "filtered": filtered,
        "featured": None if filtered or page.number > 1 else page.object_list[0] if page.object_list else None,
        "total": published().count(),
    })


@require_safe
@cache_for_anonymous(60)
def blog_post(request, slug):
    post = get_object_or_404(published().prefetch_related("tags"), slug=slug)
    related = {p.slug: p for p in published().filter(slug__in=post.related_slugs)}
    related = [related[s] for s in post.related_slugs if s in related][:3]
    if len(related) < 3 and post.category_slug:
        extra = published().filter(category_slug=post.category_slug).exclude(slug=post.slug).exclude(
            slug__in=[p.slug for p in related])[: 3 - len(related)]
        related += list(extra)
    # WordPress stays the canonical home only while it's configured; otherwise this page is the original.
    canonical = (post.wordpress_url if settings.BLOG_WORDPRESS_URL and settings.BLOG_CANONICAL_TO_WORDPRESS
                 and post.wordpress_url else None)
    page_url = request.build_absolute_uri(post.get_absolute_url())
    ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "description": post.excerpt,
        "datePublished": post.published_at.isoformat(),
        "dateModified": post.imported_at.isoformat(),
        "url": canonical or page_url,
        "mainEntityOfPage": canonical or page_url,
        "articleSection": post.category,
        "keywords": [t.name for t in post.tags.all()],
        "author": {"@type": "Person", "name": branding.AUTHOR, "url": branding.WEBSITE},
        "publisher": {"@type": "Organization", "name": branding.NAME, "url": branding.WEBSITE},
    }
    # Safe inside <script>: never let content close the element early.
    ld_json = json.dumps(ld, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return render(request, "blog/post.html", {
        "ld_json": mark_safe(ld_json),
        "post": post,
        "related": related,
        "newer": published().filter(published_at__gt=post.published_at).order_by("published_at").first(),
        "older": published().filter(published_at__lt=post.published_at).order_by("-published_at").first(),
        "canonical": canonical,
    })


@require_safe
def blog_media(request, path):
    """Serve an image from the vault, but only one that a published post actually uses."""
    if not PostAsset.objects.filter(path=path, post__is_published=True).exists():
        raise Http404
    root = Path(settings.BLOG_SRC_ROOT).resolve()
    try:
        target = Path(safe_join(root, path)).resolve()
    except SuspiciousFileOperation:
        raise Http404
    if not target.is_file() or not target.is_relative_to(root):
        raise Http404
    content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
    response = FileResponse(open(target, "rb"), content_type=content_type)
    response["Cache-Control"] = "public, max-age=86400"
    if target.suffix.lower() == ".svg":
        # SVG can carry scripts: never let one run as a page on our domain.
        response["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'; sandbox"
    return response
