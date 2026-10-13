"""Delete resume PDFs from Google Drive once their review has been finished for RESUME_RETENTION_DAYS.
The report stays, so the user can still read it. Run daily from cron (see README)."""
from django.core.management.base import BaseCommand

from resumes import drive, services


class Command(BaseCommand):
    help = "Delete resume PDFs from Google Drive after the retention period."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, help="Override RESUME_RETENTION_DAYS.")
        parser.add_argument("--dry-run", action="store_true", help="List what would be deleted.")

    def handle(self, *args, days=None, dry_run=False, **options):
        deleted = failed = 0
        for review in services.expired_files(days):
            if dry_run:
                self.stdout.write(f"would delete {review.tracking_id} ({review.drive_file_id})")
                continue
            try:
                services.delete_file(review)
                deleted += 1
            except drive.DriveError as e:
                failed += 1
                self.stderr.write(f"{review.tracking_id}: {e}")
        if not dry_run:
            self.stdout.write(f"Deleted {deleted} resume PDF(s) from Drive; {failed} failed.")
        if failed:
            raise SystemExit(1)
