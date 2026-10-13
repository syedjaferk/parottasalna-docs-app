"""Retry report emails that didn't go out when the review finished (mailer down, not configured yet…).
Run every few minutes from cron (see README)."""
from django.core.management.base import BaseCommand

from resumes import mailer, services


class Command(BaseCommand):
    help = "Send resume review emails that haven't been sent yet."

    def handle(self, *args, **options):
        if not mailer.is_configured():
            self.stdout.write("Mailer not configured; nothing sent.")
            return
        pending = list(services.unsent_emails().filter(mail_attempts__lt=services.MAX_MAIL_ATTEMPTS)
                       .select_related("user").order_by("completed_at"))
        sent = sum(services.send_email(review) for review in pending)
        self.stdout.write(f"Sent {sent} of {len(pending)} pending email(s).")
