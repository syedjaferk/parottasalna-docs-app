from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "headline", "stage", "location", "updated_at")
    list_filter = ("stage",)
    search_fields = ("user__email", "user__first_name", "headline", "location")
    readonly_fields = ("user", "updated_at")
