"""Send email through the Parottasalna mailer (listmonk, a separate self-hosted service: ../mailer).

The portal renders and escapes the whole email itself (Django templates) and listmonk's pass-through
template sends it unchanged. Recipients aren't stored in listmonk (subscriber_mode "external"), and the
portal's API user can only send transactional mail.
"""
import requests
from django.conf import settings

TIMEOUT = 15


class MailerError(Exception):
    pass


def is_configured():
    return bool(settings.MAILER_URL and settings.MAILER_API_USER and settings.MAILER_API_TOKEN
                and settings.MAILER_TEMPLATE_ID)


def send(to, subject, html, text):
    if not is_configured():
        raise MailerError("mailer not configured (MAILER_URL, MAILER_API_USER, MAILER_API_TOKEN, MAILER_TEMPLATE_ID)")
    try:
        resp = requests.post(
            f"{settings.MAILER_URL.rstrip('/')}/api/tx",
            auth=(settings.MAILER_API_USER, settings.MAILER_API_TOKEN),
            json={
                "subscriber_emails": [to],
                "subscriber_mode": "external",
                "template_id": settings.MAILER_TEMPLATE_ID,
                "subject": subject,
                "content_type": "html",
                "data": {"html": html},
                "altbody": text,
            },
            timeout=TIMEOUT,
        )
    except requests.RequestException as e:
        raise MailerError(f"mailer unreachable: {e}") from e
    if resp.status_code != 200:
        raise MailerError(f"mailer refused: HTTP {resp.status_code} {resp.text[:300]}")
