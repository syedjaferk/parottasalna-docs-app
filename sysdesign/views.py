import json

from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_safe

from courses.security import api_login_required, no_store

from .catalog import get_problem, list_problems
from .models import Problem, ProblemProgress

MAX_BODY = 200_000


@require_safe
def index(request):
    problems = list_problems()
    done = {}
    if request.user.is_authenticated:
        done = {p.problem.slug: len(p.answers) for p in ProblemProgress.objects.filter(user=request.user).select_related("problem")}
    for p in problems:
        p["category"] = p["statement"].get("category", "")
        p["done"] = done.get(p["slug"])             # None for anonymous visitors; the page script reads this browser's copy
    categories = sorted({p["category"] for p in problems if p["category"]})
    return render(request, "sysdesign/index.html", {"problems": problems, "categories": categories, "signed_in": request.user.is_authenticated})


@require_safe
@ensure_csrf_cookie
def problem(request, slug):
    data = get_problem(slug)
    if data is None:
        raise Http404("Unknown problem")
    return render(request, "sysdesign/problem.html", {"problem": data})


def _published(slug):
    p = Problem.objects.filter(slug=slug, is_published=True).first()
    if p is None:
        raise Http404("Unknown problem")
    return p


def _payload(row):
    return {"exists": row is not None, "answers": row.answers if row else {}, "current": row.current_step if row else 0}


def _clean_answers(raw, step_ids):
    """Keep only dict answers for steps that exist in this problem."""
    if not isinstance(raw, dict):
        return {}
    return {k: v for k, v in raw.items() if k in step_ids and isinstance(v, dict)}


@require_safe
@api_login_required
def progress_get(request, slug):
    p = _published(slug)
    row = ProblemProgress.objects.filter(user=request.user, problem=p).first()
    return no_store(JsonResponse(_payload(row)))


@require_POST
@api_login_required
def progress_save(request, slug):
    """Body: {answers, current, merge?}. ``merge`` adds answers the server does not have yet (used for the
    one-off import of a browser's localStorage); without it the stored progress is replaced (normal saves, reset)."""
    p = _published(slug)
    if len(request.body) > MAX_BODY:
        return JsonResponse({"error": "Too large"}, status=413)
    try:
        body = json.loads(request.body or b"{}")
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    if not isinstance(body, dict):
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    step_ids = {s.get("id") for s in p.steps}
    answers = _clean_answers(body.get("answers"), step_ids)
    current = body.get("current")
    current = current if isinstance(current, int) and not isinstance(current, bool) else 0
    current = max(0, min(current, len(p.steps)))
    row, _ = ProblemProgress.objects.get_or_create(user=request.user, problem=p)
    if body.get("merge"):
        row.answers = {**answers, **row.answers}      # what the account already has wins
        row.current_step = max(row.current_step, current)
    else:
        row.answers, row.current_step = answers, current
    row.save()
    return no_store(JsonResponse(_payload(row)))
