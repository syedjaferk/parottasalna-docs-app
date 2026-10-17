from django.urls import path

from . import views

urlpatterns = [
    path("prep/", views.tracker, name="prep_tracker"),
    path("prep/patterns/", views.patterns, name="prep_patterns"),
    path("prep/data/<str:name>.json", views.data_file, name="prep_data"),
    path("prep/progress.json", views.progress_get, name="prep_progress"),
    path("prep/progress/set/", views.progress_set, name="prep_progress_set"),
    path("prep/progress/import/", views.progress_import, name="prep_progress_import"),
    path("prep/progress/clear/", views.progress_clear, name="prep_progress_clear"),
]
