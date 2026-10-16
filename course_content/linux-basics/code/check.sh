#!/usr/bin/env bash
# check.sh - checks your tryouts for one session and tells you what is done.
#
#   bash check.sh 3        check the tryouts of Session 3
#   bash check.sh all      check everything
LAB="$HOME/linux-lab"
PASS=0; FAIL=0

ok()   { echo "  [ OK ] $1"; PASS=$((PASS + 1)); }
bad()  { echo "  [TODO] $1"; FAIL=$((FAIL + 1)); }
check() { # check "description" command...
    local text="$1"; shift
    if "$@" >/dev/null 2>&1; then ok "$text"; else bad "$text"; fi
}
has_text() { grep -q -- "$1" "$2" 2>/dev/null; }

s1() {
    echo "Session 1 · First steps"
    check "~/linux-lab/playground/hello.txt exists"            test -f "$LAB/playground/hello.txt"
    check "hello.txt contains your own sentence (3+ words)"     bash -c "[ \$(wc -w < '$LAB/playground/hello.txt') -ge 3 ]"
    check "playground/whoami.txt holds your user name"          bash -c "[ \"\$(cat '$LAB/playground/whoami.txt' 2>/dev/null)\" = \"\$(whoami)\" ]"
}
s2() {
    echo "Session 2 · Files and directories"
    check "playground/map/a/b/c exists (a folder 3 levels deep)" test -d "$LAB/playground/map/a/b/c"
    check "playground/map/home-copy.txt lists your home folder"  bash -c "[ -s '$LAB/playground/map/home-copy.txt' ]"
    check "playground/map/where.txt says where you were"         bash -c "grep -q 'linux-lab' '$LAB/playground/map/where.txt'"
}
s3() {
    echo "Session 3 · Working with files"
    check "projects/website/{css,js,images} exist"               bash -c "test -d '$LAB/playground/projects/website/css' && test -d '$LAB/playground/projects/website/js' && test -d '$LAB/playground/projects/website/images'"
    check "index.html is inside projects/website"                test -f "$LAB/playground/projects/website/index.html"
    check "style.css was MOVED into css/ (not left behind)"      bash -c "test -f '$LAB/playground/projects/website/css/style.css' && ! test -f '$LAB/playground/projects/website/style.css'"
    check "a backup copy projects/website-backup exists"         test -d "$LAB/playground/projects/website-backup"
    check "the folder projects/old was deleted"                  bash -c "test -d '$LAB/playground/projects' && ! test -e '$LAB/playground/projects/old'"
}
s4() {
    echo "Session 4 · Reading and editing"
    check "playground/shopping.txt has 5 lines"                  bash -c "[ \$(wc -l < '$LAB/playground/shopping.txt') -eq 5 ]"
    check "playground/summary.txt holds the first 3 lines of app.log" bash -c "diff <(head -n 3 '$LAB/logs/app.log') '$LAB/playground/summary.txt'"
    check "playground/last-lines.txt holds the last 2 lines of app.log" bash -c "diff <(tail -n 2 '$LAB/logs/app.log') '$LAB/playground/last-lines.txt'"
}
s5() {
    echo "Session 5 · Pipes and text"
    check "playground/errors.txt has only the ERROR lines (3)"       bash -c "[ \$(wc -l < '$LAB/playground/errors.txt') -eq 3 ] && ! grep -v ERROR '$LAB/playground/errors.txt'"
    check "playground/fruit-counts.txt shows apple 3 first"      bash -c "head -n 1 '$LAB/playground/fruit-counts.txt' | grep -q 'apple' && head -n 1 '$LAB/playground/fruit-counts.txt' | grep -q '3'"
    check "playground/chennai.txt holds the 4 people from Chennai" bash -c "[ \$(grep -c Chennai '$LAB/playground/chennai.txt') -eq 4 ] && [ \$(wc -l < '$LAB/playground/chennai.txt') -eq 4 ]"
}
s6() {
    echo "Session 6 · Finding things"
    check "playground/log-files.txt lists the .log files"        bash -c "grep -q 'access.log' '$LAB/playground/log-files.txt' && grep -q 'app.log' '$LAB/playground/log-files.txt'"
    check "playground/count-404.txt contains the number of 404 lines" bash -c "[ \"\$(tr -d ' \n' < '$LAB/playground/count-404.txt')\" = \"\$(grep -c '\" 404 ' '$LAB/logs/access.log')\" ]"
}
s7() {
    echo "Session 7 · Users and permissions"
    check "playground/secret.txt exists and only YOU can read it (600)" bash -c "[ \"\$(stat -c %a '$LAB/playground/secret.txt' 2>/dev/null)\" = 600 ]"
    check "scripts/hello.sh is executable"                       test -x "$LAB/scripts/hello.sh"
    check "playground/shared.txt is 644"                         bash -c "[ \"\$(stat -c %a '$LAB/playground/shared.txt' 2>/dev/null)\" = 644 ]"
}
s8() {
    echo "Session 8 · Processes"
    check "playground/my-pid.txt holds the PID of a process you started" bash -c "p=\$(cat '$LAB/playground/my-pid.txt' 2>/dev/null); [ -n \"\$p\" ] && [[ \"\$p\" =~ ^[0-9]+\$ ]]"
    check "that sleep process was stopped (not running now)"     bash -c "p=\$(cat '$LAB/playground/my-pid.txt' 2>/dev/null); [ -n \"\$p\" ] && ! kill -0 \"\$p\" 2>/dev/null"
}
s9() {
    echo "Session 9 · Packages and network"
    check "playground/archive.tar.gz exists"                     test -f "$LAB/playground/archive.tar.gz"
    check "the archive contains docs/readme.txt"                 bash -c "tar -tzf '$LAB/playground/archive.tar.gz' | grep -q 'readme.txt'"
    check "playground/path.txt shows your PATH"                  bash -c "grep -q '/usr' '$LAB/playground/path.txt'"
}
s10() {
    echo "Session 10 · Shell scripting"
    check "scripts/greet.sh exists and is executable"            test -x "$LAB/scripts/greet.sh"
    check "greet.sh prints a greeting with the name you pass"    bash -c "'$LAB/scripts/greet.sh' Meena | grep -q Meena"
    check "scripts/backup.sh creates a copy of data/"            bash -c "test -x '$LAB/scripts/backup.sh' && cd '$LAB' && ./scripts/backup.sh >/dev/null 2>&1 && ls -d '$LAB'/backup* >/dev/null 2>&1"
}
s11() {
    echo "Session 11 · Troubleshooting"
    check "playground/disk-report.txt contains a disk usage report" bash -c "grep -q 'Filesystem' '$LAB/playground/disk-report.txt' || grep -q '%' '$LAB/playground/disk-report.txt'"
    check "playground/biggest.txt lists large files/folders"     bash -c "[ \$(wc -l < '$LAB/playground/biggest.txt') -ge 3 ]"
}

if [ ! -d "$LAB" ]; then echo "Run 'bash lab.sh' first."; exit 1; fi
case "${1:-}" in
    all) for n in 1 2 3 4 5 6 7 8 9 10 11; do "s$n"; echo; done ;;
    1|2|3|4|5|6|7|8|9|10|11) "s$1" ;;
    *) echo "Usage: bash check.sh <1-11|all>"; exit 1 ;;
esac
echo
echo "Done: $PASS OK, $FAIL still to do."
[ "$FAIL" -eq 0 ]
