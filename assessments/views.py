import csv
import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods, require_safe

from courses.security import api_login_required, csv_safe, no_store
from courses.services import can_track
from streaks.services import record_action

from . import services as svc
from .models import Assessment, AssessmentAttempt


def _assessment_for(request, slug):
    queryset = Assessment.objects.select_related("course")
    if not request.user.is_staff:
        queryset = queryset.filter(is_published=True)       # staff can preview drafts
    assessment = get_object_or_404(queryset, slug=slug)
    if not svc.can_open(request.user, assessment):
        raise Http404                                          # don't reveal what exists
    return assessment


def _attempt_for(request, pk):
    attempt = get_object_or_404(AssessmentAttempt.objects.select_related("assessment", "assessment__course"), pk=pk)
    if attempt.user_id != request.user.pk:
        raise Http404
    return attempt


def _form_items(attempt):
    saved = attempt.answers or {}
    items = []
    for question in svc.ordered_questions(attempt):
        picked = set(saved.get(str(question.pk), []))
        parsed = question.parsed_choices()
        items.append({
            "question": question,
            "choices": [(i, parsed[i][0], i in picked) for i in svc.choice_sequence(attempt, question)],
            "answered": bool(picked),
        })
    return items


@login_required
@require_safe
def assessment_list(request):
    svc.expire_stale(request.user)
    assessments = svc.visible_assessments(request.user)
    best = svc.best_attempts(request.user, assessments)
    running = {a.assessment_id: a for a in AssessmentAttempt.objects.filter(
        user=request.user, assessment__in=assessments, submitted_at__isnull=True)}
    rows = [{
        "assessment": a, "best": best.get(a.pk), "running": running.get(a.pk),
        "status": a.window_status(), "left": svc.attempts_left(a, request.user),
        "questions": a.questions.count(),
    } for a in assessments]
    return render(request, "assessments/list.html", {"rows": rows})


@login_required
@require_safe
def assessment_detail(request, slug):
    assessment = _assessment_for(request, slug)
    svc.expire_stale(request.user)
    running = AssessmentAttempt.objects.filter(assessment=assessment, user=request.user,
                                               submitted_at__isnull=True).first()
    past = list(AssessmentAttempt.objects.filter(assessment=assessment, user=request.user,
                                                 submitted_at__isnull=False))
    return render(request, "assessments/detail.html", {
        "assessment": assessment, "running": running, "past": past,
        "questions": assessment.questions.count(), "status": assessment.window_status(),
        "left": svc.attempts_left(assessment, request.user),
    })


@login_required
@require_POST
def assessment_start(request, slug):
    assessment = _assessment_for(request, slug)
    try:
        attempt, _ = svc.start_attempt(assessment, request.user)
    except svc.AssessmentError as error:
        messages.error(request, str(error))
        return redirect("assessment_detail", slug=assessment.slug)
    return redirect("assessment_take", pk=attempt.pk)


@login_required
@require_http_methods(["GET", "POST"])
def assessment_take(request, pk):
    attempt = _attempt_for(request, pk)
    assessment = attempt.assessment
    if not attempt.is_open:
        return redirect("assessment_result", pk=attempt.pk)

    if request.method == "POST":
        questions = list(assessment.questions.all())
        if svc.is_past_deadline(attempt):
            # Too late for what was typed in the page: grade what was autosaved before the deadline.
            done = svc.finalize(attempt.pk, timed_out=True)
        else:
            posted = svc.answers_from_post(request.POST, questions)
            done = svc.finalize(attempt.pk, answers=posted, timed_out=request.POST.get("auto") == "1"
                                and timezone.now() > attempt.deadline)
        if assessment.course_id and can_track(request.user, assessment.course):
            record_action(request.user)
        return redirect("assessment_result", pk=done.pk)

    if svc.is_past_deadline(attempt):
        svc.finalize(attempt.pk, timed_out=True)
        messages.info(request, "Your time ran out, so your saved answers were submitted.")
        return redirect("assessment_result", pk=attempt.pk)

    now = timezone.now()
    response = render(request, "assessments/take.html", {
        "attempt": attempt, "assessment": assessment, "items": _form_items(attempt),
        "remaining": svc.remaining_seconds(attempt, now),
        "server_now_ms": int(now.timestamp() * 1000), "deadline_ms": int(attempt.deadline.timestamp() * 1000),
        "total_seconds": assessment.time_limit_minutes * 60,
    })
    return no_store(response)


@require_POST
@api_login_required
def assessment_save(request, pk):
    attempt = get_object_or_404(AssessmentAttempt.objects.select_related("assessment"), pk=pk, user=request.user)
    try:
        payload = json.loads(request.body or b"{}")
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    now = timezone.now()
    if not attempt.is_open:
        return JsonResponse({"ok": False, "expired": True, "remaining": 0})
    saved = svc.save_answers(attempt, payload.get("answers", {}), now)
    return no_store(JsonResponse({"ok": saved, "expired": not saved, "remaining": svc.remaining_seconds(attempt, now)}))


@login_required
@require_safe
def assessment_result(request, pk):
    attempt = get_object_or_404(AssessmentAttempt.objects.select_related("assessment", "user"), pk=pk)
    if attempt.user_id != request.user.pk and not request.user.is_staff:
        raise Http404
    if attempt.is_open:
        if attempt.user_id != request.user.pk:
            raise Http404
        return redirect("assessment_take", pk=attempt.pk)
    assessment = attempt.assessment
    review = []
    if assessment.show_answers or request.user.is_staff:
        for question in svc.ordered_questions(attempt):
            picked = set(attempt.answers.get(str(question.pk), []))
            parsed = question.parsed_choices()
            review.append({
                "question": question,
                "choices": [{"text": parsed[i][0], "correct": parsed[i][1], "picked": i in picked}
                            for i in svc.choice_sequence(attempt, question)],
                "is_right": picked == question.correct_indexes(),
                "skipped": not picked,
            })
    return render(request, "assessments/result.html", {
        "attempt": attempt, "assessment": assessment, "review": review,
        "left": svc.attempts_left(assessment, attempt.user),
        "minutes": attempt.seconds_used // 60, "seconds": attempt.seconds_used % 60,
    })


def _results_rows(assessment):
    return list(assessment.attempts.select_related("user").filter(submitted_at__isnull=False).order_by("-submitted_at"))


@staff_member_required
@require_safe
def assessment_results(request, slug):
    assessment = get_object_or_404(Assessment, slug=slug)
    svc.expire_stale()
    rows = _results_rows(assessment)
    in_progress = assessment.attempts.filter(submitted_at__isnull=True).count()
    return render(request, "assessments/results.html", {"assessment": assessment, "rows": rows, "in_progress": in_progress})


@staff_member_required
@require_safe
def assessment_results_csv(request, slug):
    assessment = get_object_or_404(Assessment, slug=slug)
    svc.expire_stale()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{assessment.slug}-results.csv"'
    writer = csv.writer(response)
    writer.writerow(["Email", "Name", "Score", "Out of", "Percent", "Passed", "Minutes used", "Timed out", "Submitted"])
    for a in _results_rows(assessment):
        writer.writerow([csv_safe(v) for v in [
            a.user.email or a.user.username, a.user.get_full_name(), a.score, a.max_score, a.percentage,
            "yes" if a.passed else "no", round(a.seconds_used / 60, 1), "yes" if a.timed_out else "no",
            a.submitted_at.isoformat(timespec="seconds"),
        ]])
    return no_store(response)
