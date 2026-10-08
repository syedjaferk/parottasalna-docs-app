#!/bin/sh
# Dump the Postgres database to backups/portal-<date>.sql.gz and keep 14 days of dumps.
# If /etc/portal-backup.conf exists, also encrypt the dump (gpg, AES-256) and copy it off the
# server with rclone (e.g. Google Drive), keeping OFFSITE_KEEP_DAYS days there.
#
# Restore:  gunzip -c backups/portal-<date>.sql.gz | docker compose exec -T db psql -U portal portal
# From the off-site copy:
#   gpg -d portal-<date>.sql.gz.gpg | gunzip | docker compose exec -T db psql -U portal portal
set -eu

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP_DIR"
mkdir -p backups
chmod 700 backups

NAME="backups/portal-$(date +%F_%H%M).sql.gz"
TMP=$(mktemp backups/.dump.XXXXXX)
# Dump to a file first: in a pipe, a failed pg_dump would still leave a "valid" empty .gz.
if ! docker compose exec -T db pg_dump -U portal portal > "$TMP"; then
    rm -f "$TMP"
    echo "pg_dump failed." >&2
    exit 1
fi
gzip -c "$TMP" > "$NAME"
rm -f "$TMP"
chmod 600 "$NAME"
find backups -name 'portal-*.sql.gz' -mtime +14 -delete
echo "Backup written: $NAME ($(du -h "$NAME" | cut -f1))"

# ---------------------------------------------------------------- off-site copy
CONF=/etc/portal-backup.conf
if [ ! -f "$CONF" ]; then
    echo "Off-site copy: not configured ($CONF missing)."
    exit 0
fi
# shellcheck disable=SC1090
. "$CONF"   # OFFSITE_REMOTE, OFFSITE_KEEP_DAYS, PASSPHRASE_FILE
: "${OFFSITE_REMOTE:?set OFFSITE_REMOTE in $CONF}" "${PASSPHRASE_FILE:?set PASSPHRASE_FILE in $CONF}"

ENC="$NAME.gpg"
gpg --batch --yes --quiet --symmetric --cipher-algo AES256 \
    --passphrase-file "$PASSPHRASE_FILE" --output "$ENC" "$NAME"
if rclone copy --quiet "$ENC" "$OFFSITE_REMOTE"; then
    rm -f "$ENC"
    rclone delete --quiet --min-age "${OFFSITE_KEEP_DAYS:-30}d" --include 'portal-*.sql.gz.gpg' "$OFFSITE_REMOTE"
    echo "Off-site copy: $OFFSITE_REMOTE/$(basename "$ENC") (kept ${OFFSITE_KEEP_DAYS:-30} days)"
else
    rm -f "$ENC"
    echo "Off-site copy FAILED: could not upload to $OFFSITE_REMOTE (local backup is fine)." >&2
    exit 1
fi
