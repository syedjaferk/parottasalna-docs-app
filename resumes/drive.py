"""Google Drive storage for uploaded resumes.

The portal only creates files in one folder and later deletes them (scope drive.file). Credentials come
from GDRIVE_CREDENTIALS_FILE, either:
  - an OAuth token for a normal Google account, made with  manage.py drive_authorize  (simplest; works with
    a personal Gmail too). drive.file only reaches files and folders this app created, so that command also
    creates the folder. The worker can use the same token file to download.
  - a service account key: put the folder on a *shared drive* and add the service account as a member
    (service accounts have no storage of their own, so uploads to a My Drive folder fail).
"""
import json
import logging
import secrets
import threading

from django.conf import settings

log = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files"
FILES_URL = "https://www.googleapis.com/drive/v3/files"
TIMEOUT = 30  # seconds per request

_session = None
_lock = threading.Lock()


class DriveError(Exception):
    pass


def is_configured():
    return bool(settings.GDRIVE_CREDENTIALS_FILE and settings.RESUME_DRIVE_FOLDER_ID)


def _get_session():
    global _session
    with _lock:
        if _session is None:
            import google.auth
            import google.auth.exceptions
            from google.auth.transport.requests import AuthorizedSession
            try:
                # A user token keeps the scopes it was granted; a service account gets SCOPES.
                creds, _ = google.auth.load_credentials_from_file(
                    settings.GDRIVE_CREDENTIALS_FILE, default_scopes=SCOPES)
            except (OSError, ValueError, google.auth.exceptions.GoogleAuthError) as e:
                raise DriveError(f"Can't load Drive credentials: {e}") from e
            _session = AuthorizedSession(creds)
        return _session


def _request(method, url, **kwargs):
    import google.auth.exceptions
    import requests
    try:
        return _get_session().request(method, url, timeout=TIMEOUT, **kwargs)
    except (requests.RequestException, google.auth.exceptions.GoogleAuthError) as e:
        raise DriveError(f"Drive request failed: {e}") from e


def upload_pdf(data, name, tracking_id):
    """Upload bytes as a PDF into the resume folder. Returns the Drive file ID."""
    boundary = f"resume-{secrets.token_hex(16)}"
    meta = {
        "name": name,
        "mimeType": "application/pdf",
        "parents": [settings.RESUME_DRIVE_FOLDER_ID],
        "appProperties": {"tracking_id": tracking_id},
    }
    body = (
        f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{json.dumps(meta)}\r\n"
        f"--{boundary}\r\nContent-Type: application/pdf\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    resp = _request(
        "POST", UPLOAD_URL,
        params={"uploadType": "multipart", "supportsAllDrives": "true", "fields": "id"},
        data=body, headers={"Content-Type": f"multipart/related; boundary={boundary}"},
    )
    if resp.status_code != 200:
        raise DriveError(f"Drive upload failed: HTTP {resp.status_code} {resp.text[:300]}")
    return resp.json()["id"]


def create_folder(name, session):
    """Create a folder in My Drive with the given authorised session. Returns its ID."""
    resp = session.post(FILES_URL, params={"fields": "id"}, timeout=TIMEOUT,
                        json={"name": name, "mimeType": "application/vnd.google-apps.folder"})
    if resp.status_code != 200:
        raise DriveError(f"Creating the folder failed: HTTP {resp.status_code} {resp.text[:300]}")
    return resp.json()["id"]


def delete_file(file_id):
    """Delete a file for good (not to the bin). A file that's already gone counts as deleted."""
    resp = _request("DELETE", f"{FILES_URL}/{file_id}", params={"supportsAllDrives": "true"})
    if resp.status_code not in (200, 204, 404):
        raise DriveError(f"Drive delete failed: HTTP {resp.status_code} {resp.text[:300]}")
