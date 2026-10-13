"""API for the review worker on our own machine. It polls (nothing calls in to it), so it can sit behind NAT.

Every request: POST with  Authorization: Bearer <ATS_WORKER_TOKEN>

  /api/ats/claim/                 -> 200 {tracking_id, drive_file_id, target_role, attempt} | 204 nothing waiting
  /api/ats/<id>/complete/         body {"result": {...}}  -> 200 {status}  | 422 {errors} (fix and retry)
  /api/ats/<id>/fail/             body {"reason": "unreadable" | "not_a_resume" | "error"}  -> 200

The worker never gets the user's name or email: only the Drive file and the tracking ID.
The result format and its checks are in results.py.
"""
import hmac
import json
from functools import wraps

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import services
from .models import ResumeReview
from .results import ResultError


def worker_api(view):
    @csrf_exempt
    @require_POST
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        token = settings.ATS_WORKER_TOKEN
        sent = request.headers.get("Authorization", "")
        if not token or not hmac.compare_digest(sent.encode(), f"Bearer {token}".encode()):
            return JsonResponse({"error": "unauthorised"}, status=401)
        return view(request, *args, **kwargs)
    return wrapped


def _body(request):
    try:
        data = json.loads(request.body or b"{}")
    except (ValueError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _claimed(tracking_id):
    review = get_object_or_404(ResumeReview, tracking_id=tracking_id)
    if review.status != ResumeReview.Status.PROCESSING:
        return review, JsonResponse({"error": f"not claimed (status: {review.status})"}, status=409)
    return review, None


@worker_api
def claim(request):
    review = services.claim_next()
    if review is None:
        return HttpResponse(status=204)
    return JsonResponse({
        "tracking_id": review.tracking_id,
        "drive_file_id": review.drive_file_id,
        "target_role": review.target_role,
        "attempt": review.attempts,
    })


@worker_api
def complete(request, tracking_id):
    review, conflict = _claimed(tracking_id)
    if conflict:
        return conflict
    data = _body(request)
    if data is None or "result" not in data:
        return JsonResponse({"errors": ['body must be {"result": {...}}']}, status=422)
    try:
        services.complete(review, data["result"])
    except ResultError as e:
        return JsonResponse({"errors": e.errors}, status=422)
    return JsonResponse({"status": review.status, "flags": review.flags})


@worker_api
def fail(request, tracking_id):
    review, conflict = _claimed(tracking_id)
    if conflict:
        return conflict
    data = _body(request) or {}
    services.fail(review, data.get("reason", "error"))
    return JsonResponse({"status": review.status})
