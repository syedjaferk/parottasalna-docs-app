"""One-time: copy everything the blog still needs from WordPress into the Obsidian vault.

    python manage.py localize_blog_vault /path/to/second-brain --dry-run   # preview
    python manage.py localize_blog_vault /path/to/second-brain             # write

Run it while WordPress (BLOG_WORDPRESS_URL) is still online. Afterwards the vault alone is enough:
`import_blog --no-wordpress` produces the same blog. Commit the vault changes with git.
"""
from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from blog.management.commands.import_blog import fetch_wordpress, wordpress_session
from blog.vault import localize_vault


_session = wordpress_session()


def download(url: str) -> bytes:
    response = _session.get(url, timeout=30)
    response.raise_for_status()
    kind = response.headers.get("Content-Type", "")
    if not (kind.startswith("image/") or kind.startswith("application/pdf")):
        raise ValueError(f"not an image or PDF: {kind}")
    return response.content


class Command(BaseCommand):
    help = "Download WordPress images, repaired code and post links into the vault, so the blog no longer needs WordPress."

    def add_arguments(self, parser):
        parser.add_argument("source", nargs="?", help="Vault folder (default: BLOG_SRC_ROOT)")
        parser.add_argument("--dry-run", action="store_true", help="Show what would change; write nothing")

    def handle(self, source, dry_run, **options):
        root = Path(source or settings.BLOG_SRC_ROOT).expanduser().resolve()
        if not root.is_dir():
            raise CommandError(f"Vault folder not found: {root}")
        if not settings.BLOG_WORDPRESS_URL:
            raise CommandError("Set BLOG_WORDPRESS_URL to the live WordPress site; that's where the copies come from.")
        try:
            wordpress = fetch_wordpress(settings.BLOG_WORDPRESS_URL, self.stdout.write)
        except (requests.RequestException, ValueError) as exc:
            raise CommandError(f"Couldn't read WordPress: {exc}")

        report = localize_vault(root, settings.BLOG_WORDPRESS_URL, wordpress, download,
                                dry_run=dry_run, log=self.stdout.write)
        prefix = "Would change" if dry_run else "Changed"
        self.stdout.write(self.style.SUCCESS(
            f"{prefix} {report.files_changed} post files: {report.code_blocks} code blocks repaired, "
            f"{report.images_relinked} image references pointed at attachments/, "
            f"{report.links_relinked} links turned into [[wikilinks]]."))
        if not dry_run:
            self.stdout.write(f"Downloaded {report.images_downloaded} images into {root / 'attachments'}.")
        if report.failed_downloads:
            self.stderr.write(self.style.WARNING(
                f"{len(report.failed_downloads)} image(s) couldn't be downloaded and still point to WordPress: "
                + ", ".join(report.failed_downloads[:10]) + (" …" if len(report.failed_downloads) > 10 else "")))
        if report.external_post_links:
            self.stdout.write(f"{report.external_post_links} link(s) point to WordPress posts that aren't in the "
                              "vault; they were left unchanged.")
