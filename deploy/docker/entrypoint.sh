#!/bin/sh
set -e

# Only the web container migrates; the WebSocket container (ws) sets RUN_MIGRATIONS=false.
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    python manage.py migrate --noinput
fi

# Rebuild every active course so new markdown is picked up after a restart. This runs in the
# background: the web server starts at once and serves the previous build until it finishes.
if [ "${BUILD_DOCS_ON_START:-true}" = "true" ]; then
    (python manage.py build_docs || echo "Some course builds failed; see the admin for logs.") &
fi

exec "$@"
