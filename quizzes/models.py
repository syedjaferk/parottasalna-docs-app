from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from courses.models import Course


CHAPTER_HELP = (
    "Docs page this belongs to: the markdown file name without .md, e.g. <code>lesson-1</code> or "
    "<code>sessions/04-llm-terminology</code>. A card linking to it is shown on that page. "
    "Leave blank for a course-level item."
)


def clean_chapter(course, chapter: str) -> str:
    """Normalise a chapter name and check the page exists in the course's content folder."""
    chapter = chapter.strip().strip("/").removesuffix(".md").removesuffix(".rst")
    if chapter and course is not None:
        try:
            src = course.src_dir
        except Exception:
            return chapter
        if src.is_dir() and not any((src / f"{chapter}{ext}").is_file() for ext in (".md", ".rst")):
            raise ValidationError({"chapter": f"No page “{chapter}.md” in this course's content folder."})
    return chapter


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=200)
    chapter = models.CharField(max_length=200, blank=True, help_text=CHAPTER_HELP)
    description = models.TextField(blank=True, help_text="Shown before the student starts.")
    is_published = models.BooleanField(
        default=False, help_text="Students only see published quizzes."
    )
    max_attempts = models.PositiveSmallIntegerField(
        default=0, help_text="0 means unlimited attempts."
    )
    pass_percentage = models.PositiveSmallIntegerField(default=60)
    show_answers = models.BooleanField(
        default=True, help_text="After submitting, show correct answers and explanations."
    )
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers are listed first.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["course", "order", "id"]
        verbose_name_plural = "quizzes"

    def __str__(self):
        return f"{self.course.title} · {self.title}"

    def clean(self):
        super().clean()
        self.chapter = clean_chapter(self.course if self.course_id else None, self.chapter)

    @property
    def max_score(self):
        return sum(q.points for q in self.questions.all())


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField(help_text="Markdown is supported, including `code` and ``` blocks.")
    choices = models.TextField(
        help_text="One choice per line. Start the correct choice(s) with <code>*</code>. "
        "With more than one correct choice, students pick all that apply."
    )
    explanation = models.TextField(blank=True, help_text="Shown after submitting (optional).")
    points = models.PositiveSmallIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text[:80]

    def parsed_choices(self):
        """[(text, is_correct), ...] from the one-per-line choices field."""
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


class Attempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts"
    )
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=0)
    # {question_id: [selected choice indexes]} as submitted.
    answers = models.JSONField(default=dict, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [models.Index(fields=["quiz", "user"])]

    def __str__(self):
        return f"{self.user} · {self.quiz.title} · {self.score}/{self.max_score}"

    @property
    def percentage(self):
        return round(100 * self.score / self.max_score) if self.max_score else 0

    @property
    def passed(self):
        return self.percentage >= self.quiz.pass_percentage


class Deck(models.Model):
    """A set of flashcards for a course, optionally tied to one chapter."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="decks")
    title = models.CharField(max_length=200)
    chapter = models.CharField(max_length=200, blank=True, help_text=CHAPTER_HELP)
    description = models.TextField(blank=True, help_text="Shown before the student starts.")
    is_published = models.BooleanField(default=False, help_text="Students only see published decks.")
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers are listed first.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["course", "order", "id"]

    def __str__(self):
        return f"{self.course.title} · {self.title}"

    def clean(self):
        super().clean()
        self.chapter = clean_chapter(self.course if self.course_id else None, self.chapter)


class Flashcard(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="cards")
    front = models.TextField(help_text="The question or term. Markdown is supported.")
    back = models.TextField(help_text="The answer or explanation. Markdown is supported.")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.front[:80]


class CardReview(models.Model):
    """A student's latest self-assessment of one card ("Got it" or "Again")."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="card_reviews")
    card = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name="reviews")
    known = models.BooleanField(default=False)
    times_seen = models.PositiveIntegerField(default=0)
    reviewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "card"], name="uniq_user_card")]

    def __str__(self):
        return f"{self.user} · {self.card} · {'known' if self.known else 'learning'}"
