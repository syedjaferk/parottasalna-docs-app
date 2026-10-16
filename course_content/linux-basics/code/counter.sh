#!/usr/bin/env bash
# counter.sh - loops
for i in 1 2 3; do
    echo "Round $i"
done

count=3
while [ "$count" -gt 0 ]; do
    echo "countdown: $count"
    count=$((count - 1))
done
echo "Lift off!"
