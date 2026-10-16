#!/usr/bin/env bash
# lab.sh - creates the practice folder ~/linux-lab with sample files for every session.
#
#   bash lab.sh            create it (does nothing to files you already changed)
#   bash lab.sh --reset    delete ~/linux-lab and create it again from scratch
set -eu

LAB="$HOME/linux-lab"

if [ "${1:-}" = "--reset" ] && [ -d "$LAB" ]; then
    rm -rf "$LAB"
    echo "Old lab removed."
fi

mkdir -p "$LAB"/{data,logs,docs,scripts,playground}

# ---- data/fruits.txt: a messy list (unsorted, with repeats)
[ -f "$LAB/data/fruits.txt" ] || printf '%s\n' banana apple mango apple cherry banana grape mango apple kiwi cherry orange > "$LAB/data/fruits.txt"

# ---- data/people.csv: a small table
[ -f "$LAB/data/people.csv" ] || cat > "$LAB/data/people.csv" <<'EOF'
name,city,age,role
Asha,Chennai,29,developer
Bala,Madurai,34,tester
Chitra,Chennai,41,manager
Dinesh,Coimbatore,25,developer
Esha,Madurai,31,designer
Farook,Chennai,38,developer
Gita,Trichy,27,tester
Hari,Coimbatore,45,manager
Indu,Chennai,23,designer
Jeeva,Trichy,36,developer
EOF

# ---- logs/access.log: 60 web-server lines, made the same way every time
if [ ! -f "$LAB/logs/access.log" ]; then
    paths=(/ /index.html /about /login /products /cart /api/items /missing /admin)
    codes=(200 200 200 200 301 404 200 500 403)
    ips=(10.0.0.5 10.0.0.7 192.168.1.20 172.16.4.9 10.0.0.5 203.0.113.8)
    for i in $(seq 0 59); do
        ip=${ips[$((i % 6))]}
        path=${paths[$(( (i * 7) % 9 ))]}
        code=${codes[$(( (i * 5) % 9 ))]}
        size=$(( 500 + (i * 137) % 4000 ))
        hour=$(( 8 + i / 10 ))
        minute=$(( (i * 11) % 60 ))
        printf '%s - - [15/Oct/2026:%02d:%02d:00 +0530] "GET %s HTTP/1.1" %s %s\n' "$ip" "$hour" "$minute" "$path" "$code" "$size"
    done > "$LAB/logs/access.log"
fi

# ---- logs/app.log: an application log with levels
[ -f "$LAB/logs/app.log" ] || cat > "$LAB/logs/app.log" <<'EOF'
2026-10-15 09:00:01 INFO  server started on port 8080
2026-10-15 09:00:05 INFO  connected to database
2026-10-15 09:02:11 WARN  slow query took 2.4s
2026-10-15 09:05:30 INFO  user asha logged in
2026-10-15 09:07:42 ERROR payment failed for order 1042
2026-10-15 09:07:43 INFO  retrying payment for order 1042
2026-10-15 09:07:45 INFO  payment ok for order 1042
2026-10-15 09:15:09 WARN  disk usage at 81%
2026-10-15 09:20:00 INFO  user bala logged in
2026-10-15 09:31:12 ERROR cannot send email to user chitra
2026-10-15 09:44:50 INFO  backup completed
2026-10-15 09:59:59 ERROR database connection lost
2026-10-15 10:00:02 INFO  connected to database
EOF

# ---- docs and a tiny script
[ -f "$LAB/docs/readme.txt" ] || printf 'Welcome to the Linux lab!\nThis folder is safe. Break things here.\n' > "$LAB/docs/readme.txt"
[ -f "$LAB/docs/notes.md" ]   || printf '# My notes\n\n- learn ls\n- learn cd\n- learn grep\n' > "$LAB/docs/notes.md"
[ -f "$LAB/scripts/hello.sh" ] || printf '#!/usr/bin/env bash\necho "Hello from a script!"\n' > "$LAB/scripts/hello.sh"

echo "Lab ready at $LAB"
ls "$LAB"
