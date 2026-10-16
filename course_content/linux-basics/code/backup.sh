#!/usr/bin/env bash
# backup.sh - copy a folder into a dated backup
set -eu                       # stop on errors and on unset variables
SRC="${1:-$HOME/linux-lab/data}"
STAMP=$(date +%F_%H%M)
DEST="$HOME/linux-lab/backup-$STAMP"

if [ ! -d "$SRC" ]; then
    echo "Nothing to back up: $SRC is not a folder" >&2
    exit 1
fi

cp -r "$SRC" "$DEST"
echo "Backed up $SRC -> $DEST"
