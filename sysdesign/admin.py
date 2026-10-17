from django.contrib import admin

from .models import Problem, ProblemProgress


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "difficulty", "minutes", "is_pro", "is_published", "position", "updated_at")
    list_filter = ("difficulty", "is_pro", "is_published")
    list_editable = ("is_published", "position")
    search_fields = ("title", "slug", "tagline")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ProblemProgress)
class ProblemProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "problem", "current_step", "updated_at")
    list_filter = ("problem",)
    search_fields = ("user__email", "problem__slug")
    raw_id_fields = ("user",)
