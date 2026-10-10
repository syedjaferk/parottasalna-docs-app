from datetime import timedelta

from django import forms
from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils import timezone

from courses.models import Course

from .models import LiveSession, validate_meeting_url
from .services import schedule_series

WEEKDAYS = [(0, "Mon"), (1, "Tue"), (2, "Wed"), (3, "Thu"), (4, "Fri"), (5, "Sat"), (6, "Sun")]


class SeriesForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.filter(is_active=True))
    title = forms.CharField(
        max_length=200, initial="Session {n}",
        help_text="“{n}” becomes a running number (set “Number from”). Each day can be renamed later.",
    )
    number_from = forms.IntegerField(required=False, min_value=0, initial=1, label="Number from",
                                     help_text="Leave blank if the title has no {n}.")
    meet_url = forms.URLField(label="Google Meet link", max_length=300, validators=[validate_meeting_url])
    start_time = forms.TimeField(initial="20:00", widget=forms.TimeInput(attrs={"type": "time"}),
                                 help_text="India time (IST).")
    end_time = forms.TimeField(initial="21:00", widget=forms.TimeInput(attrs={"type": "time"}))
    weekdays = forms.TypedMultipleChoiceField(choices=WEEKDAYS, coerce=int, initial=[0, 1, 2, 3, 4, 5, 6],
                                              widget=forms.CheckboxSelectMultiple)
    first_day = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    last_day = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    description = forms.CharField(max_length=300, required=False)

    def clean(self):
        data = super().clean()
        first, last = data.get("first_day"), data.get("last_day")
        if first and last:
            if last < first:
                self.add_error("last_day", "Must be on or after the first day.")
            elif last - first > timedelta(days=366):
                self.add_error("last_day", "Schedule at most one year at a time.")
        if data.get("start_time") and data.get("start_time") == data.get("end_time"):
            self.add_error("end_time", "Must be different from the start time.")
        if "{n}" in data.get("title", "") and data.get("number_from") is None:
            self.add_error("number_from", "Set a starting number for {n}.")
        return data


@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "day", "time", "is_cancelled")
    list_filter = ("course", "is_cancelled")
    list_editable = ("is_cancelled",)
    search_fields = ("title", "course__title")
    date_hierarchy = "starts_at"
    ordering = ("-starts_at",)
    actions = ["cancel_sessions", "restore_sessions"]
    change_list_template = "admin/live/livesession/change_list.html"

    @admin.display(description="Day", ordering="starts_at")
    def day(self, obj):
        return f"{timezone.localtime(obj.starts_at):%a %d %b %Y}"

    @admin.display(description="Time (IST)")
    def time(self, obj):
        return f"{timezone.localtime(obj.starts_at):%I:%M %p} – {timezone.localtime(obj.ends_at):%I:%M %p}"

    @admin.action(description="Mark selected sessions as cancelled")
    def cancel_sessions(self, request, queryset):
        self.message_user(request, f"Cancelled {queryset.update(is_cancelled=True)} session(s).")

    @admin.action(description="Un-cancel selected sessions")
    def restore_sessions(self, request, queryset):
        self.message_user(request, f"Restored {queryset.update(is_cancelled=False)} session(s).")

    def get_urls(self):
        return [path("schedule/", self.admin_site.admin_view(self.schedule_view), name="live_schedule")] + super().get_urls()

    def schedule_view(self, request):
        if not self.has_add_permission(request):
            return redirect("admin:index")
        form = SeriesForm(request.POST or None, initial={"first_day": timezone.localdate()})
        if request.method == "POST" and form.is_valid():
            d = form.cleaned_data
            created, skipped = schedule_series(
                d["course"], d["title"], d["meet_url"], d["start_time"], d["end_time"], set(d["weekdays"]),
                d["first_day"], d["last_day"], number_from=d["number_from"], description=d["description"],
            )
            msg = f"Scheduled {created} session(s) for {d['course'].title}."
            if skipped:
                msg += f" Skipped {skipped} that already existed."
            self.message_user(request, msg, messages.SUCCESS if created else messages.WARNING)
            return redirect(reverse("admin:live_livesession_changelist"))
        context = {**self.admin_site.each_context(request), "title": "Schedule a series of live sessions",
                   "form": form, "opts": self.model._meta}
        return render(request, "admin/live/livesession/schedule.html", context)
