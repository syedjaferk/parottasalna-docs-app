from django.urls import path

from . import views

urlpatterns = [
    path("assessments/", views.assessment_list, name="assessment_list"),
    path("assessments/attempts/<int:pk>/", views.assessment_take, name="assessment_take"),
    path("assessments/attempts/<int:pk>/save/", views.assessment_save, name="assessment_save"),
    path("assessments/attempts/<int:pk>/result/", views.assessment_result, name="assessment_result"),
    path("assessments/<slug:slug>/", views.assessment_detail, name="assessment_detail"),
    path("assessments/<slug:slug>/start/", views.assessment_start, name="assessment_start"),
    path("assessments/<slug:slug>/results/", views.assessment_results, name="assessment_results"),
    path("assessments/<slug:slug>/results.csv", views.assessment_results_csv, name="assessment_results_csv"),
]
