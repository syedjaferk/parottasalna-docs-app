#!/bin/bash
# Runs each lesson script in a throwaway HOME and folder, so your own Git settings are never touched,
# and saves the real output next to it.   Usage: ./run.sh
cd "$(dirname "$0")"
for f in [0-9][0-9]-*.sh; do
  work=$(mktemp -d)
  mkdir "$work/home" "$work/play"
  (cd "$work/play" && HOME="$work/home" GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL="$work/home/.gitconfig" \
     GIT_AUTHOR_DATE="2026-01-05T10:00:00+0000" GIT_COMMITTER_DATE="2026-01-05T10:00:00+0000" \
     bash "$OLDPWD/$f") 2>&1 | sed "s#$work/play#~/work#g; s#$work/home#~#g" > "${f%.sh}.out"
  rm -rf "$work"
done
