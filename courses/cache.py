"""Short server-side caching for public pages.

Only signed-out visitors get cached copies: signed-in pages show the user's name and a logout
form with their CSRF token, so they are always rendered fresh. Pages that contain a form for
signed-out visitors (the sign-in page) must not use this, because the CSRF token in the cached HTML
would belong to someone else.
"""
import hashlib
from functools import wraps

from django.core.cache import cache

# Free-text search would let anyone fill the cache with unique keys; render those fresh.
_UNCACHED_PARAMS = ("q",)


def cache_for_anonymous(seconds):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if (request.user.is_authenticated or request.method not in ("GET", "HEAD")
                    or any(request.GET.get(p) for p in _UNCACHED_PARAMS)):
                return view(request, *args, **kwargs)
            path = request.get_full_path()
            key = "anonpage:" + hashlib.sha256(path.encode()).hexdigest()
            response = cache.get(key)
            if response is None:
                response = view(request, *args, **kwargs)
                if response.status_code == 200 and not response.streaming and not response.cookies:
                    cache.set(key, response, seconds)
            return response
        return wrapper
    return decorator
