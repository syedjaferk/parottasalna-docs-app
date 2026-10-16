#!/usr/bin/env bash
# report.sh - summary of the lab logs
LOG="$HOME/linux-lab/logs/app.log"

count_level() {            # a function: count lines of one level
    grep -c " $1 " "$LOG"
}

if [ ! -f "$LOG" ]; then
    echo "Log file not found: $LOG" >&2
    exit 2
fi

echo "Report for $LOG"
echo "  INFO : $(count_level INFO)"
echo "  WARN : $(count_level WARN)"
echo "  ERROR: $(count_level ERROR)"
