from django.urls import path

from . import api, views

urlpatterns = [
    path("resume-review/", views.upload, name="resume_upload"),
    path("resume-review/mine/", views.mine, name="resume_mine"),
    path("resume-review/<str:tracking_id>/", views.status, name="resume_status"),
    path("resume-review/<str:tracking_id>/delete/", views.delete, name="resume_delete"),
    # Worker API (resumes/api.py)
    path("api/ats/claim/", api.claim, name="ats_claim"),
    path("api/ats/<str:tracking_id>/complete/", api.complete, name="ats_complete"),
    path("api/ats/<str:tracking_id>/fail/", api.fail, name="ats_fail"),
]
