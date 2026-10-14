from django.contrib import admin

from .models import CodeSmell, SmellAnswer, SmellQuiz


class SmellQuizInline(admin.StackedInline):
    model = SmellQuiz
    extra = 0


@admin.register(CodeSmell)
class CodeSmellAdmin(admin.ModelAdmin):
    list_display = ("title", "number", "level", "order", "is_active")
    list_filter = ("level", "is_active")
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [SmellQuizInline]


@admin.register(SmellAnswer)
class SmellAnswerAdmin(admin.ModelAdmin):
    list_display = ("user", "smell", "is_correct", "answered_at")
    list_filter = ("is_correct",)
