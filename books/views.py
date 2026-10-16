import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import render
from django.views.decorators.http import require_safe

from courses.cache import cache_for_anonymous

from .library import get_book

_IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}  # no SVG: it could carry scripts


@require_safe
@cache_for_anonymous(60)
def book_index(request):
    return render(request, "books/index.html", {"book": get_book()})


@require_safe
@cache_for_anonymous(60)
def book_chapter(request, slug):
    book = get_book()
    chapters = book.chapters
    index = next((i for i, c in enumerate(chapters) if c.slug == slug), None)
    if index is None:
        raise Http404
    return render(request, "books/chapter.html", {
        "book": book,
        "chapter": chapters[index],
        "prev": chapters[index - 1] if index else None,
        "next": chapters[index + 1] if index + 1 < len(chapters) else None,
    })


@require_safe
def book_media(request, name):
    root = (Path(settings.BOOK_ROOT) / "images").resolve()
    target = (root / name).resolve()
    if target.parent != root or target.suffix.lower() not in _IMAGE_TYPES or not target.is_file():
        raise Http404
    response = FileResponse(open(target, "rb"), content_type=mimetypes.guess_type(target.name)[0])
    response["Cache-Control"] = "public, max-age=86400"
    return response
