from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Poll


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ("code", "question", "is_open", "vote_count", "created_by", "created_at", "present_link")
    list_filter = ("is_open",)
    search_fields = ("code", "question")
    readonly_fields = ("code", "created_by", "created_at", "closed_at")

    @admin.display(description="Votes")
    def vote_count(self, obj):
        return obj.votes.count()

    @admin.display(description="")
    def present_link(self, obj):
        return format_html('<a href="{}">Present →</a>', reverse("poll_present", args=[obj.code]))

    def has_add_permission(self, request):
        return False   # create polls from /polls/ so they get a code
