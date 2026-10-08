import csv

from django import forms
from django.contrib import admin
from django.db.models import Avg, Count, Max
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html

from courses.security import csv_safe, no_store

from .models import Attempt, CardReview, Deck, Flashcard, Question, Quiz
from .services import parse_bulk_cards


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = (("order", "points"), "text", "choices", "explanation")
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Keep the inline compact: these are short fields most of the time.
        formset.form.base_fields["text"].widget = forms.Textarea(attrs={"rows": 3, "cols": 90})
        formset.form.base_fields["choices"].widget = forms.Textarea(attrs={
            "rows": 4, "cols": 90,
            "placeholder": "list\n*tuple\ndict\nset",
        })
        formset.form.base_fields["explanation"].widget = forms.Textarea(attrs={"rows": 2, "cols": 90})
        return formset


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "chapter", "is_published", "question_count",
                    "attempt_count", "average", "links")
    list_filter = ("course", "is_published")
    list_editable = ("is_published",)
    search_fields = ("title", "chapter")
    inlines = [QuestionInline]
    fieldsets = (
        (None, {"fields": ("course", "title", "chapter", "description", "is_published")}),
        ("Rules", {"fields": (("max_attempts", "pass_percentage"), "show_answers", "order")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("course").annotate(
            _questions=Count("questions", distinct=True),
            _attempts=Count("attempts", distinct=True),
            _avg=Avg("attempts__score"),
        )

    @admin.display(ordering="_questions", description="Questions")
    def question_count(self, obj):
        return obj._questions

    @admin.display(ordering="_attempts", description="Attempts")
    def attempt_count(self, obj):
        return obj._attempts

    @admin.display(description="Avg score")
    def average(self, obj):
        return "-" if obj._avg is None else f"{obj._avg:.1f}"

    @admin.display(description="")
    def links(self, obj):
        return format_html(
            '<a href="{}">Preview</a> · <a href="{}">Scores</a>',
            reverse("quiz_take", args=[obj.course.slug, obj.pk]),
            reverse("quiz_scoreboard", args=[obj.course.slug]),
        )


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("user_email", "quiz", "score_display", "percent", "passed_display", "submitted_at", "review")
    list_filter = ("quiz__course", "quiz")
    search_fields = ("user__email", "user__first_name", "user__last_name", "quiz__title")
    date_hierarchy = "submitted_at"
    list_select_related = ("user", "quiz", "quiz__course")
    readonly_fields = ("quiz", "user", "score", "max_score", "answers", "submitted_at")
    actions = ["export_csv"]

    def has_add_permission(self, request):
        return False

    @admin.display(ordering="user__email", description="Student")
    def user_email(self, obj):
        return obj.user.email or obj.user.username

    @admin.display(ordering="score", description="Score")
    def score_display(self, obj):
        return f"{obj.score}/{obj.max_score}"

    @admin.display(description="%")
    def percent(self, obj):
        return f"{obj.percentage}%"

    @admin.display(boolean=True, description="Passed")
    def passed_display(self, obj):
        return obj.passed

    @admin.display(description="")
    def review(self, obj):
        return format_html('<a href="{}">Review</a>', reverse("quiz_result", args=[obj.quiz.course.slug, obj.pk]))

    @admin.action(description="Export selected attempts to CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="quiz-attempts.csv"'
        writer = csv.writer(response)
        writer.writerow(["Email", "Name", "Course", "Quiz", "Score", "Out of", "Percent", "Passed", "Submitted"])
        for a in queryset.select_related("user", "quiz", "quiz__course"):
            writer.writerow([csv_safe(v) for v in [
                a.user.email, a.user.get_full_name(), a.quiz.course.title, a.quiz.title,
                a.score, a.max_score, a.percentage, "yes" if a.passed else "no",
                a.submitted_at.isoformat(timespec="seconds"),
            ]])
        return no_store(response)


# ---------------------------------------------------------------- Flashcards

class DeckAdminForm(forms.ModelForm):
    bulk_cards = forms.CharField(
        label="Add cards (bulk)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 6, "cols": 90,
                                     "placeholder": "What does LLM stand for? :: Large Language Model\n"
                                                    "Low temperature means? :: Predictable, focused answers"}),
        help_text="One card per line: <code>front :: back</code>. Cards are added after the existing ones. "
                  "For longer answers with Markdown or code, use the card editor below.",
    )

    class Meta:
        model = Deck
        fields = "__all__"

    def clean_bulk_cards(self):
        cards, bad = parse_bulk_cards(self.cleaned_data.get("bulk_cards", ""))
        if bad:
            raise forms.ValidationError(
                f"Line(s) {', '.join(map(str, bad))} need the form 'front :: back' with text on both sides."
            )
        return cards


class FlashcardInline(admin.TabularInline):
    model = Flashcard
    extra = 1
    fields = ("order", "front", "back")

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        for name in ("front", "back"):
            formset.form.base_fields[name].widget = forms.Textarea(attrs={"rows": 2, "cols": 50})
        return formset


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    form = DeckAdminForm
    list_display = ("title", "course", "chapter", "is_published", "card_count", "links")
    list_filter = ("course", "is_published")
    list_editable = ("is_published",)
    search_fields = ("title", "chapter")
    inlines = [FlashcardInline]
    fieldsets = (
        (None, {"fields": ("course", "title", "chapter", "description", "is_published", "order")}),
        ("Add many cards at once", {"fields": ("bulk_cards",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("course").annotate(_cards=Count("cards"))

    @admin.display(ordering="_cards", description="Cards")
    def card_count(self, obj):
        return obj._cards

    @admin.display(description="")
    def links(self, obj):
        return format_html('<a href="{}">Preview</a>', reverse("deck_study", args=[obj.course.slug, obj.pk]))

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        cards = form.cleaned_data.get("bulk_cards") or []
        if cards:
            start = (form.instance.cards.aggregate(m=Max("order"))["m"] or 0) + 1
            Flashcard.objects.bulk_create(
                Flashcard(deck=form.instance, front=front, back=back, order=start + i)
                for i, (front, back) in enumerate(cards)
            )
            self.message_user(request, f"Added {len(cards)} card(s).")


@admin.register(CardReview)
class CardReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "deck", "card", "known", "times_seen", "reviewed_at")
    list_filter = ("card__deck__course", "card__deck", "known")
    search_fields = ("user__email", "card__front")
    list_select_related = ("user", "card", "card__deck")
    readonly_fields = ("user", "card", "known", "times_seen", "reviewed_at")

    def has_add_permission(self, request):
        return False

    @admin.display(description="Deck")
    def deck(self, obj):
        return obj.card.deck.title
