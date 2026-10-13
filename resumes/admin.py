from django.contrib import admin, messages

from . import services
from .models import ResumeReview


@admin.register(ResumeReview)
class ResumeReviewAdmin(admin.ModelAdmin):
    list_display = ("tracking_id", "email", "status", "ats_score", "target_role", "created_at", "mailed_at",
                    "file_deleted_at")
    list_filter = ("status",)
    search_fields = ("tracking_id", "email", "target_role")
    readonly_fields = ("tracking_id", "user", "email", "file_name", "target_role", "drive_file_id", "result",
                       "ats_score", "flags", "attempts", "consented_at", "created_at", "claimed_at",
                       "completed_at", "file_deleted_at", "mailed_at", "mail_attempts")
    actions = ["release_reviews", "requeue_reviews", "resend_email"]

    @admin.action(description="Checked: show the held review(s) to the user")
    def release_reviews(self, request, queryset):
        held = queryset.filter(status=ResumeReview.Status.HELD)
        for review in held:
            services.release(review)
        messages.success(request, f"Released {held.count()} review(s).")

    @admin.action(description="Review again (send back to the queue)")
    def requeue_reviews(self, request, queryset):
        done = sum(services.requeue(r) for r in queryset)
        messages.info(request, f"Queued {done} review(s); ones whose PDF is already deleted were skipped.")

    @admin.action(description="Email the report (or failure notice) again")
    def resend_email(self, request, queryset):
        sent = 0
        for review in queryset.select_related("user"):
            review.mailed_at = None
            sent += services.send_email(review)
        messages.info(request, f"Sent {sent} email(s). Reviews that aren't finished or held are skipped; "
                               "failures are in the logs.")
