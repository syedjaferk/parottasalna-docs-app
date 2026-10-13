from django.apps import AppConfig


class ResumesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "resumes"
    verbose_name = "Resume review"

    def ready(self):
        from . import signals  # noqa: F401  (removes the PDF from Drive when a review is deleted)
