#!/bin/sh
# Pull origin/main and apply it. Called by GitHub Actions through deploy/ci.sh, or by hand:
#   sudo /opt/course_portal/deploy/deploy.sh
#
# - App code changed (anything outside course_content/, docs/, .github/, deploy/*.sh, top-level *.md):
#   rebuild and restart the containers, then rebuild every course's docs.
# - Only course_content/<folder>/ changed: no restart; rebuild just those courses' docs and
#   reload their quizzes and flashcards.
set -eu

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP_DIR"
EXPECTED="${1:-}"

OLD=$(git rev-parse HEAD)
git fetch --quiet origin main
NEW=$(git rev-parse origin/main)

if [ -n "$EXPECTED" ] && ! git merge-base --is-ancestor "$EXPECTED" "$NEW"; then
    echo "Commit $EXPECTED is not on origin/main; refusing to deploy." >&2
    exit 1
fi
if [ "$OLD" = "$NEW" ]; then
    echo "Already at $(git log -1 --format='%h %s')."
    exit 0
fi

git merge --ff-only --quiet origin/main
echo "Updated $(git rev-parse --short "$OLD") → $(git log -1 --format='%h %s')"

CHANGED=$(git diff --name-only "$OLD" "$NEW")
APP_CHANGED=$(printf '%s\n' "$CHANGED" | grep -Ev '^(course_content/|docs/|\.github/|deploy/[^/]+\.sh$|[^/]+\.md$)' || true)
COURSE_DIRS=$(printf '%s\n' "$CHANGED" | sed -n 's#^course_content/\([^/]*\)/.*#\1#p' | sort -u | tr '\n' ' ')

wait_for_web() {
    # The entrypoint runs migrations before gunicorn starts; wait until they are applied.
    for _ in $(seq 1 60); do
        if docker compose exec -T web python manage.py migrate --check >/dev/null 2>&1; then
            return 0
        fi
        sleep 2
    done
    echo "The web container did not become ready in 2 minutes." >&2
    docker compose logs --tail 50 web >&2
    return 1
}

if [ -n "$APP_CHANGED" ]; then
    echo "App files changed:"
    printf '  %s\n' $APP_CHANGED
    # This script builds the docs itself (below) so a failure shows up in the Actions log.
    BUILD_DOCS_ON_START=false docker compose up -d --build --remove-orphans
    if printf '%s\n' "$APP_CHANGED" | grep -q '^deploy/docker/nginx.conf$'; then
        docker compose restart nginx
    fi
    wait_for_web
    docker compose exec -T web python manage.py deploy_content --all
elif [ -n "$COURSE_DIRS" ]; then
    echo "Course content changed: $COURSE_DIRS"
    # shellcheck disable=SC2086
    docker compose exec -T web python manage.py deploy_content $COURSE_DIRS
else
    echo "Only docs or workflow files changed; nothing to rebuild."
fi
echo "Deploy finished."
