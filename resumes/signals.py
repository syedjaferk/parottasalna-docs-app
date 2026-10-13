"""When a review is deleted any other way (admin, or the user's account is deleted), remove its PDF too."""
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import ResumeReview
from .services import delete_quietly


@receiver(post_delete, sender=ResumeReview)
def delete_pdf_from_drive(sender, instance, **kwargs):
    if instance.drive_file_id:
        delete_quietly(instance.drive_file_id)
