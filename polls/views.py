import secrets
from functools import wraps

import segno
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core import signing
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST, require_safe

from courses.security import no_store

from . import services
from .models import CODE_LENGTH, MAX_OPTIONS, Poll

COOKIE = "poll_voter"
COOKIE_SALT = "polls.voter"
COOKIE_AGE = 30 * 24 * 3600

def _voter_token(request):
    try:
        return signing.loads(request.COOKIES.get(COOKIE, ""), salt=COOKIE_SALT, max_age=COOKIE_AGE)
    except signing.BadSignature:
        return None

def _vote_url(request, poll):
    return request.build_absolute_uri(reverse("poll_vote", args=[poll.code]))

def _rows(data):
    """Result rows for the bars partial."""
    return [{"index": i, "text": text, "count": data["counts"][i],
             "pct": round(100 * data["counts"][i] / data["total"]) if data["total"] else 0}
            for i, text in enumerate(data["options"])]


def _qr_svg(url, scale=8):
    return segno.make(url, error="m").svg_inline(scale=scale, omitsize=True, border=2,
                                                  dark="#111827", light="#ffffff")

# ---------------------------------------------------------------- students (no login)

@require_http_methods(["GET", "POST"])
def enter(request):
    """Type a poll code (for anyone who can't scan the QR)."""
    error = None
    code = "".join(ch for ch in request.POST.get("code", "").upper() if ch.isalnum())[:CODE_LENGTH]
    if request.method == "POST":
        if Poll.objects.filter(code=code).exists():
            return redirect("poll_vote", code=code)
        error = "No poll with that code. Check the code on the teacher's screen."
    return no_store(render(request, "polls/enter.html", {"error": error, "code": code}))

@require_http_methods(["GET", "POST"])
def vote(request, code):
    poll = Poll.objects.filter(code=code.upper()).first()
    if poll is None:
        messages.info(request, "That poll doesn't exist.")
        return redirect("poll_enter")
    token = _voter_token(request)
    new_token = None
    if request.method == "POST":
        if token is None:
            token = new_token = secrets.token_urlsafe(24)
        try:
            services.cast(poll, token, request.POST.get("choice"))
        except services.PollError as exc:
            messages.error(request, str(exc))
        else:
            services.broadcast(poll)
        response = redirect("poll_vote", code=poll.code)       # POST → redirect → GET
        if new_token:
            response.set_cookie(COOKIE, signing.dumps(new_token, salt=COOKIE_SALT), max_age=COOKIE_AGE,
                                httponly=True, samesite="Lax", secure=not settings.DEBUG)
        return response
    mine = services.my_choice(poll, token)
    data = services.state(poll)
    show = data["show_results"] and mine is not None
    rows = _rows(data)
    return no_store(render(request, "polls/vote.html", {
        "poll": poll, "rows": rows, "mine": mine, "show": show, "total": data["total"],
    }))

# ---------------------------------------------------------------- teachers (staff only)

def staff_required(view):
    """Creating and running polls is for staff. Signed-out visitors go to the login page; signed-in
    non-staff get a 404, so the teacher pages aren't advertised. Voting (above) is open to everyone."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), reverse("admin:login"))
        if not (request.user.is_active and request.user.is_staff):
            raise Http404
        return view(request, *args, **kwargs)
    return wrapper


def _own_poll(request, code):
    """Staff run their own polls; superusers can run any."""
    poll = get_object_or_404(Poll, code=code)
    if not (poll.created_by_id == request.user.pk or request.user.is_superuser):
        raise Http404
    return poll

@staff_required
@require_http_methods(["GET", "POST"])
def manage(request):
    """List my polls and create a new one in one step."""
    form = {"question": "", "options": "", "show_results": True}
    errors = {}
    if request.method == "POST":
        form = {"question": request.POST.get("question", ""), "options": request.POST.get("options", ""),
                "show_results": request.POST.get("show_results") == "on"}
        try:
            poll = services.create_poll(form["question"], form["options"], request.user, form["show_results"])
        except ValidationError as exc:
            errors = dict(exc.message_dict)
            errors["general"] = errors.pop("__all__", [])   # templates can't read "__all__"
        except services.PollError as exc:
            errors = {"general": [str(exc)]}
        else:
            return redirect("poll_present", code=poll.code)
    polls = Poll.objects.all() if request.user.is_superuser else Poll.objects.filter(created_by=request.user)
    return no_store(render(request, "polls/manage.html", {
        "form": form, "errors": errors, "polls": polls[:30], "max_options": MAX_OPTIONS,
    }))

@staff_required
@require_safe
def present(request, code):
    """The big screen: QR code, short link and live results."""
    poll = _own_poll(request, code)
    url = _vote_url(request, poll)
    data = services.state(poll)
    return no_store(render(request, "polls/present.html", {
        "poll": poll, "vote_url": url, "short_url": url.split("://", 1)[-1].rstrip("/"),
        "qr_svg": _qr_svg(url), "rows": _rows(data), "total": data["total"], "mine": None,
    }))

@staff_required
@require_POST
def action(request, code):
    poll = _own_poll(request, code)
    what = request.POST.get("action")
    if what == "close":
        services.set_open(poll, False)
    elif what == "open":
        services.set_open(poll, True)
    elif what == "reset":
        services.reset(poll)
    elif what == "toggle_results":
        poll.show_results = not poll.show_results
        poll.save(update_fields=["show_results"])
    elif what == "delete":
        poll.delete()
        messages.success(request, "Poll deleted.")
        return redirect("poll_manage")
    else:
        raise Http404
    services.broadcast(poll)
    return redirect("poll_present", code=poll.code)

@staff_required
@require_safe
def qr_svg(request, code):
    """A standalone QR image to print or paste into slides."""
    poll = _own_poll(request, code)
    response = HttpResponse(_qr_svg(_vote_url(request, poll), scale=16).replace(
        "<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1), content_type="image/svg+xml")
    response["Content-Disposition"] = f'attachment; filename="poll-{poll.code}-qr.svg"'
    return response
