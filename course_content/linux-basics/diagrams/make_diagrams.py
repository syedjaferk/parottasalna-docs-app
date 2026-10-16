"""Builds every diagram of the Linux Basics course as diagrams/<name>.html (an inline SVG <figure>).

Pages include them with

    ```{raw} html
    :file: ../diagrams/<name>.html
    ```

Edit a function, then run:  python course_content/linux-basics/diagrams/make_diagrams.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _dg import ALL, D, diagram


@diagram
def l00_journey():
    d = D("l00-journey", 720, 270, "The Linux Basics journey",
          "Four parts: getting around, text and finding things, running a system, and automating and fixing.")
    parts = [("1 Getting around", "terminal · files\nediting", "blue"), ("2 Text & search", "pipes · grep\nfind", "green"),
             ("3 Running a system", "permissions · processes\npackages · network", "amber"), ("4 Automate & fix", "scripts · logs\ntroubleshooting", "red")]
    for i, (t, s, k) in enumerate(parts):
        x = 15 + i * 178
        y = 150 - i * 32
        d.box(x, y, 160, 100 + i * 10 - 0, [(t, "bold")] + [(ln, "small") for ln in s.split("\n")], k)
        if i < 3:
            d.arrow([(x + 160, y + 40), (x + 176, y + 40 - 32)], kind="blue")
    d.text(360, 25, "Beginner → confident Linux user", "title")
    return d.render()


@diagram
def l00_options():
    d = D("l00-options", 720, 200, "Four ways to get a Linux terminal",
          "WSL on Windows, the built-in terminal on Linux and macOS, a virtual machine, or Docker.")
    items = [("Windows", "WSL: wsl --install", "blue"), ("Linux / macOS", "open Terminal", "green"), ("Any computer", "VirtualBox + Ubuntu", "amber"), ("Docker", "docker run -it ubuntu", "ghost")]
    for i, (t, s, k) in enumerate(items):
        d.box(15 + i * 178, 40, 160, 100, [(t, "bold"), (s, "small")], k)
    d.text(360, 175, "All give you the same bash terminal and the same commands", "small")
    return d.render()


@diagram
def l01_layers():
    d = D("l01-layers", 720, 250, "Terminal, shell and the system",
          "You type in the terminal; the shell understands the command; the kernel talks to the hardware.")
    layers = [("You", "types: ls -l", "ghost"), ("Terminal", "the window", "blue"), ("Shell (bash)", "understands commands", "green"), ("Kernel + programs", "do the work", "amber"), ("Hardware", "disk · CPU · memory", "box")]
    for i, (t, s, k) in enumerate(layers):
        y = 12 + i * 46
        d.box(150, y, 420, 38, [(t + "  ·  " + s, "")], k)
        if i < 4:
            d.arrow([(360, y + 38), (360, y + 46)], kind="blue")
    return d.render()


@diagram
def l01_anatomy():
    d = D("l01-anatomy", 720, 190, "Anatomy of a command",
          "A command is the program name, then options that change how it works, then arguments that say what to work on.")
    d.box(60, 50, 120, 56, ("ls", "bold"), "blue"); d.box(220, 50, 120, 56, ("-l", "bold"), "amber"); d.box(380, 50, 200, 56, ("/home", "bold"), "green")
    d.text(120, 30, "COMMAND", "title"); d.text(280, 30, "OPTION", "title"); d.text(480, 30, "ARGUMENT", "title")
    d.text(120, 135, "what to do", "small"); d.text(280, 135, "how to do it", "small"); d.text(480, 135, "what to do it to", "small")
    d.text(360, 168, "spaces separate the parts · everything is case-sensitive", "small")
    return d.render()


@diagram
def l02_tree():
    d = D("l02-tree", 720, 300, "The Linux file tree",
          "One tree starting at / (root). Your files live under /home; settings under /etc; logs under /var/log.")
    d.box(310, 10, 100, 36, ("/", "bold"), "blue")
    tops = [("/home", "your files"), ("/etc", "settings"), ("/var", "logs, data"), ("/usr", "programs"), ("/tmp", "temporary"), ("/dev", "devices")]
    xs = [20, 135, 250, 365, 480, 595]
    for (n, s), x in zip(tops, xs):
        d.box(x, 90, 105, 50, [(n, "code"), (s, "small")], "box")
        d.arrow([(360, 46), (x + 52, 88)], kind="blue", head=False)
    d.box(20, 190, 105, 36, ("asha", "code"), "green"); d.arrow([(72, 140), (72, 188)], kind="blue", head=False)
    d.box(20, 245, 105, 40, ("linux-lab", "code"), "amber"); d.arrow([(72, 226), (72, 243)], kind="blue", head=False)
    d.box(250, 190, 105, 36, ("/var/log", "code"), "ghost"); d.arrow([(302, 140), (302, 188)], kind="blue", head=False)
    d.text(480, 215, "no C: or D: drives: everything is in one tree", "small")
    return d.render()


@diagram
def l02_paths():
    d = D("l02-paths", 720, 250, "Absolute and relative paths",
          "An absolute path starts at / and works from anywhere. A relative path starts from where you are now.")
    d.box(20, 20, 330, 90, [("ABSOLUTE", "title"), ("/home/asha/linux-lab/data/fruits.txt", "code"), ("works from anywhere", "small")], "blue")
    d.box(370, 20, 330, 90, [("RELATIVE (from ~/linux-lab)", "title"), ("data/fruits.txt", "code"), ("depends on where you are", "small")], "green")
    d.text(360, 140, "Shortcuts", "title")
    for i, (k, v) in enumerate([(".", "here"), ("..", "parent folder"), ("~", "home"), ("-", "previous folder"), ("/", "root")]):
        d.box(20 + i * 140, 160, 125, 60, [(k, "code"), (v, "small")], "amber")
    return d.render()


@diagram
def l03_copy_move():
    d = D("l03-copy-move", 720, 250, "cp, mv and rm",
          "cp leaves the original and makes a copy; mv moves or renames (the original disappears); rm deletes for good.")
    for i, (t, s, k) in enumerate([("cp a.txt b.txt", "copy", "blue"), ("mv a.txt b.txt", "move / rename", "green"), ("rm a.txt", "delete (no undo)", "red")]):
        x = 20 + i * 235
        d.text(x + 105, 18, t, "code")
        d.box(x, 30, 100, 40, ("a.txt", "code"), "ghost" if i == 1 else ("ghost" if i == 2 else "box"))
        d.arrow([(x + 100, 50), (x + 130, 50)], kind=["blue", "green", "red"][i])
        if i < 2:
            d.box(x + 132, 30, 80, 40, ("b.txt", "code"), k)
        else:
            d.box(x + 132, 30, 80, 40, ("(gone)", "small"), "ghost")
        d.text(x + 105, 100, "before: a.txt", "small")
        after = ["after: a.txt AND b.txt", "after: only b.txt", "after: nothing"][i]
        d.box(x, 120, 210, 40, (after, "bold"), k)
        d.text(x + 105, 190, s, "small")
    d.text(360, 230, "cp -r and rm -r work on whole folders (r = recursive)", "small")
    return d.render()


@diagram
def l04_viewers():
    d = D("l04-viewers", 720, 230, "Choosing a file viewer",
          "cat shows everything, less shows page by page, head the first lines, tail the last lines (tail -f follows).")
    items = [("cat", "whole file", "short files"), ("less", "page by page", "long files (q quits)"), ("head", "first lines", "peek at the start"), ("tail", "last lines", "-f follows a live log")]
    for i, (n, a, b) in enumerate(items):
        d.box(15 + i * 178, 30, 160, 110, [(n, "code"), (a, "bold"), (b, "small")], ["blue", "green", "amber", "amber"][i])
    d.text(360, 180, "Count with wc -l · identify with file · edit with nano", "small")
    return d.render()


@diagram
def l04_redirect():
    d = D("l04-redirect", 720, 220, "Redirection",
          "> overwrites the file, >> appends to it, < feeds a file into a command.")
    d.box(20, 40, 150, 50, ("command", "code"), "blue")
    d.arrow([(170, 55), (300, 55)], kind="red", label=">  overwrite", lx=235, ly=40)
    d.arrow([(170, 75), (300, 75)], kind="green", label=">>  append", lx=235, ly=95)
    d.box(300, 40, 150, 50, ("file.txt", "code"), "box")
    d.box(20, 140, 150, 50, ("command", "code"), "blue")
    d.arrow([(300, 165), (172, 165)], kind="blue", label="<  input", lx=236, ly=150)
    d.box(300, 140, 150, 50, ("file.txt", "code"), "box")
    d.text(580, 65, "> destroys old content!", "small"); d.text(580, 165, "reads the file as input", "small")
    return d.render()


@diagram
def l05_pipe():
    d = D("l05-pipe", 720, 200, "The pipe",
          "The pipe connects the output of one command to the input of the next, like an assembly line.")
    cmds = [("cat access.log", "read"), ("grep ' 404 '", "filter"), ("sort | uniq -c", "count"), ("head -n 3", "top 3")]
    for i, (c, s) in enumerate(cmds):
        x = 15 + i * 178
        d.box(x, 60, 130, 56, [(c, "code"), (s, "small")], ["blue", "green", "amber", "ghost"][i])
        if i < 3:
            d.arrow([(x + 130, 88), (x + 176, 88)], kind="blue", label="|", lx=x + 153, ly=74)
    d.text(360, 160, "small tools, one job each, chained together", "small")
    return d.render()


@diagram
def l05_streams():
    d = D("l05-streams", 720, 230, "stdin, stdout and stderr",
          "Every command has an input stream (0), a normal output stream (1) and an error stream (2).")
    d.box(280, 60, 160, 90, [("command", "code")], "amber")
    d.arrow([(60, 95), (278, 95)], kind="blue", label="0  stdin  (keyboard)", lx=170, ly=80)
    d.arrow([(442, 80), (660, 80)], kind="green", label="1  stdout  (screen)", lx=550, ly=64)
    d.arrow([(442, 125), (660, 125)], kind="red", label="2  stderr  (screen)", lx=550, ly=145)
    d.text(550, 185, "> file  captures 1   ·   2> file  captures 2   ·   &> both", "small")
    return d.render()


@diagram
def l06_find_grep():
    d = D("l06-find-grep", 720, 220, "find vs grep",
          "find searches by what a file is called or looks like; grep searches inside files for text.")
    d.box(20, 30, 330, 120, [("find", "code"), ("by NAME · TYPE · SIZE · AGE", "bold"), ("find . -name '*.log' -mtime -7", "small")], "blue")
    d.box(370, 30, 330, 120, [("grep -r", "code"), ("by CONTENT", "bold"), ("grep -rl 'ERROR' .", "small")], "green")
    d.text(360, 185, "Combine: find . -name '*.log' | xargs grep ERROR", "code")
    return d.render()


@diagram
def l07_owner_group_others():
    d = D("l07-owner-group-others", 720, 230, "Owner, group, others",
          "Every file has an owner, a group, and everyone else. Each of the three has its own read, write and execute rules.")
    for i, (t, s, k) in enumerate([("Owner (u)", "the user who owns it", "green"), ("Group (g)", "users in its group", "amber"), ("Others (o)", "everybody else", "ghost")]):
        d.box(20 + i * 235, 30, 210, 100, [(t, "bold"), (s, "small"), ("r  w  x", "code")], k)
    d.box(20, 160, 680, 44, [("root (the administrator) can do anything, so be careful with sudo", "small")], "red")
    return d.render()


@diagram
def l07_permissions():
    d = D("l07-permissions", 720, 250, "Reading -rwxr-xr--",
          "The first character is the type, then three triplets for owner, group and others.")
    chars = ["-", "r", "w", "x", "r", "-", "x", "r", "-", "-"]
    for i, c in enumerate(chars):
        x = 40 + i * 62
        k = "ghost" if i == 0 else ["green", "amber", "blue"][(i - 1) // 3]
        d.box(x, 40, 54, 54, (c, "code"), k)
    d.text(67, 20, "type", "small"); d.text(40 + 62 * 2.5, 20, "OWNER", "title"); d.text(40 + 62 * 5.5, 20, "GROUP", "title"); d.text(40 + 62 * 8.5, 20, "OTHERS", "title")
    d.text(67, 125, "- file", "small"); d.text(40 + 62 * 2.5, 125, "rwx = read, write, run", "small"); d.text(40 + 62 * 5.5, 125, "r-x = read, run", "small"); d.text(40 + 62 * 8.5, 125, "r-- = read only", "small")
    d.box(60, 160, 600, 56, [("file: r = see content · w = change · x = run      directory: r = list · w = add/delete · x = enter", "small")], "box")
    return d.render()


@diagram
def l07_octal():
    d = D("l07-octal", 720, 230, "Permission numbers",
          "r is 4, w is 2, x is 1. Add them per person: 7 is rwx, 6 is rw-, 5 is r-x, 4 is r--.")
    d.box(20, 20, 200, 44, [("r = 4   w = 2   x = 1", "code")], "ghost")
    for i, (n, e, k) in enumerate([("644", "rw- r-- r--", "blue"), ("600", "rw- --- ---", "red"), ("755", "rwx r-x r-x", "green"), ("700", "rwx --- ---", "amber")]):
        x = 20 + i * 175
        d.box(x, 90, 155, 80, [(n, "bold"), (e, "code")], k)
    d.text(107, 195, "normal file", "small"); d.text(282, 195, "private file", "small"); d.text(457, 195, "program / folder", "small"); d.text(632, 195, "private folder", "small")
    return d.render()


@diagram
def l08_processes():
    d = D("l08-processes", 720, 240, "Processes and PIDs",
          "Every running program is a process with a number (PID). A parent starts children; you can list, pause and stop them.")
    d.box(280, 15, 160, 44, [("init / systemd", "code"), ("PID 1", "small")], "blue")
    for i, (n, p) in enumerate([("bash", 2410), ("sshd", 912), ("nginx", 1310)]):
        x = 60 + i * 240
        d.box(x, 100, 140, 44, [(n, "code"), (f"PID {p}", "small")], "green")
        d.arrow([(360, 59), (x + 70, 98)], kind="blue", head=False)
    d.box(60, 185, 140, 40, [("ls", "code"), ("child of bash", "small")], "amber"); d.arrow([(130, 144), (130, 183)], kind="blue", head=False)
    d.text(480, 190, "ps aux · top · kill PID", "code")
    return d.render()


@diagram
def l08_signals():
    d = D("l08-signals", 720, 220, "Signals",
          "kill sends a signal: TERM asks politely, KILL forces, STOP pauses and CONT resumes.")
    for i, (n, s, k) in enumerate([("kill PID", "TERM (15): please stop", "green"), ("kill -9 PID", "KILL (9): stop NOW", "red"), ("Ctrl + C", "INT: interrupt", "amber"), ("Ctrl + Z", "STOP: pause", "blue")]):
        d.box(15 + i * 178, 40, 160, 100, [(n, "code"), (s, "small")], k)
    d.text(360, 180, "Try the polite one first. Use -9 only as a last resort.", "small")
    return d.render()


@diagram
def l08_cron():
    d = D("l08-cron", 720, 200, "A cron schedule line",
          "Five time fields (minute, hour, day of month, month, day of week) then the command.")
    fields = [("30", "minute"), ("2", "hour"), ("*", "day of month"), ("*", "month"), ("*", "day of week")]
    for i, (v, n) in enumerate(fields):
        d.box(20 + i * 110, 40, 100, 50, (v, "code"), "blue")
        d.text(70 + i * 110, 110, n, "small")
    d.box(580, 40, 120, 50, ("command", "code"), "green")
    d.text(360, 160, "30 2 * * *  → every day at 02:30", "bold")
    return d.render()


@diagram
def l09_package_manager():
    d = D("l09-package-manager", 720, 220, "How a package manager works",
          "You ask for a package; the manager fetches it from a trusted repository, checks it and installs it with its dependencies.")
    d.box(20, 70, 130, 60, [("You", "bold"), ("apt install tree", "small")], "blue")
    d.box(270, 70, 150, 60, [("Package manager", "bold"), ("apt / dnf", "small")], "amber")
    d.box(540, 70, 160, 60, [("Repository", "bold"), ("trusted, signed", "small")], "green")
    d.arrow([(150, 95), (268, 95)], kind="blue"); d.arrow([(420, 85), (538, 85)], kind="blue", label="download", lx=479, ly=70); d.arrow([(538, 115), (422, 115)], kind="green")
    d.text(360, 175, "installs the package and everything it depends on · updates and removes cleanly", "small")
    return d.render()


@diagram
def l09_tar():
    d = D("l09-tar", 720, 200, "tar: bundle and compress",
          "tar -czf creates a compressed archive; tar -tzf lists it; tar -xzf extracts it.")
    d.box(20, 50, 160, 70, [("folder", "bold"), ("docs/  data/", "code")], "blue")
    d.arrow([(180, 85), (270, 85)], kind="green", label="tar -czf", lx=225, ly=70)
    d.box(270, 50, 180, 70, [("archive.tar.gz", "code"), ("one small file", "small")], "amber")
    d.arrow([(450, 85), (540, 85)], kind="green", label="tar -xzf", lx=495, ly=70)
    d.box(540, 50, 160, 70, [("folder again", "bold"), ("docs/  data/", "code")], "blue")
    d.text(360, 160, "c = create · x = extract · t = test/list · z = gzip · f = file name", "small")
    return d.render()


@diagram
def l10_script_flow():
    d = D("l10-script-flow", 720, 220, "From idea to script",
          "Type the commands in a file, add the shebang line, make it executable, then run it.")
    steps = [("1 Write", "nano script.sh", "blue"), ("2 Shebang", "first line", "amber"), ("3 chmod +x", "make executable", "green"), ("4 Run", "./script.sh", "ghost")]
    for i, (t, s, k) in enumerate(steps):
        x = 15 + i * 178
        d.box(x, 60, 160, 70, [(t, "bold"), (s, "code")], k)
        if i < 3:
            d.arrow([(x + 160, 95), (x + 176, 95)], kind="blue")
    d.text(360, 175, "Later: schedule it with cron", "small")
    return d.render()


@diagram
def l10_exit_codes():
    d = D("l10-exit-codes", 720, 230, "if and exit codes",
          "Every command returns an exit code: 0 means success, anything else means failure. if uses it to decide.")
    d.box(20, 80, 150, 60, [("run a command", "bold")], "blue")
    d.box(240, 80, 150, 60, [("exit code?", "bold"), ("$?", "code")], "amber")
    d.arrow([(170, 110), (238, 110)], kind="blue")
    d.box(480, 25, 220, 56, [("0 → success", "bold"), ("then-branch runs", "small")], "green")
    d.box(480, 140, 220, 56, [("not 0 → failure", "bold"), ("else-branch / exit 1", "small")], "red")
    d.arrow([(390, 95), (478, 55)], kind="green"); d.arrow([(390, 125), (478, 168)], kind="red")
    return d.render()


@diagram
def l11_method():
    d = D("l11-method", 720, 230, "A calm troubleshooting method",
          "Describe the problem, check the vital signs, read the logs, test one idea, then confirm and write it down.")
    steps = [("1 Describe", "what, since when?", "ghost"), ("2 Vital signs", "df · free · top", "blue"), ("3 Logs", "journalctl · tail", "green"), ("4 One change", "test one idea", "amber"), ("5 Confirm", "note the cause", "ghost")]
    for i, (t, s, k) in enumerate(steps):
        x = 10 + i * 142
        d.box(x, 60, 128, 70, [(t, "bold"), (s, "small")], k)
        if i < 4:
            d.arrow([(x + 128, 95), (x + 140, 95)], kind="blue")
    d.text(360, 175, "read the whole error · change one thing at a time · copy before editing", "small")
    return d.render()


if __name__ == "__main__":
    for fn in ALL:
        fn()
    print(f"{len(ALL)} diagrams written")
