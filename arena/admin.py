from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import LiveGame, LiveQuestion, LiveQuiz, Player


class LiveQuestionInline(admin.StackedInline):
    model = LiveQuestion
    extra = 1
    fields = ("order", "text", "choices", "time_limit", "points")
    formfield_overrides = {
        LiveQuestion._meta.get_field("choices").__class__: {"widget": forms.Textarea(attrs={"rows": 4, "cols": 60})},
    }


@admin.register(LiveQuiz)
class LiveQuizAdmin(admin.ModelAdmin):
    list_display = ("title", "question_count", "updated_at", "host_link")
    search_fields = ("title",)
    inlines = [LiveQuestionInline]
    readonly_fields = ("created_by",)

    @admin.display(description="Questions")
    def question_count(self, obj):
        return obj.questions.count()

    @admin.display(description="")
    def host_link(self, obj):
        return format_html('<a href="{}">Host live →</a>', reverse("arena_host_home"))

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class PlayerInline(admin.TabularInline):
    model = Player
    fields = ("nickname", "score", "joined_at")
    readonly_fields = fields
    extra = 0
    can_delete = False
    ordering = ("-score",)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(LiveGame)
class LiveGameAdmin(admin.ModelAdmin):
    list_display = ("quiz", "pin", "status", "player_count", "created_at", "results")
    list_filter = ("status",)
    readonly_fields = ("quiz", "host", "pin", "status", "current_index", "question_started_at", "created_at", "ended_at")
    inlines = [PlayerInline]

    @admin.display(description="Players")
    def player_count(self, obj):
        return obj.players.count()

    @admin.display(description="")
    def results(self, obj):
        return format_html('<a href="{}">CSV</a>', reverse("arena_results_csv", args=[obj.pk]))

    def has_add_permission(self, request):
        return False
