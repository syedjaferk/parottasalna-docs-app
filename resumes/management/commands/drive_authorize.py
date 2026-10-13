"""One-time setup for resume uploads with your own Google account (no service account needed).

Opens a browser to sign in to Google, saves an OAuth token (scope drive.file), and creates the folder the
resumes go into. Run it on a computer with a browser, then copy the token to the server. Needs an OAuth
client of type "Desktop app" (Google Cloud Console → APIs & Services → Credentials).

    python manage.py drive_authorize --client-secrets client_secret.json --token secrets/drive-token.json
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from resumes import drive


class Command(BaseCommand):
    help = "Sign in to Google Drive once, save the token, and create the resume folder."

    def add_arguments(self, parser):
        parser.add_argument("--client-secrets", type=Path, default=Path("client_secret.json"),
                            help="OAuth client JSON (type: Desktop app).")
        parser.add_argument("--token", type=Path, default=Path("secrets/drive-token.json"),
                            help="Where to save the token.")
        parser.add_argument("--folder-name", default="Resume reviews")
        parser.add_argument("--no-folder", action="store_true", help="Only save the token.")

    def handle(self, *args, client_secrets, token, folder_name, no_folder, **options):
        client_secrets, token = Path(client_secrets), Path(token)
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
        except ImportError:
            raise CommandError("pip install google-auth-oauthlib")
        if not client_secrets.exists():
            raise CommandError(f"{client_secrets} not found. Download it from Google Cloud Console → "
                               "Credentials → OAuth client ID (Desktop app).")
        flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets), drive.SCOPES)
        # offline + consent: always return a refresh token, so the server can keep working on its own
        creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        token.parent.mkdir(parents=True, exist_ok=True)
        # to_json() leaves out "type", which google.auth.load_credentials_from_file needs
        token.write_text(json.dumps({**json.loads(creds.to_json()), "type": "authorized_user"}, indent=1))
        token.chmod(0o600)
        self.stdout.write(self.style.SUCCESS(f"Saved the token to {token}"))
        if no_folder:
            return
        from google.auth.transport.requests import AuthorizedSession
        folder_id = drive.create_folder(folder_name, AuthorizedSession(creds))
        self.stdout.write(self.style.SUCCESS(f'Created the folder "{folder_name}" in your My Drive.'))
        self.stdout.write(f"\nAdd to .env:\n  GDRIVE_CREDENTIALS_FILE={token.resolve()}\n"
                          f"  RESUME_DRIVE_FOLDER_ID={folder_id}\n"
                          f"(on the server in Docker: GDRIVE_CREDENTIALS_FILE=/app/secrets/{token.name})")
