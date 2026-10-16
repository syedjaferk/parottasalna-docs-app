# Session 11 · Troubleshooting

**⏱ about 90 minutes · 🧰 you need: [Session 10](10-shell-scripting.md) done**

## The big idea

Everything breaks eventually: a disk fills up, a program freezes, a website won't load. What separates a beginner from a capable admin is
**not knowing every answer**. It's having a **method** and knowing **where Linux keeps its evidence**. Today you learn the vital signs of a machine,
where the logs are, and a calm, repeatable way to find the cause.

**Everyday example:** a doctor. She doesn't guess. She asks *"what are the symptoms?"*, checks the **vital signs** (temperature, pulse),
reads the **medical history** (logs), forms a guess, tests it, and only then treats. You'll do exactly the same with a computer.

```{raw} html
:file: ../diagrams/l11-method.html
```

## 1. The method: five calm steps

| Step | Ask yourself | Example |
|---|---|---|
| **1. Describe** | What *exactly* is wrong? What changed? | "The website returns errors since 10:00." |
| **2. Check the vital signs** | Disk? Memory? CPU? Is the program running? | `df -h`, `free -h`, `uptime`, `systemctl status` |
| **3. Read the logs** | What does the system *say*? | `tail`, `journalctl`, `grep ERROR` |
| **4. Form one guess and test it** | Change **one** thing at a time | restart the service, fix the permission |
| **5. Confirm and write it down** | Is it really fixed? Note the cause | so you (and others) never repeat it |

**The golden rules:** read the **whole error message** (the answer is usually in it); change **one thing at a time**; **copy before you edit**
(`cp file file.bak`); never fix a problem by `chmod 777` or `sudo rm -rf`.

## 2. Vital signs

### Disk space: `df`

```bash
df -h
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2  468G  339G  106G  77% /
tmpfs           3.8G  1.2M  3.8G   1% /run
/dev/nvme0n1p1  511M  6.1M  505M   2% /boot/efi
```

| Column | Meaning |
|---|---|
| `Size` / `Used` / `Avail` | total, used, free |
| `Use%` | **watch this**: above ~90% is a warning, 100% is an outage |
| `Mounted on` | where this disk appears in the tree |

(Disks and mount points differ on your computer.) Also check **inodes**, the number of files a disk can hold. A disk can be "full" with plenty of
space left if it has millions of tiny files: `df -i`.

### What is using the space? `du`

```bash
du -h --max-depth=1 ~/linux-lab | sort -rh
```

```text
56K	/home/asha/linux-lab
16K	/home/asha/linux-lab/logs
12K	/home/asha/linux-lab/docs
12K	/home/asha/linux-lab/data
...
```

The routine for **"disk is full"**: `df -h` → find the full disk → `du -h --max-depth=1 /that/place | sort -rh | head` → go **one level deeper** into the biggest
folder → repeat until you find the culprit (usually logs, caches, or old backups).

### Memory, CPU and load

```bash
free -h
uptime
top          # press q to quit
```

| Signal | Healthy | Worry when |
|---|---|---|
| **`available`** memory (`free -h`) | a good share left | close to 0, and swap is heavily used |
| **load average** (`uptime`) | below the number of CPU cores (`nproc`) | above it for a long time |
| a single process in `top` | uses little | one process holds ~100% CPU or most memory |

### Who is listening on a port? `ss` and `lsof`

```bash
ss -tlnp | head
sudo lsof -i :8080       # which program is using port 8080?
```

Typical error *"Address already in use"* means another program already holds that port. Find it, then stop it or choose another port.

## 3. Logs: the system's diary

Linux writes down **what happened**. Learn where to look:

| Where | What's in it |
|---|---|
| `/var/log/syslog` (Debian/Ubuntu) or `/var/log/messages` (RHEL) | general system messages |
| `/var/log/auth.log` (or `/var/log/secure`) | **logins** and `sudo` use |
| `/var/log/nginx/`, `/var/log/apache2/` | web-server access and error logs |
| `/var/log/dpkg.log` | what `apt` installed |
| `dmesg` | kernel messages (hardware, disks, USB) |
| **`journalctl`** | the central journal of **systemd** services |

