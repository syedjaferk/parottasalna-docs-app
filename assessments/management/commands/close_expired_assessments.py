"""Close timed attempts whose time ran out and that nobody submitted (grades the answers saved so far).

Run it every few minutes (cron) so results appear even if the student closed the browser:
    */5 * * * *  python manage.py close_expired_assessments
"""
from django.core.management.base import BaseCommand

from assessments.services import expire_stale


class Command(BaseCommand):
    help = "Grade and close timed-out assessment attempts."

    def handle(self, *args, **options):
        self.stdout.write(f"{expire_stale()} attempt(s) closed.")
