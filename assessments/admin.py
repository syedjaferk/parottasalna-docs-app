import csv

from django import forms
from django.contrib import admin
from django.db.models import Count
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html

from courses.security import csv_safe, no_store

from .models import Assessment, AssessmentAttempt, AssessmentQuestion


class QuestionInline(admin.StackedInline):
    model = AssessmentQuestion
    extra = 1
    fields = (("order", "points"), "text", "choices", "explanation")

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields["text"].widget = forms.Textarea(attrs={"rows": 3, "cols": 90})
        formset.form.base_fields["choices"].widget = forms.Textarea(attrs={"rows": 4, "cols": 90, "placeholder": "ls\n*pwd\ncd\ncat"})
        formset.form.base_fields["explanation"].widget = forms.Textarea(attrs={"rows": 2, "cols": 90})
        return formset


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "time_limit_minutes", "question_count", "max_attempts", "is_published", "links")
    list_filter = ("course", "is_published")
    list_editable = ("is_published",)
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [QuestionInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "course", "description", "is_published", "order")}),
        ("Time and attempts", {"fields": ("time_limit_minutes", "max_attempts", "opens_at", "closes_at", "pass_percentage")}),
        ("Behaviour", {"fields": ("shuffle_questions", "show_answers")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_questions=Count("questions"))

    @admin.display(description="Questions", ordering="_questions")
    def question_count(self, obj):
        return obj._questions

    @admin.display(description="Links")
    def links(self, obj):
        if not obj.pk:
            return ""
        return format_html('<a href="{}">Open</a> · <a href="{}">Results</a>',
                           reverse("assessment_detail", args=[obj.slug]), reverse("assessment_results", args=[obj.slug]))


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "assessment", "score_display", "percent", "timed_out", "started_at", "submitted_at")
    list_filter = ("assessment", "timed_out")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("assessment", "user", "started_at", "deadline", "submitted_at", "timed_out", "score", "max_score",
                       "answers", "question_order")
    actions = ["export_csv"]

    def has_add_permission(self, request):
        return False

    @admin.display(description="Score")
    def score_display(self, obj):
        return f"{obj.score}/{obj.max_score}" if obj.submitted_at else "in progress"

    @admin.display(description="%")
    def percent(self, obj):
        return f"{obj.percentage}%" if obj.submitted_at else ""

    @admin.action(description="Export selected attempts to CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="assessment-attempts.csv"'
        writer = csv.writer(response)
        writer.writerow(["Assessment", "Email", "Score", "Out of", "Percent", "Timed out", "Started", "Submitted"])
        for a in queryset.select_related("user", "assessment"):
            writer.writerow([csv_safe(v) for v in [a.assessment.title, a.user.email or a.user.username, a.score, a.max_score,
                                                   a.percentage, a.timed_out, a.started_at.isoformat(timespec="seconds"),
                                                   a.submitted_at.isoformat(timespec="seconds") if a.submitted_at else ""]])
        return no_store(response)
