#!/bin/sh
# Entry point for GitHub Actions. It is the ONLY thing the CI keys can run: on the server the
# keys sit in /home/deploy/.ssh/authorized_keys as forced commands, e.g.
#   command="sudo -n /opt/course_portal/deploy/ci.sh \"$SSH_ORIGINAL_COMMAND\"",restrict ssh-ed25519 …
#   command="sudo -n /opt/course_portal/deploy/ci.sh sync-blog",restrict ssh-ed25519 …   (blog repo)
#
# Tasks:  deploy [commit] | build-docs [slug|all] | load-practice [slug|all] | sync-blog | backup | status
set -eu
set -f  # never glob while splitting the request

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG=/var/log/portal_ci.log

# The request arrives as one string; split it into words (globbing is off).
# shellcheck disable=SC2086
set -- $*
TASK="${1:-}"
ARG="${2:-}"
[ $# -le 2 ] || { echo "Too many arguments." >&2; exit 2; }

matches() { printf '%s' "$2" | grep -Eqx "$1"; }
SLUG='all|[a-z0-9][a-z0-9-]{0,63}'
SHA='[0-9a-f]{7,40}'

reject() { echo "Rejected: '$TASK $ARG'. Allowed: deploy [commit], build-docs [slug|all], load-practice [slug|all], sync-blog, backup, status" >&2; exit 2; }

case "$TASK" in
    deploy) [ -z "$ARG" ] || matches "$SHA" "$ARG" || reject ;;
    build-docs|load-practice) ARG="${ARG:-all}"; matches "$SLUG" "$ARG" || reject ;;
    sync-blog|backup|status) [ -z "$ARG" ] || reject ;;
    *) reject ;;
esac

# One task at a time (two quick pushes, or a deploy during a blog sync).
exec 9>/tmp/portal-ci.lock
flock -w 900 9 || { echo "Another task is still running; gave up after 15 minutes." >&2; exit 1; }

echo "$(date '+%F %T') ${SUDO_USER:-$(id -un)} $TASK $ARG" >> "$LOG"
cd "$APP_DIR"

target() { if [ "$ARG" = all ]; then echo --all; else echo "$ARG"; fi; }

case "$TASK" in
    deploy)        exec "$APP_DIR/deploy/deploy.sh" "$ARG" ;;
    build-docs)    exec docker compose exec -T web python manage.py deploy_content --no-practice "$(target)" ;;
    load-practice) exec docker compose exec -T web python manage.py deploy_content --no-build "$(target)" ;;
    sync-blog)     exec "$APP_DIR/deploy/sync_blog.sh" ;;
    backup)        exec "$APP_DIR/deploy/backup_db.sh" ;;
    status)
        git log -1 --format='Deployed commit: %h %s (%cr)'
        docker compose ps --format 'table {{.Service}}\t{{.Status}}'
        ;;
esac
