import json
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST, require_safe

from courses.security import api_login_required, no_store

from .catalog import DATA_DIR, problem_ids
from .models import ProblemProgress

MAX_NOTE = 2000
MAX_IMPORT = 4000


def _progress_json(user):
    rows = ProblemProgress.objects.filter(user=user).values_list("problem_id", "solved", "bookmarked", "note")
    return {pid: {"s": s, "b": b, "n": n} for pid, s, b, n in rows if s or b or n}


def _apply(user, pid, data):
    """Create/update one progress row from a dict with any of solved / bookmarked / note."""
    row, _ = ProblemProgress.objects.get_or_create(user=user, problem_id=pid)
    if "solved" in data:
        solved = bool(data["solved"])
        if solved and not row.solved:
            row.solved_at = timezone.now()
        row.solved = solved
    if "bookmarked" in data:
        row.bookmarked = bool(data["bookmarked"])
    if "note" in data:
        row.note = str(data["note"] or "")[:MAX_NOTE]
    if not (row.solved or row.bookmarked or row.note):
        row.delete()
    else:
        row.save()


@require_safe
@login_required
def tracker(request):
    return render(request, "prep/tracker.html", {"tab": "tracker"})


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
            _apply(request.user, pid, {"solved": v.get("s"), "bookmarked": v.get("b"), "note": v.get("n")})
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
        qs.update(**{"solved": False, "solved_at": None} if what == "solved" else {"bookmarked": False} if what == "bookmarks" else {"note": ""})
        ProblemProgress.objects.filter(user=request.user, solved=False, bookmarked=False, note="").delete()
    return no_store(JsonResponse({"progress": _progress_json(request.user)}))
