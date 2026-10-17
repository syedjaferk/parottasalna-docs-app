import json
from datetime import date, timedelta
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST, require_safe

from courses.security import api_login_required, no_store

from .catalog import DATA_DIR, problem_ids
from . import services
from .models import ProblemProgress

MAX_NOTE = 2000
MAX_IMPORT = 4000
OUTCOMES = {"cold", "hint", "fail"}


def _apply(user, pid, data):
    """Create/update one progress row from a dict with any of solved / bookmarked / note."""
    row, _ = ProblemProgress.objects.get_or_create(user=user, problem_id=pid)
    if "solved" in data:
        if bool(data["solved"]) and not row.solved:       # a plain tick, or an import: solved today, review tomorrow
            services.log_attempt(user, pid, "cold", confidence=3)
            row.refresh_from_db()
        elif not data["solved"] and row.solved:
            services.reset_schedule(row)
    if "bookmarked" in data:
        row.bookmarked = bool(data["bookmarked"])
    if "note" in data:
        row.note = str(data["note"] or "")[:MAX_NOTE]
    if not (row.solved or row.bookmarked or row.note or row.attempts):
        row.delete()
    else:
        row.save()


def _progress_json(user):
    return services.progress_json(user)


def _import_row(user, pid, v):
    """Restore one exported entry, keeping its re-solve schedule when the export has one."""
    def num(key, lo, hi):
        x = v.get(key)
        return x if isinstance(x, int) and not isinstance(x, bool) and lo <= x <= hi else None

    row, _ = ProblemProgress.objects.get_or_create(user=user, problem_id=pid)
    row.bookmarked = bool(v.get("b"))
    row.note = str(v.get("n") or "")[:MAX_NOTE]
    if v.get("s") and not row.solved:
        row.solved, row.solved_at = True, timezone.now()
    row.stage = num("st", 0, 4) or row.stage
    try:
        row.next_review = date.fromisoformat(v["nr"]) if v.get("nr") else row.next_review
    except (ValueError, TypeError):
        pass
    row.confidence = num("cf", 1, 5) or row.confidence
    row.attempts = num("at", 0, 10000) or row.attempts
    if row.solved and not v.get("st") and not row.next_review:   # an older export without a schedule: start the cycle
        row.stage, row.next_review = 1, timezone.localdate() + timedelta(days=1)
    if not (row.solved or row.bookmarked or row.note or row.attempts):
        row.delete()
    else:
        row.save()


@require_safe
@login_required
def home(request):
    return render(request, "prep/home.html", {"tab": "home"})


@require_safe
@login_required
def tracker(request):
    return render(request, "prep/tracker.html", {"tab": "tracker"})


@require_safe
@login_required
def placement(request):
    return render(request, "prep/placement.html", {"tab": "placement"})


@require_safe
@login_required
def patterns(request):
    return render(request, "prep/patterns.html", {"tab": "patterns"})


@require_safe
@login_required
def data_file(request, name):
    """Serves catalog.json and pattern_guides.json to signed-in students only."""
    if name not in ("catalog", "pattern_guides"):
        raise Http404
    path = Path(DATA_DIR / f"{name}.json")
    if not path.is_file():
        raise Http404
    response = FileResponse(open(path, "rb"), content_type="application/json; charset=utf-8")
    response["Cache-Control"] = "private, max-age=3600"
    return response


@require_safe
@api_login_required
def progress_get(request):
    return no_store(JsonResponse({"progress": _progress_json(request.user)}))


@require_POST
@api_login_required
def progress_set(request):
    """Body: {"id": "<problem id>", "solved"?: bool, "bookmarked"?: bool, "note"?: str}."""
    try:
        data = json.loads(request.body or b"{}")
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    pid = data.get("id") if isinstance(data, dict) else None
    if pid not in problem_ids():
        return JsonResponse({"error": "Unknown problem"}, status=404)
    _apply(request.user, pid, data)
    return no_store(JsonResponse({"ok": True}))


