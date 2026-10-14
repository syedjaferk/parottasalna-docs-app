from django.urls import path

from . import views

urlpatterns = [
    path("calendar/daily.ics", views.daily_reminder, name="live_calendar_daily"),
    path("calendar/reset/", views.reset_calendar_link, name="live_calendar_reset"),
    path("calendar/<str:token>.ics", views.calendar_feed, name="live_calendar_feed"),
]
