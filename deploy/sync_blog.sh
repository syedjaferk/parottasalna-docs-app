#!/bin/sh
# Pull the latest posts from the vault repo and refresh the blog.
# Usage on the server:   /opt/course_portal/deploy/sync_blog.sh
# Optional cron (every 30 min):  */30 * * * * /opt/course_portal/deploy/sync_blog.sh >> /var/log/sync_blog.log 2>&1
set -e

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VAULT_DIR="${BLOG_SOURCE_DIR:-$APP_DIR/../second-brain}"

echo "$(date '+%F %T') pulling $VAULT_DIR"
git -C "$VAULT_DIR" pull --ff-only --quiet

cd "$APP_DIR"
# --prune removes posts you deleted from the vault, so the blog always mirrors it.
docker compose exec -T web python manage.py import_blog --prune
