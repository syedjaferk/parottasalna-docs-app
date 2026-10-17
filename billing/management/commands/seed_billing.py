"""Create the starter Pro plan and the open cohort. Safe to re-run; edit the rows in the admin afterwards."""
from datetime import date

from django.core.management.base import BaseCommand

from billing.models import Cohort, Plan
from courses.models import Course


class Command(BaseCommand):
    help = "Create the starter Pro plan and cohort rows if they do not exist."

    def handle(self, *args, **options):
        plan, made = Plan.objects.get_or_create(slug="pro-yearly", defaults={
            "name": "Pro", "tagline": "Everything in the free courses, plus the premium practice paths.",
            "features": "All Pro courses\nEvery system design playground problem\nInterview prep packs and mock questions\nCertificate of completion\nSupports the free courses staying free",
            "price_paise": 99900, "duration_days": 365, "sort_order": 10})
        self.stdout.write(f"Plan {plan.slug}: {'created' if made else 'exists'}")
        course = Course.objects.filter(slug="data-engineering").first()
        cohort, made = Cohort.objects.get_or_create(slug="data-engineering-oct", defaults={
            "title": "End-to-End Data Engineering", "course": course,
            "summary": "40 days, live and mentor-led, with Databricks Data Engineer Associate exam prep.",
            "schedule": "Mon, Wed, Fri · 8-9 PM IST", "starts_on": date(2026, 10, 12), "price_paise": 0,
            "status": Cohort.Status.RUNNING})
        self.stdout.write(f"Cohort {cohort.slug}: {'created' if made else 'exists'} (set its price and status in the admin)")