### Reading logs with what you already know

```bash
cd ~/linux-lab/logs
tail -n 5 app.log                 # the latest lines
grep ERROR app.log                # only the errors
grep -c ERROR app.log             # how many?
tail -f app.log                   # watch live (Ctrl+C to stop)
```

```text
2026-10-15 09:07:42 ERROR payment failed for order 1042
2026-10-15 09:31:12 ERROR cannot send email to user chitra
2026-10-15 09:59:59 ERROR database connection lost
```

**What to look at in an error line:** the **time** (does it match when the problem began?), the **level** (ERROR/WARN), and the **message**. Then look at the
lines **just before** the first ERROR: the cause is often there.

```bash
grep -n -B2 -A1 "database connection lost" app.log
```

`-B2` shows 2 lines **b**efore, `-A1` shows 1 line **a**fter: the surrounding context.

### `journalctl` (systemd systems)

```bash
journalctl -u ssh --since "1 hour ago"     # one service, recent
journalctl -p err -b                       # only errors since the last boot
journalctl -f                              # follow live
sudo journalctl --disk-usage               # how big is the journal?
```

| Option | Meaning |
|---|---|
| `-u NAME` | one **u**nit (service) |
| `--since`, `--until` | time range (`"2026-10-15 09:00"`, `"10 min ago"`) |
| `-p err` | priority: only errors (or worse) |
| `-b` | since the current **b**oot (`-b -1` = the previous boot) |
| `-f` | **f**ollow, like `tail -f` |
| `-n 50` | last 50 lines |

## 4. A casebook: symptom → cause → fix

| Symptom | Likely cause | How to check | Fix |
|---|---|---|---|
| `No space left on device` | a disk or inodes are full | `df -h`, `df -i`, `du ... \| sort -rh` | delete old logs/caches, resize disk |
| `Permission denied` | file or folder permissions | `ls -l`, `ls -ld folder`, `id` | `chmod`/`chown` the **right** thing; use `sudo` only if needed |
| `command not found` | not installed, or not on `PATH` | `which x`, `echo $PATH` | `apt install`, or fix `PATH` |
| `Address already in use` | port taken | `ss -tlnp`, `lsof -i :PORT` | stop the other process or change the port |
| service won't start | bad config, port, permissions | `systemctl status NAME`, `journalctl -u NAME -n 50` | read the **last error line** of the journal, fix, restart |
| system is slow | CPU, memory or disk is busy | `top`, `free -h`, `uptime`, `df -h` | stop/limit the hog; add memory |
| `Connection refused` | nothing is listening there | `ss -tln`, `systemctl status` | start the service |
| `Connection timed out` | blocked by firewall/network | `ping`, `curl -v`, firewall rules | open the port / fix routing |
| `Could not resolve host` | DNS problem | `dig example.com`, `cat /etc/resolv.conf` | fix DNS or network |
| cron job does nothing | wrong paths/environment | `grep CRON /var/log/syslog`, run by hand | full paths, redirect output to a log |
| script: `bad interpreter ^M` | Windows line endings | `file script.sh` | `sed -i 's/\r$//' script.sh` |

## 5. How to ask for help (and get it)

When you ask a teammate (or a forum) for help, include:

