import csv

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db import transaction
from django.views.decorators.http import require_http_methods, require_safe

from courses.models import Course
from courses.security import csv_safe, no_store
from courses.services import can_track, user_can_access

from .models import Attempt, Quiz
from .services import (
    attempts_left,
    attempts_used,
    best_scores,
    grade,
    published_quizzes,
    selected_answers,
)


def _form_items(questions, answers):
    """Questions with their choices and what the student already picked (for re-display)."""
    items = []
    for question in questions:
        picked = set(answers.get(str(question.pk), []))
        items.append({
            "question": question,
            "choices": [(i, text, i in picked) for i, (text, _) in enumerate(question.parsed_choices())],
            "answered": bool(picked),
        })
    return items


def _course_for(request, slug):
    """Quizzes store scores, so they're only for students enrolled in the course (and staff)."""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    if not can_track(request.user, course):
        raise Http404  # same as docs: don't reveal which courses exist
    return course


def _quiz_for(request, course, pk):
    quizzes = published_quizzes(course)
    if request.user.is_staff:  # staff can preview drafts
        quizzes = course.quizzes.all()
    return get_object_or_404(quizzes, pk=pk)


@login_required
@require_safe
def quiz_list(request, slug):
    course = _course_for(request, slug)
    quizzes = list(published_quizzes(course))
    best = best_scores(request.user, quizzes)
    rows = [{"quiz": quiz, "best": best.get(quiz.pk)} for quiz in quizzes]
    return render(request, "quizzes/quiz_list.html", {"course": course, "rows": rows})


@login_required
@require_http_methods(["GET", "POST"])
def quiz_take(request, slug, pk):
    course = _course_for(request, slug)
    quiz = _quiz_for(request, course, pk)
    questions = list(quiz.questions.all())
    left = attempts_left(quiz, request.user)

    if left == 0:
        messages.info(request, "You have used all your attempts for this quiz.")
        return redirect("quiz_list", slug=course.slug)

    if request.method == "POST":
        answers = selected_answers(request.POST, questions)
        unanswered = sum(1 for q in questions if not answers[str(q.pk)])
        if unanswered and not request.POST.get("confirm_unanswered"):
            messages.warning(
                request,
                f"{unanswered} question(s) are unanswered. Answer them, or submit again to finish anyway.",
            )
            return render(request, "quizzes/quiz_take.html", {
                "course": course, "quiz": quiz, "items": _form_items(questions, answers),
                "attempts_left": left, "confirm_unanswered": True,
            })
        score, max_score = grade(questions, answers)
        with transaction.atomic():
            # Lock the quiz row so two simultaneous submissions can't both slip under max_attempts.
            Quiz.objects.select_for_update().filter(pk=quiz.pk).exists()
            if attempts_left(quiz, request.user) == 0:
                messages.info(request, "You have used all your attempts for this quiz.")
                return redirect("quiz_list", slug=course.slug)
            attempt = Attempt.objects.create(
                quiz=quiz, user=request.user, score=score, max_score=max_score, answers=answers
            )
        return redirect("quiz_result", slug=course.slug, pk=attempt.pk)

    return render(request, "quizzes/quiz_take.html", {
        "course": course, "quiz": quiz, "items": _form_items(questions, {}), "attempts_left": left,
    })


@login_required
@require_safe
def quiz_result(request, slug, pk):
    course = _course_for(request, slug)
    attempt = get_object_or_404(Attempt.objects.select_related("quiz"), pk=pk, quiz__course=course)
    if attempt.user_id != request.user.pk and not request.user.is_staff:
        raise Http404
    quiz = attempt.quiz
    review = []
    for question in quiz.questions.all():
        picked = set(attempt.answers.get(str(question.pk), []))
        choices = [
            {"text": text, "correct": correct, "picked": i in picked}
            for i, (text, correct) in enumerate(question.parsed_choices())
        ]
        review.append({
            "question": question,
            "choices": choices,
            "is_right": picked == question.correct_indexes(),
        })
    return render(request, "quizzes/quiz_result.html", {
        "course": course, "quiz": quiz, "attempt": attempt, "review": review,
        "attempts_left": attempts_left(quiz, attempt.user),
        "attempt_number": Attempt.objects.filter(
            quiz=quiz, user=attempt.user, submitted_at__lte=attempt.submitted_at
        ).count(),
    })


