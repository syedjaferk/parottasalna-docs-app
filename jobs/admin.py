from django.contrib import admin, messages

from . import services
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "status", "posted_by", "created_at", "last_date")
    list_filter = ("status", "job_type", "work_mode")
    search_fields = ("title", "company", "location", "skills", "posted_by__email")
    readonly_fields = ("posted_by", "reviewed_by", "created_at", "updated_at", "published_at")
    actions = ["approve_jobs", "reject_jobs"]

    @admin.action(description="Approve selected jobs (make them live)")
    def approve_jobs(self, request, queryset):
        for job in queryset:
            job.approve(request.user)
            job.save()
        messages.success(request, f"Approved {queryset.count()} job(s).")

    @admin.action(description="Reject selected jobs")
    def reject_jobs(self, request, queryset):
        for job in queryset:
            services.reject(job, request.user)
        messages.info(request, f"Rejected {queryset.count()} job(s).")
