from datetime import timedelta

from django import forms
from django.contrib import admin
from django.utils import timezone

from .models import Cohort, Membership, Order, Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price_paise", "duration_days", "payment_url", "is_active", "sort_order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "starts_on", "price_paise", "payment_url", "seats", "course", "is_listed")
    list_filter = ("status", "is_listed")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("razorpay_order_id", "user", "plan", "cohort", "amount_paise", "status", "created_at", "paid_at")
    list_filter = ("status",)
    search_fields = ("razorpay_order_id", "razorpay_payment_id", "user__email")
    readonly_fields = [f.name for f in Order._meta.fields]

    def has_add_permission(self, request):
        return False


class MembershipForm(forms.ModelForm):
    ends_at = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
                                  help_text="Leave empty to use the plan's length, counted from today (or from the end of the current membership).")

    class Meta:
        model = Membership
        fields = "__all__"


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """Grant Pro by hand after you have taken payment elsewhere: pick the user and the plan, then save."""

    form = MembershipForm
    list_display = ("user", "plan", "starts_at", "ends_at")
    search_fields = ("user__email",)
    raw_id_fields = ("user", "order")

    def save_model(self, request, obj, form, change):
        if not obj.ends_at:
            now = timezone.now()
            current = Membership.objects.filter(user=obj.user, ends_at__gt=now).order_by("-ends_at").first()
            obj.ends_at = (current.ends_at if current else now) + timedelta(days=obj.plan.duration_days)
        super().save_model(request, obj, form, change)
