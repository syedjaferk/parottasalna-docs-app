from django.contrib import admin

from .models import CatalogLookup, CatalogProblem, CatalogSheet, PatternGuide, PlacementQuestion, ProblemProgress


@admin.register(ProblemProgress)
class ProblemProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "problem_id", "solved", "bookmarked", "updated_at")
    list_filter = ("solved", "bookmarked")
    search_fields = ("user__email", "problem_id")


@admin.register(CatalogProblem)
class CatalogProblemAdmin(admin.ModelAdmin):
    list_display = ("pid", "title", "platform", "difficulty", "position")
    list_filter = ("platform", "difficulty")
    search_fields = ("pid", "title")


@admin.register(CatalogLookup)
class CatalogLookupAdmin(admin.ModelAdmin):
    list_display = ("name", "count")

    @admin.display(description="entries")
    def count(self, obj):
        return len(obj.values)


@admin.register(CatalogSheet)
class CatalogSheetAdmin(admin.ModelAdmin):
    list_display = ("name", "sheet_id", "by", "kind", "position")


@admin.register(PatternGuide)
class PatternGuideAdmin(admin.ModelAdmin):
    list_display = ("pattern", "time", "space", "session", "position")
    search_fields = ("pattern", "kid")


@admin.register(PlacementQuestion)
class PlacementQuestionAdmin(admin.ModelAdmin):
    list_display = ("qid", "pattern", "q", "position")
    list_filter = ("pattern",)
    search_fields = ("q", "qid")
