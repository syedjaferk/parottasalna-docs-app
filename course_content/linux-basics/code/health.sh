#!/usr/bin/env bash
# health.sh - a quick health check of this machine
set -u

echo "=== Health check: $(hostname) @ $(date '+%F %T') ==="

echo
echo "--- Disk (warn above 85%) ---"
df -h --output=target,pcent | tail -n +2 | while read -r mount pct; do
    use=${pct%\%}                       # strip the % sign
    if [ "$use" -ge 85 ]; then
        echo "WARNING: $mount is ${pct} full"
    else
        echo "ok: $mount ${pct}"
    fi
done

echo
echo "--- Memory ---"
free -h | awk 'NR==2 {print "used " $3 " of " $2 ", available " $7}'

echo
echo "--- Load (1 / 5 / 15 min) vs $(nproc) CPU cores ---"
uptime | awk -F'load average:' '{print $2}'

echo
echo "--- Biggest folders in your lab ---"
du -h --max-depth=1 ~/linux-lab 2>/dev/null | sort -rh | head -n 4

echo
echo "--- Errors in the lab log ---"
grep -c ERROR ~/linux-lab/logs/app.log
