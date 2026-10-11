"""Check the Calendly connection used by the admin panel:  python manage.py check_calendly

Prints who the token belongs to and how many upcoming calls it can see. Never prints the token."""
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from panel import calendly


class Command(BaseCommand):
    help = "Test CALENDLY_TOKEN against the Calendly API (needs scopes: users:read, scheduled_events:read)."

    def handle(self, *args, **options):
        raw = os.environ.get("CALENDLY_TOKEN", "")
        token = settings.CALENDLY_TOKEN
        if not token:
            raise CommandError("CALENDLY_TOKEN is empty. Add it to the server's .env and restart the web container.")
        self.stdout.write(f"Token: {len(token)} characters")
        if raw != raw.strip() or raw[:1] in "\"'" or raw[-1:] in "\"'":
            self.stdout.write(self.style.WARNING("The value has quotes or spaces around it: remove them in .env."))
        if token.count(".") != 2:
            self.stdout.write(self.style.WARNING("That doesn't look like a Calendly personal access token "
                                                 "(expected a long token with two dots). Was it copied completely?"))
        try:
            me = calendly._get("/users/me", scope="users:read")["resource"]
            self.stdout.write(self.style.SUCCESS(f"Connected as {me.get('name')} <{me.get('email')}>"))
            calls, error = calendly.upcoming_calls(refresh=True)
        except calendly.CalendlyError as exc:
            raise CommandError(str(exc))
        if error:
            raise CommandError(error)
        self.stdout.write(self.style.SUCCESS(f"Upcoming calls visible: {len(calls)}"))
