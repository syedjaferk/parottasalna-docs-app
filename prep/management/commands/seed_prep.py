"""Load the interview-prep content from prep/data/*.json into the database (idempotent).

    python manage.py seed_prep
"""
from django.core.management.base import BaseCommand

from prep.seed import seed_prep


class Command(BaseCommand):
    help = "Create or update the prep catalog, pattern guides and placement quiz from prep/data/*.json."

    def handle(self, *args, **options):
        for table, (created, updated, deleted) in seed_prep().items():
            self.stdout.write(f"{table}: {created} created, {updated} updated, {deleted} removed")
        self.stdout.write(self.style.SUCCESS("Prep content loaded."))
