"""Read-only Calendly client for the admin panel: upcoming booked calls.

Needs a Calendly personal access token in CALENDLY_TOKEN (Calendly → Integrations → API & Webhooks).
Uses only the standard library. Results are cached for a few minutes so the panel stays fast and we
stay far below Calendly's rate limits.
"""
import json
import logging
from datetime import datetime, timezone as dt_timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache
from django.utils.dateparse import parse_datetime

log = logging.getLogger(__name__)
API = "https://api.calendly.com"
CACHE_KEY = "panel:calendly:upcoming"
CACHE_SECONDS = 300
MAX_CALLS = 10
# Scopes a personal access token needs for the admin panel (Calendly grants nothing by default).
SCOPES = ("users:read", "scheduled_events:read")


class CalendlyError(Exception):
    """Shown on the panel as-is, so keep messages short and free of secrets."""


def _reason(exc):
    """Calendly's own explanation from an error response, e.g. " (Unauthenticated: The access token is
    invalid)". Calendly's text only; the token is never echoed."""
    try:
        body = json.loads(exc.read() or b"{}")
    except (ValueError, OSError):
        return ""
    if not isinstance(body, dict):
        return ""
    parts = [str(body.get("title") or "")[:80], str(body.get("message") or "")[:200]]
    text = ": ".join(p for p in parts if p)
    return f" ({text})" if text else ""


def _get(path, params=None, scope="scheduled_events:read"):
    url = path if path.startswith("http") else API + path
    if params:
        url += "?" + urlencode(params)
    req = Request(url, headers={"Authorization": f"Bearer {settings.CALENDLY_TOKEN}",
                                "Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=8) as resp:
            return json.load(resp)
    except HTTPError as exc:
        reason = _reason(exc)
        if exc.code == 401:
            raise CalendlyError(f"Calendly says the token is invalid or expired{reason}. Check CALENDLY_TOKEN "
                                "in the server's .env (no quotes or spaces) or create a new token.")
        if exc.code == 403:
            raise CalendlyError(f"The token works but is missing the \"{scope}\" scope{reason}. Create a new "
                                f"personal access token with the scopes: {', '.join(SCOPES)}.")
        raise CalendlyError(f"Calendly returned an error ({exc.code}){reason}.")
    except (URLError, TimeoutError, ValueError) as exc:
        log.warning("Calendly request failed: %s", exc)
        raise CalendlyError("Couldn't reach Calendly. Try again in a minute.")


def _fetch_upcoming():
    me = _get("/users/me", scope="users:read")["resource"]["uri"]
    now = datetime.now(dt_timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000Z")
    events = _get("/scheduled_events", {"user": me, "status": "active", "min_start_time": now,
                                        "sort": "start_time:asc", "count": MAX_CALLS})["collection"]
    calls = []
    for event in events:
        invitees = _get(event["uri"] + "/invitees", {"status": "active", "count": 5}).get("collection", [])
        location = event.get("location") or {}
        calls.append({
            "name": event.get("name", "Call"),
            "start": parse_datetime(event["start_time"]),
            "end": parse_datetime(event["end_time"]),
            "join_url": location.get("join_url") or "",
            "invitees": [{
                "name": i.get("name", ""),
                "email": i.get("email", ""),
                "answers": [(qa.get("question", ""), qa.get("answer", "")) for qa in i.get("questions_and_answers") or []],
            } for i in invitees],
        })
    return calls


def upcoming_calls(refresh=False):
    """Returns (calls, error). calls is None when Calendly isn't configured."""
    if not settings.CALENDLY_TOKEN:
        return None, None
    if not refresh:
        cached = cache.get(CACHE_KEY)
        if cached is not None:
            return cached, None
    try:
        calls = _fetch_upcoming()
    except CalendlyError as exc:
        return [], str(exc)
    except (KeyError, TypeError) as exc:      # unexpected response shape
        log.warning("Unexpected Calendly response: %r", exc)
        return [], "Calendly sent a response we couldn't read."
    cache.set(CACHE_KEY, calls, CACHE_SECONDS)
    return calls, None
