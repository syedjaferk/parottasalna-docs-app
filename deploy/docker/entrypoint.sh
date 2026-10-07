#!/bin/sh
set -e

python manage.py migrate --noinput

# Rebuild every active course on start so new markdown is picked up after a restart.
if [ "${BUILD_DOCS_ON_START:-true}" = "true" ]; then
    python manage.py build_docs || echo "Some course builds failed; see the admin for logs."
fi

exec "$@"
