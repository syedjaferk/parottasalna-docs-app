from django import forms
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Count

from .builder import build_in_background
from .models import Course, Enrollment
from .services import parse_emails


class CourseAdminForm(forms.ModelForm):
    bulk_emails = forms.CharField(
        label="Add users (bulk)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4, "cols": 60}),
        help_text="Gmail addresses separated by commas, spaces or new lines. "
        "They can sign in with Google as soon as they are added.",
    )

    class Meta:
        model = Course
        fields = "__all__"

    def clean_bulk_emails(self):
        valid, invalid = parse_emails(self.cleaned_data.get("bulk_emails", ""))
        if invalid:
            raise forms.ValidationError("Invalid email address(es): " + ", ".join(invalid))
        return valid


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    fields = ("email", "user", "added_at")
    readonly_fields = ("user", "added_at")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm
    list_display = ("title", "slug", "is_active", "is_common", "build_status", "last_built_at",
                    "user_count", "docs_link", "scores_link")
    list_filter = ("is_common", "is_active", "build_status")
    list_editable = ("is_common",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("build_status", "last_built_at", "build_log_display")
    inlines = [EnrollmentInline]
    actions = ["rebuild_docs"]
    fieldsets = (
        (None, {"fields": ("title", "slug", "description", "source_dir", "is_active", "is_common")}),
        ("Add users", {"fields": ("bulk_emails",)}),
        ("Documentation build", {"fields": ("build_status", "last_built_at", "build_log_display")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_users=Count("enrollments"))

    @admin.display(ordering="_users", description="Users")
    def user_count(self, obj):
        return "All students" if obj.is_common else obj._users

    @admin.display(description="Docs")
    def docs_link(self, obj):
        if obj.build_status != Course.BuildStatus.OK:
            return "-"
        return format_html('<a href="{}">Open</a>', reverse("course_docs", args=[obj.slug]))

    @admin.display(description="Quizzes")
    def scores_link(self, obj):
        return format_html('<a href="{}">Scores</a>', reverse("quiz_scoreboard", args=[obj.slug]))

    @admin.display(description="Build log")
    def build_log_display(self, obj):
        if not obj.build_log:
            return "-"
        return format_html(
            '<pre style="white-space:pre-wrap;max-height:300px;overflow:auto">{}</pre>',
            obj.build_log,
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Public vs enrolled changes the docs' search-engine tags, which are baked in at build time.
        if change and "is_common" in form.changed_data and obj.build_status == Course.BuildStatus.OK:
            build_in_background([obj.pk])
            self.message_user(request, f"Rebuilding “{obj.title}” docs for its new visibility.")

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        emails = form.cleaned_data.get("bulk_emails") or []
        added = sum(
            Enrollment.objects.get_or_create(course=form.instance, email=email)[1]
            for email in emails
        )
        if emails:
            self.message_user(
                request, f"{added} user(s) added; {len(emails) - added} were already enrolled."
            )

    @admin.action(description="Rebuild documentation for selected courses")
    def rebuild_docs(self, request, queryset):
        ids = list(queryset.values_list("pk", flat=True))
        build_in_background(ids)
        self.message_user(
            request, f"Started building {len(ids)} course(s). Refresh in a moment.",
            level=messages.INFO,
        )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("email", "course", "user", "added_at")
    list_filter = ("course",)
    search_fields = ("email",)
    readonly_fields = ("user",)
