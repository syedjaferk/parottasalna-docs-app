"""Small helpers shared by the JSON endpoints and CSV exports."""
from functools import wraps

from django.http import JsonResponse

# Spreadsheet apps execute cells starting with these as formulas (CSV/formula injection).
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def csv_safe(value):
    """Neutralise a CSV cell so Excel/Sheets show it as text instead of running it as a formula."""
    if value is None:
        return ""
    text = str(value)
    return "'" + text if text.startswith(_FORMULA_PREFIXES) else text


def api_login_required(view):
    """Like login_required, but answers API calls with 401 JSON instead of redirecting to HTML."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        return view(request, *args, **kwargs)
    return wrapper


def no_store(response):
    """Per-user API data must never be cached by browsers or shared proxies."""
    response["Cache-Control"] = "private, no-store"
    return response
