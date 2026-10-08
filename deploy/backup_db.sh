#!/bin/sh
# Dump the Postgres database to backups/portal-<date>.sql.gz and keep 14 days of dumps.
# Restore:  gunzip -c backups/portal-<date>.sql.gz | docker compose exec -T db psql -U portal portal
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