@require_POST
@api_login_required
def progress_import(request):
    """Body: {"progress": {"<id>": {"s": bool, "b": bool, "n": str}}, "replace"?: bool} (the export format)."""
    try:
        data = json.loads(request.body or b"{}")
        items = data["progress"]
    except (ValueError, KeyError, TypeError):
        return JsonResponse({"error": "Invalid file"}, status=400)
    if not isinstance(items, dict) or len(items) > MAX_IMPORT:
        return JsonResponse({"error": "Invalid file"}, status=400)
    known = problem_ids()
    if data.get("replace"):
        ProblemProgress.objects.filter(user=request.user).delete()
    done = 0
    for pid, v in items.items():
        if pid in known and isinstance(v, dict):
            _import_row(request.user, pid, v)
            done += 1
    return no_store(JsonResponse({"imported": done, "progress": _progress_json(request.user)}))


@require_POST
@api_login_required
def progress_clear(request):
    """Body: {"what": "solved" | "bookmarks" | "notes" | "all", "ids"?: [problem ids]} - clears for the signed-in student."""
    try:
        data = json.loads(request.body or b"{}")
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    what = data.get("what")
    if what not in ("solved", "bookmarks", "notes", "all"):
        return JsonResponse({"error": "Invalid request"}, status=400)
    qs = ProblemProgress.objects.filter(user=request.user)
    ids = data.get("ids")
    if isinstance(ids, list):
        qs = qs.filter(problem_id__in=[i for i in ids if isinstance(i, str)][:MAX_IMPORT])
    if what == "all":
        qs.delete()
    else:
        qs.update(**{"solved": False, "solved_at": None, "stage": 0, "next_review": None, "attempts": 0, "confidence": None} if what == "solved" else {"bookmarked": False} if what == "bookmarks" else {"note": ""})
        ProblemProgress.objects.filter(user=request.user, solved=False, bookmarked=False, note="", attempts=0).delete()
    return no_store(JsonResponse({"progress": _progress_json(request.user)}))


@require_safe
@api_login_required
def next_json(request):
    """Today's plan: reviews due, new problems to try, and coverage per pattern."""
    return no_store(JsonResponse(services.plan_for_user(request.user), json_dumps_params={"default": str}))


@require_POST
@api_login_required
def progress_log(request):
    """Body: {"id", "outcome": cold|hint|fail, "confidence"?: 1-5, "minutes"?: int, "note"?: str}."""
    try:
        data = json.loads(request.body or b"{}")
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    if not isinstance(data, dict) or data.get("id") not in problem_ids() or data.get("outcome") not in OUTCOMES:
        return JsonResponse({"error": "Invalid request"}, status=400)

    def small(key, lo, hi):
        v = data.get(key)
        return v if isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi else None

    note = data.get("note")
    row = services.log_attempt(request.user, data["id"], data["outcome"], confidence=small("confidence", 1, 5),
                               minutes=small("minutes", 0, 600), note=str(note)[:MAX_NOTE] if isinstance(note, str) else None)
    return no_store(JsonResponse({"ok": True, "entry": services.progress_json(request.user).get(row.problem_id)}))


@require_safe
@api_login_required
def placement_questions(request):
    return no_store(JsonResponse({"questions": services.public_questions()}))


@require_POST
@api_login_required
def placement_submit(request):
    """Body: {"answers": {"q1": 2, "q2": -1, ...}}. Grades on the server so the answers are never sent to the browser first."""
    try:
        answers = json.loads(request.body or b"{}")["answers"]
    except (ValueError, KeyError, TypeError):
        return JsonResponse({"error": "Invalid request"}, status=400)
    if not isinstance(answers, dict):
        return JsonResponse({"error": "Invalid request"}, status=400)
    results, diag, score, total, level = services.grade_placement(answers)
    services.save_placement(request.user, diag, score, total, level)
    return no_store(JsonResponse({"results": results, "score": score, "total": total, "level": level, "patterns": diag}))