1. **What you tried to do** (the goal).
2. **The exact command** you ran.
3. **The full error message** (copy it; don't retype it).
4. **What you already checked**, and the output of `uname -a` and `cat /etc/os-release` if relevant.

`history | tail -n 20` shows your recent commands. **Never paste passwords, keys or tokens.**

## 6. Final project: a health-check script

Combine everything: write **`health.sh`** that prints a one-screen report and warns if something is wrong.

```bash
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
```

Download it: {download}`health.sh <../code/health.sh>`. Run it:

```bash
chmod +x health.sh
./health.sh
```

```text
=== Health check: laptop @ 2026-10-15 23:40:02 ===

--- Disk (warn above 85%) ---
ok: / 77%
ok: /run 1%
ok: /boot/efi 2%

--- Memory ---
used 2.1Gi of 7.6Gi, available 5.2Gi

--- Load (1 / 5 / 15 min) vs 8 CPU cores ---
 0.15, 0.20, 0.18

--- Biggest folders in your lab ---
56K	/home/asha/linux-lab
16K	/home/asha/linux-lab/logs
12K	/home/asha/linux-lab/docs
12K	/home/asha/linux-lab/data

--- Errors in the lab log ---
3
```

(Your numbers will be different.) It uses variables, `while read`, pipes, `awk`, `du`, `df`, `free`, `uptime` and `grep`: nearly everything from the course. Schedule it with cron
and send the output to a log, and you have real monitoring.

## Common mistakes

| Mistake | Why it hurts | Instead |
|---|---|---|
| changing many things at once | you won't know what fixed it (or broke it) | **one** change, then test |
| skipping the logs | the answer was written there | read the **last** error and the lines before it |
| fixing with `chmod -R 777` | opens a security hole and hides the real problem | find the exact permission needed |
| deleting logs to "free space" blindly | you lose the evidence | find what's big first; rotate/compress logs |
| editing config files without a backup | can't go back | `cp file file.bak` first |
| restarting things "to see if it helps" | may hide the cause, causes downtime | check status and logs first |
| not writing it down | the same issue returns | keep a short log of cause and fix |

## Tryouts

Work in `~/linux-lab/playground`. Check with `bash ~/linux-lab/check.sh 11`.

**Tryout 1 · Warm-up.** What percentage of your root disk (`/`) is used? How much memory is *available*? How many CPU cores do you have (`nproc`)?

<details class="solution">
<summary>Answer</summary>

```bash
df -h /          # look at Use%
free -h          # look at the "available" column
nproc            # number of CPU cores
```

</details>

**Tryout 2 · Build.** Save a disk report (`df -h`) into `disk-report.txt`, and the **five biggest** files/folders under `~/linux-lab` (`du -ah | sort -rh | head`) into `biggest.txt`.

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab/playground
df -h > disk-report.txt
du -ah ~/linux-lab | sort -rh | head -n 5 > biggest.txt
cat biggest.txt
```

</details>

**Tryout 3 · Challenge.** *Be the detective.* In `logs/app.log`, find (a) the **time** of the first ERROR, (b) the **line just before** it, (c) how many minutes pass between the "database connection lost" error and the next "connected to database" message.

<details class="solution">
<summary>Answer</summary>

```bash
cd ~/linux-lab/logs
grep -n ERROR app.log | head -n 1            # (a) line 5: 09:07:42
grep -n -B1 ERROR app.log | head -n 2        # (b) the line before is "user asha logged in" at 09:05:30
grep -n -A1 "connection lost" app.log        # (c) lost at 09:59:59, reconnected at 10:00:02
```

(c) is **3 seconds**, so the outage was very short. Reading the logs turned "something broke" into a precise story.

</details>

```bash
bash ~/linux-lab/check.sh 11
bash ~/linux-lab/check.sh all
```

## Final exam

Ready to test the whole course? Take the **timed final exam**: **Linux Basics · Final Exam** (20 questions, 20 minutes). Find it
under *Practice → Timed assessments* in the portal, or open the **⏱ Timed assessments** link in your account menu.

## Quiz

Take **"Session 11 · Quiz"** from the portal's **Quizzes** page.

## Recap

- ✅ Troubleshoot with a **method**: describe → vital signs → logs → one guess → confirm and note.
- ✅ Vital signs: `df -h` (and `-i`), `du ... | sort -rh`, `free -h`, `uptime`, `top`, `ss -tlnp`.
- ✅ Logs: `/var/log`, `journalctl -u NAME -n 50`, `tail -f`, `grep ERROR`, context with `-B`/`-A`.
- ✅ Read the **whole** error; change **one** thing; copy before editing; never `chmod 777`.
- ✅ You built a health-check script from the tools in this course.

**🎉 Course complete!** Keep the **[Cheat sheet](../cheatsheet.md)** beside you, build small scripts for your own tasks, and take the **timed final exam**.
