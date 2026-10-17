"""Timed assessments: like a quiz, but with a countdown and a hard time limit enforced by the server."""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from courses.models import Course


class Assessment(models.Model):
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.CASCADE, related_name="assessments",
                               help_text="Leave empty for an open assessment any signed-in user can take. "
                                         "With a course, only students enrolled in it (and staff) can take it.")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField(blank=True, help_text="Shown on the start page.")
    time_limit_minutes = models.PositiveSmallIntegerField(
        default=30, validators=[MinValueValidator(1), MaxValueValidator(600)],
        help_text="The countdown starts when the student presses Start. When it ends the answers are submitted automatically.")
    pass_percentage = models.PositiveSmallIntegerField(default=60, validators=[MaxValueValidator(100)])
    max_attempts = models.PositiveSmallIntegerField(default=1, help_text="0 means unlimited attempts.")
    shuffle_questions = models.BooleanField(default=True, help_text="Each attempt gets the questions in a different order.")
    shuffle_choices = models.BooleanField(default=True, help_text="Each attempt gets the answer options of every question in a different order. "
                                                                  "Turn it off if a question has options like 'All of the above'.")
    show_answers = models.BooleanField(default=True, help_text="After submitting, show the correct answers and explanations.")
    opens_at = models.DateTimeField(null=True, blank=True, help_text="Optional. Nobody can start before this time.")
    closes_at = models.DateTimeField(null=True, blank=True,
                                     help_text="Optional. Nobody can start after this time, and running attempts end at this time.")
    is_published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.opens_at and self.closes_at and self.closes_at <= self.opens_at:
            raise ValidationError({"closes_at": "The assessment must close after it opens."})

    @property
    def max_score(self):
        return sum(q.points for q in self.questions.all())

    def window_status(self, now=None):
        """'open', 'upcoming' or 'closed'."""
        now = now or timezone.now()
        if self.opens_at and now < self.opens_at:
            return "upcoming"
        if self.closes_at and now >= self.closes_at:
            return "closed"
        return "open"


class AssessmentQuestion(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField(help_text="Markdown is supported, including `code` and ``` blocks.")
    choices = models.TextField(help_text="One choice per line. Start the correct choice(s) with *. "
                                         "With more than one correct choice, students pick all that apply.")
    explanation = models.TextField(blank=True, help_text="Shown after submitting, if answers are shown.")
    points = models.PositiveSmallIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text[:80]

    def parsed_choices(self):
        """[(text, is_correct), ...]"""
        result = []
        for line in self.choices.splitlines():
            line = line.strip()
            if not line:
                continue
            correct = line.startswith("*")
            result.append((line[1:].strip() if correct else line, correct))
        return result

    def correct_indexes(self):
        return {i for i, (_, correct) in enumerate(self.parsed_choices()) if correct}

    @property
    def is_multiple(self):
        return len(self.correct_indexes()) > 1

    def clean(self):
        super().clean()
        choices = self.parsed_choices()
        if len(choices) < 2:
            raise ValidationError({"choices": "Add at least two choices, one per line."})
        if not any(correct for _, correct in choices):
            raise ValidationError({"choices": "Mark at least one correct choice with *."})


class AssessmentAttempt(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="attempts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assessment_attempts")
    started_at = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField(help_text="When the countdown ends (set once, when the attempt starts).")
    submitted_at = models.DateTimeField(null=True, blank=True)
    timed_out = models.BooleanField(default=False, help_text="Submitted automatically because time ran out.")
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=0)
    # {question_id: [selected choice indexes]}: saved while the student works, final once submitted.
    answers = models.JSONField(default=dict, blank=True)
    question_order = models.JSONField(default=list, blank=True)
    # {question_id: [original choice indexes in the order shown]}. Empty = choices shown in their written order.
    choice_order = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [models.Index(fields=["assessment", "user"]), models.Index(fields=["submitted_at", "deadline"])]

    def __str__(self):
        return f"{self.user} · {self.assessment.title} · {self.score}/{self.max_score}"

    @property
    def is_open(self):
        return self.submitted_at is None

    @property
    def percentage(self):
        return round(100 * self.score / self.max_score) if self.max_score else 0

    @property
    def passed(self):
        return self.percentage >= self.assessment.pass_percentage

    @property
    def seconds_used(self):
        end = self.submitted_at or timezone.now()
        return max(0, int((min(end, self.deadline) - self.started_at).total_seconds()))
