from django.contrib import admin

from .models import ProblemProgress


@admin.register(ProblemProgress)
class ProblemProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "problem_id", "solved", "bookmarked", "updated_at")
    list_filter = ("solved", "bookmarked")
    search_fields = ("user__email", "problem_id")
