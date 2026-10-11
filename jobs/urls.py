from django.urls import path

from . import views

# Action routes come before the "<pk>/<slug>/" detail route, which would otherwise swallow "edit", "delete"…
urlpatterns = [
    path("jobs/", views.job_list, name="job_list"),
    path("jobs/new/", views.job_new, name="job_new"),
    path("jobs/mine/", views.job_mine, name="job_mine"),
    path("jobs/review/", views.job_review, name="job_review"),
    path("jobs/<int:pk>/edit/", views.job_edit, name="job_edit"),
    path("jobs/<int:pk>/delete/", views.job_delete, name="job_delete"),
    path("jobs/<int:pk>/moderate/", views.job_moderate, name="job_moderate"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail_short"),
    path("jobs/<int:pk>/<slug:slug>/", views.job_detail, name="job_detail"),
]