@require_safe
def quiz_feed(request, slug):
    """Quizzes per docs page, fetched by the 'Take the quiz' card inside the Sphinx docs.

    Readers who aren't enrolled (e.g. anyone browsing a common course) get an empty list: no quiz card.
    """
    course = get_object_or_404(Course, slug=slug, is_active=True)
    if not user_can_access(request.user, course):
        raise Http404
    quizzes = list(published_quizzes(course)) if can_track(request.user, course) else []
    best = best_scores(request.user, quizzes) if quizzes else {}
    data = []
    for quiz in quizzes:
        attempt = best.get(quiz.pk)
        left = attempts_left(quiz, request.user)
        data.append({
            "title": quiz.title,
            "chapter": quiz.chapter,
            "questions": quiz.question_count,
            "url": reverse("quiz_take", args=[course.slug, quiz.pk]),
            "can_attempt": left != 0,
            "best": {
                "score": attempt.score,
                "max_score": attempt.max_score,
                "percentage": attempt.percentage,
                "passed": attempt.passed,
                "url": reverse("quiz_result", args=[course.slug, attempt.pk]),
            } if attempt else None,
        })
    return no_store(JsonResponse({"list_url": reverse("quiz_list", args=[course.slug]), "quizzes": data}))


def _student_key(user):
    # Enrollments are by email; staff accounts may have none, so fall back to the username.
    return (user.email or user.username).lower()


def _scoreboard(course):
    """(quizzes, rows) where each row is {email, name, cells: [best attempt | None], total, max}."""
    quizzes = list(course.quizzes.order_by("order", "id"))
    best = {}
    for attempt in (
        Attempt.objects.filter(quiz__course=course)
        .select_related("user", "quiz")
        .order_by("-score", "-submitted_at")
    ):
        best.setdefault((_student_key(attempt.user), attempt.quiz_id), attempt)

    people = {e.email.lower(): "" for e in course.enrollments.all()}
    for (email, _), attempt in best.items():
        people.setdefault(email, "")
        people[email] = attempt.user.get_full_name() or people[email]

    rows = []
    for email in sorted(people):
        cells = [best.get((email, quiz.pk)) for quiz in quizzes]
        taken = [cell for cell in cells if cell]
        rows.append({
            "email": email,
            "name": people[email],
            "cells": cells,
            "total": sum(cell.score for cell in taken),
            "max": sum(cell.max_score for cell in taken),
            "taken": len(taken),
        })
    return quizzes, rows


@staff_member_required
@require_safe
def scoreboard(request, slug):
    course = get_object_or_404(Course, slug=slug)
    quizzes, rows = _scoreboard(course)
    return render(request, "quizzes/scoreboard.html", {"course": course, "quizzes": quizzes, "rows": rows})


@staff_member_required
@require_safe
def scoreboard_csv(request, slug):
    course = get_object_or_404(Course, slug=slug)
    quizzes, rows = _scoreboard(course)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{course.slug}-quiz-scores.csv"'
    writer = csv.writer(response)
    writer.writerow([csv_safe(v) for v in ["Email", "Name", *[q.title for q in quizzes], "Quizzes taken", "Total", "Out of"]])
    for row in rows:
        writer.writerow([csv_safe(v) for v in [
            row["email"], row["name"],
            *[f"{c.score}/{c.max_score}" if c else "" for c in row["cells"]],
            row["taken"], row["total"], row["max"],
        ]])
    return no_store(response)
