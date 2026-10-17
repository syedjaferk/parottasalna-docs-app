"""Load the playground problems from sysdesign/data/*.json into the database (idempotent).

    python manage.py load_sysdesign
"""
from django.core.management.base import BaseCommand

from sysdesign.seed import load_problems


class Command(BaseCommand):
    help = "Create or update playground problems from sysdesign/data/*.json."

    def handle(self, *args, **options):
        created, updated = load_problems()
        self.stdout.write(self.style.SUCCESS(f"System design problems: {created} created, {updated} updated."))
