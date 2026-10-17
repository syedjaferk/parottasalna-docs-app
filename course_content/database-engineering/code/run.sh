#!/bin/sh
# Re-creates the practice database and saves the real output of each lesson script next to it.
# Usage: PSQL="psql -h /tmp -p 5544 -U postgres -d course" ./run.sh
PSQL=${PSQL:-psql -d course}
cd "$(dirname "$0")"
$PSQL -q -f 00-setup.sql
for f in [0-9][0-9]-*.sql; do
  [ "$f" = 00-setup.sql ] && continue
  $PSQL -X < "$f" > "${f%.sql}.out" 2>&1
done
