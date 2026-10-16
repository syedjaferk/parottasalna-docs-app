"""Builds every diagram of the Git: Basics to Intermediate course as diagrams/<name>.html (an inline SVG <figure>).

Pages include them with

    ```{raw} html
    :file: ../diagrams/<name>.html
    ```

Edit a function, then run:  python course_content/git-basics-to-intermediate/diagrams/make_diagrams.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _dg import ALL, D, diagram

R = 16
ARROW_KINDS = ("blue", "green", "red")


def node(d, x, y, label="", kind="blue", r=R):
    """A commit: a circle with an optional short label."""
    d.circle(x, y, r, kind)
    if label:
        d.text(x, y, label, "small")


def link(d, a, b, kind="", dashed=False, r=R):
    """Arrow from a child commit to its parent (Git history points backwards)."""
    (x1, y1), (x2, y2) = a, b
    dist = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / dist, (y2 - y1) / dist
    d.arrow([(x1 + ux * (r + 1), y1 + uy * (r + 1)), (x2 - ux * (r + 3), y2 - uy * (r + 3))], kind=kind, dashed=dashed)


def tag(d, x, y, text, kind="green", below=False, r=R):
    """A branch/tag label with an arrow pointing at the commit at (x, y)."""
    w = 14 + 8.4 * len(text)
    ak = kind if kind in ARROW_KINDS else ""
    if below:
        d.box(x - w / 2, y + r + 18, w, 24, (text, "code"), kind, rx=6)
        d.arrow([(x, y + r + 18), (x, y + r + 3)], kind=ak)
    else:
        d.box(x - w / 2, y - r - 42, w, 24, (text, "code"), kind, rx=6)
        d.arrow([(x, y - r - 18), (x, y - r - 3)], kind=ak)


def row(d, y, xs, labels=None, kinds=None):
    """A straight line of commits; returns their (x, y) points and links each to the one before it."""
    pts = [(x, y) for x in xs]
    for i, p in enumerate(pts):
        lab = labels[i] if labels else ""
        node(d, p[0], p[1], lab, kinds[i] if kinds else "blue")
        if i:
            link(d, p, pts[i - 1])
    return pts


@diagram
def g00_journey():
    d = D("g00-journey", 720, 270, "The Git journey",
          "Four parts: foundations, branching and merging, teamwork and power tools, and workflows for real projects.")
    parts = [("1 Foundations", "init · add · commit\nlog · diff · undo", "blue"), ("2 Branching", "branch · switch\nmerge · conflicts", "green"),
             ("3 Teamwork", "GitHub · push · pull\nPRs · rebase · stash", "amber"), ("4 Workflows", "Git Flow · GitHub Flow\ntrunk-based · rescue", "red")]
    for i, (t, s, k) in enumerate(parts):
        x = 15 + i * 178
        y = 150 - i * 32
        d.box(x, y, 160, 100, [(t, "bold")] + [(ln, "small") for ln in s.split("\n")], k)
        if i < 3:
            d.arrow([(x + 160, y + 40), (x + 176, y + 40 - 32)], kind="blue")
    d.text(360, 25, "Beginner → confident Git user", "title")
    return d.render()


@diagram
def g01_before_after():
    d = D("g01-before-after", 720, 230, "Files with and without Git",
          "Without Git you copy files and invent names; with Git there is one file and Git remembers every version.")
    d.box(20, 20, 320, 160, [("WITHOUT GIT", "title"), ("report.docx", "code"), ("report_final.docx", "code"), ("report_final_v2.docx", "code"),
                             ("report_final_v2_REAL.docx", "code"), ("which one is the latest?", "small")], "red")
    d.box(380, 20, 320, 160, [("WITH GIT", "title"), ("report.docx", "code"), ("one file in your folder", "small"), ("git log  →  every version, who, when, why", "small"),
                              ("git restore  →  go back any time", "small")], "green")
    d.text(360, 210, "Git is a time machine for your project folder", "small")
    return d.render()


@diagram
def g01_snapshots():
    d = D("g01-snapshots", 720, 230, "A commit is a snapshot",
          "Each commit stores a snapshot of the project plus who made it, when and why, and points to the commit before it.")
    msgs = ["Add homepage", "Add contact page", "Fix typo in title"]
    ids = ["a1b2c3d", "e4f5a6b", "c7d8e9f"]
    for i in range(3):
        x = 20 + i * 245
        d.box(x, 40, 210, 90, [(f"commit {ids[i]}", "code"), (f'"{msgs[i]}"', "bold"), ("snapshot · author · date", "small")], ["blue", "green", "amber"][i])
        if i:
            d.arrow([(x, 85), (x - 33, 85)], kind="blue")
            d.text(x - 16, 68, "parent", "small")
    d.text(360, 175, "each commit points to the one before it: that chain is your history", "small")
    return d.render()


@diagram
def g02_areas():
    d = D("g02-areas", 720, 240, "The three areas of Git",
          "You edit in the working folder, git add moves changes to the staging area, git commit saves them in the repository.")
    boxes = [(20, "Working folder", "your desk", "files you edit", "blue"), (275, "Staging area", "the packing box", "what goes in the next save", "amber"),
             (530, "Repository (.git)", "the photo album", "permanent history", "green")]
    for x, t, a, b, k in boxes:
        d.box(x, 35, 170, 100, [(t, "bold"), (a, "small"), (b, "small")], k)
    d.arrow([(190, 70), (273, 70)], kind="blue", label="git add", lx=232, ly=55)
    d.arrow([(445, 70), (528, 70)], kind="green", label="git commit", lx=487, ly=55)
    d.arrow([(273, 108), (192, 108)], kind="red", label="restore", lx=232, ly=123)
    d.arrow([(528, 108), (447, 108)], kind="red", label="unstage", lx=487, ly=123)
    d.text(360, 175, "edit  →  add  →  commit : the three-step rhythm of Git", "bold")
    d.text(360, 205, "the staging area lets you choose exactly what goes into each save", "small")
    return d.render()


@diagram
def g02_lifecycle():
    d = D("g02-lifecycle", 720, 250, "Life of a file in Git",
          "A new file is untracked, git add stages it, git commit saves it, editing makes it modified, and git add stages it again.")
    d.box(20, 40, 140, 50, [("Untracked", "bold"), ("new, Git ignores it", "small")], "red")
    d.box(290, 40, 140, 50, [("Staged", "bold"), ("ready to save", "small")], "amber")
    d.box(560, 40, 140, 50, [("Committed", "bold"), ("safe in history", "small")], "green")
    d.box(290, 160, 140, 50, [("Modified", "bold"), ("changed again", "small")], "blue")
    d.arrow([(160, 65), (288, 65)], kind="blue", label="git add", lx=224, ly=48)
    d.arrow([(430, 65), (558, 65)], kind="green", label="git commit", lx=494, ly=48)
    d.arrow([(630, 90), (630, 185), (432, 185)], kind="blue", label="edit the file", lx=545, ly=202)
    d.arrow([(360, 160), (360, 92)], kind="blue", label="git add", lx=402, ly=126)
    return d.render()


@diagram
def g03_diff():
    d = D("g03-diff", 720, 270, "What git diff compares",
          "git diff compares working folder to staging, git diff --staged compares staging to the last commit, git diff HEAD compares working folder to the last commit.")
    for x, t, k in [(20, "Working folder", "blue"), (275, "Staging area", "amber"), (530, "Last commit (HEAD)", "green")]:
        d.box(x, 20, 170, 46, (t, "bold"), k)
    spans = [(105, 360, 112, "git diff", "edited, not yet staged"), (360, 615, 160, "git diff --staged", "staged, not yet committed"),
             (105, 615, 208, "git diff HEAD", "everything changed since the last commit")]
    for x1, x2, y, cmd, sub in spans:
        d.line(x1, y, x2, y)
        d.line(x1, y - 7, x1, y + 7)
        d.line(x2, y - 7, x2, y + 7)
        d.text((x1 + x2) / 2, y - 14, cmd, "code")
        d.text((x1 + x2) / 2, y + 18, sub, "small")
    for x in (105, 360, 615):
        d.line(x, 66, x, 105, "line")
    return d.render()


@diagram
def g04_reset():
    d = D("g04-reset", 720, 250, "soft, mixed and hard reset",
          "All three move the branch back; mixed also empties the staging area; hard also overwrites your files.")
    heads = ["Branch moves back", "Staging area reset", "Your files changed"]
    for i, h in enumerate(heads):
        d.box(165 + i * 175, 12, 160, 32, (h, "small"), "box")
    rows = [("--soft", "green", ["yes", "no", "no"]), ("--mixed (default)", "amber", ["yes", "yes", "no"]), ("--hard", "red", ["yes", "yes", "YES - careful"])]
    for r, (name, k, cells) in enumerate(rows):
        y = 58 + r * 52
        d.box(15, y, 140, 42, (name, "code"), k)
        for i, c in enumerate(cells):
            d.box(165 + i * 175, y, 160, 42, (c, "bold" if c != "no" else ""), k if c != "no" else "ghost")
    d.text(360, 228, "--hard is the only one that can throw away work you have not committed", "small")
    return d.render()


@diagram
def g04_revert():
    d = D("g04-revert", 720, 300, "Reset versus revert",
          "Reset moves the branch back and the later commit disappears from history; revert keeps history and adds a new commit that undoes the change.")
    d.text(10, 14, "git reset --hard HEAD~1  (rewinds, rewrites history)", "title", anchor="start")
    pts = row(d, 90, [60, 150, 240], ["C1", "C2", "C3"])
    node(d, 330, 90, "C4", "ghost")
    link(d, (330, 90), pts[-1], dashed=True)
    tag(d, 240, 90, "main", "green")
    d.text(330, 136, "C4 is gone", "small")
    d.text(480, 90, "history rewritten: risky if shared", "small", anchor="start")
    d.text(10, 175, "git revert HEAD  (adds an undo commit, history stays)", "title", anchor="start")
    pts2 = row(d, 250, [60, 150, 240, 330], ["C1", "C2", "C3", "C4"])
    node(d, 420, 250, "R", "red")
    link(d, (420, 250), pts2[-1])
    tag(d, 420, 250, "main", "green")
    d.text(470, 250, "R = \"undo C4\"", "small", anchor="start")
    d.text(470, 275, "safe on shared branches", "small", anchor="start")
    return d.render()


@diagram
def g05_branch():
    d = D("g05-branch", 720, 230, "Branches are labels on commits",
          "main and feature are just labels on commits; feature has two commits that main does not have yet.")
    main = row(d, 160, [60, 150, 240, 330], ["C1", "C2", "C3", "C4"])
    feat = [(240, 80), (330, 80), (420, 80)]
    for i, p in enumerate(feat):
        node(d, p[0], p[1], f"F{i + 1}", "green")
    link(d, feat[0], main[1])
    link(d, feat[1], feat[0])
    link(d, feat[2], feat[1])
    tag(d, 330, 160, "main", "blue", below=True)
    tag(d, 420, 80, "feature", "green")
    d.box(520, 24, 70, 24, ("HEAD", "code"), "ghost", rx=6)
    d.arrow([(518, 36), (466, 36)], kind="green")
    d.text(470, 150, "a branch costs almost nothing:", "small", anchor="start")
    d.text(470, 172, "it is a 41-character label", "small", anchor="start")
    return d.render()


@diagram
def g05_head():
    d = D("g05-head", 720, 270, "HEAD is your 'you are here' marker",
          "HEAD points at a branch, and the branch points at a commit; git switch moves HEAD to another branch.")
    for off, which, title in [(0, 0, "now (on main)"), (125, 1, "after:  git switch feature")]:
        d.text(10, off + 14, title, "title", anchor="start")
        d.box(60, off + 56, 80, 30, ("HEAD", "code"), "ghost", rx=6)
        d.box(240, off + 32, 110, 30, ("main", "code"), "blue", rx=6)
        d.box(240, off + 78, 110, 30, ("feature", "code"), "green", rx=6)
        d.arrow([(140, off + 66), (238, off + 47 if which == 0 else off + 93)], kind="blue" if which == 0 else "green")
        node(d, 500, off + 47, "C3", "blue")
        node(d, 600, off + 93, "C5", "green")
        link(d, (600, off + 93), (500, off + 47))
        d.arrow([(350, off + 47), (482, off + 47)], kind="blue")
        d.arrow([(350, off + 93), (582, off + 93)], kind="green")
    return d.render()


@diagram
def g06_ff():
    d = D("g06-ff", 720, 270, "Fast-forward merge",
          "When main has not moved, merging feature just slides the main label forward; no new commit is needed.")
    d.text(10, 14, "BEFORE", "title", anchor="start")
    row(d, 100, [60, 150, 240, 330], ["C1", "C2", "C3", "C4"])
    tag(d, 150, 100, "main", "blue")
    tag(d, 330, 100, "feature", "green")
    d.text(10, 154, "AFTER   git switch main  →  git merge feature", "title", anchor="start")
    row(d, 225, [60, 150, 240, 330], ["C1", "C2", "C3", "C4"])
    tag(d, 330, 225, "main", "blue")
    d.text(420, 225, "the label slid forward. No merge commit.", "small", anchor="start")
    return d.render()


@diagram
def g06_3way():
    d = D("g06-3way", 720, 410, "Three-way merge",
          "When both branches have new commits, Git creates a merge commit with two parents that joins them.")
    d.text(10, 14, "BEFORE", "title", anchor="start")
    m = row(d, 120, [60, 150, 240], ["C1", "C2", "C3"])
    f = [(240, 62), (330, 62)]
    node(d, f[0][0], f[0][1], "F1", "green")
    node(d, f[1][0], f[1][1], "F2", "green")
    link(d, f[0], m[1])
    link(d, f[1], f[0])
    tag(d, 240, 120, "main", "blue", below=True)
    tag(d, 330, 62, "feature", "green")
    d.text(10, 214, "AFTER   git switch main  →  git merge feature", "title", anchor="start")
    oy = 215
    m2 = row(d, oy + 120, [60, 150, 240], ["C1", "C2", "C3"])
    f2 = [(240, oy + 62), (330, oy + 62)]
    node(d, f2[0][0], f2[0][1], "F1", "green")
    node(d, f2[1][0], f2[1][1], "F2", "green")
    link(d, f2[0], m2[1])
    link(d, f2[1], f2[0])
    node(d, 420, oy + 120, "M", "amber")
    link(d, (420, oy + 120), m2[2])
    link(d, (420, oy + 120), f2[1])
    tag(d, 420, oy + 120, "main", "blue", below=True)
    d.text(480, oy + 62, "M = merge commit,", "small", anchor="start")
    d.text(480, oy + 82, "it has two parents", "small", anchor="start")
    return d.render()


@diagram
def g06_conflict():
    d = D("g06-conflict", 720, 250, "How a merge conflict happens",
          "Both branches changed the same line differently, so Git cannot choose and asks you to decide.")
    d.box(240, 10, 240, 44, [("original line 3", "small"), ("color = blue", "code")], "box")
    d.box(40, 100, 250, 44, [("main changed it", "small"), ("color = red", "code")], "blue")
    d.box(430, 100, 250, 44, [("feature changed it", "small"), ("color = green", "code")], "green")
    d.arrow([(300, 54), (190, 98)], kind="blue")
    d.arrow([(420, 54), (530, 98)], kind="green")
    d.box(220, 190, 280, 46, [("CONFLICT: Git stops and asks you", "bold")], "red")
    d.arrow([(190, 144), (290, 188)], kind="red")
    d.arrow([(530, 144), (430, 188)], kind="red")
    return d.render()


@diagram
def g07_remote():
    d = D("g07_remote".replace("_", "-"), 720, 290, "Local and remote repositories",
          "You work on your computer; push sends commits to GitHub; fetch and pull bring other people's commits back; clone copies a repo the first time.")
    d.rect(10, 78, 385, 110, "ghost", rx=12)
    d.text(24, 94, "YOUR COMPUTER", "title", anchor="start")
    d.box(25, 110, 130, 60, [("Working folder", "bold"), ("your files", "small")], "blue")
    d.box(235, 110, 140, 60, [("Local repo", "bold"), (".git history", "small")], "amber")
    d.box(535, 110, 170, 60, [("GitHub", "bold"), ("remote called origin", "small")], "green")
    d.arrow([(155, 140), (233, 140)], kind="blue", label="commit", lx=194, ly=125)
    d.arrow([(375, 125), (533, 125)], kind="green", label="git push", lx=454, ly=110)
    d.arrow([(533, 155), (377, 155)], kind="blue", label="git fetch", lx=455, ly=172)
    d.arrow([(620, 108), (620, 40), (90, 40), (90, 108)], kind="blue", label="git pull  =  fetch + merge", lx=355, ly=26)
    d.arrow([(620, 172), (620, 240), (305, 240), (305, 172)], kind="green", dashed=True, label="git clone  (first time only)", lx=462, ly=262)
    return d.render()


@diagram
def g07_fetchpull():
    d = D("g07-fetchpull", 720, 345, "Fetch versus pull",
          "git fetch downloads new commits but leaves your branch alone; git pull also moves your branch forward.")
    d.text(10, 14, "AFTER  git fetch   (downloaded, your main has not moved)", "title", anchor="start")
    row(d, 95, [60, 150, 240, 330, 420], ["C1", "C2", "C3", "C4", "C5"], ["blue", "blue", "blue", "ghost", "ghost"])
    tag(d, 240, 95, "main", "blue", below=True)
    tag(d, 420, 95, "origin/main", "green")
    d.text(500, 95, "C4, C5 are on GitHub only", "small", anchor="start")
    d.text(10, 185, "AFTER  git pull   (fetch + merge: main caught up)", "title", anchor="start")
    row(d, 275, [60, 150, 240, 330, 420], ["C1", "C2", "C3", "C4", "C5"])
    tag(d, 420, 275, "main", "blue")
    tag(d, 420, 275, "origin/main", "green", below=True)
    return d.render()


@diagram
def g08_fork_pr():
    d = D("g08-fork-pr", 720, 290, "Fork and pull request",
          "Fork copies the project to your GitHub account, you clone and push to your fork, then open a pull request back to the official repo.")
    d.box(250, 12, 220, 52, [("Official repo", "bold"), ("upstream (the owner's)", "small")], "blue")
    d.box(470, 150, 220, 52, [("Your fork", "bold"), ("origin (on GitHub)", "small")], "green")
    d.box(30, 150, 220, 52, [("Your computer", "bold"), ("local clone", "small")], "amber")
    d.arrow([(400, 64), (520, 148)], kind="blue", label="1 fork", lx=430, ly=110)
    d.arrow([(468, 168), (252, 168)], kind="green", label="2 clone", lx=360, ly=153)
    d.arrow([(252, 188), (468, 188)], kind="green", label="3 push your branch", lx=360, ly=205)
    d.arrow([(640, 148), (472, 40)], kind="red", label="4 open a pull request", lx=618, ly=88)
    d.arrow([(290, 64), (150, 148)], kind="blue", dashed=True, label="5 pull upstream", lx=148, ly=100)
    d.text(360, 250, "dashed: keep your copy up to date with the owner's changes", "small")
    return d.render()


@diagram
def g08_pr_flow():
    d = D("g08-pr-flow", 720, 170, "Life of a pull request",
          "Branch, commit, push, open the pull request, get a review, then merge.")
    steps = [("1 Branch", "git switch -c", "blue"), ("2 Commit", "git commit", "blue"), ("3 Push", "git push -u", "amber"),
             ("4 Open PR", "on GitHub", "amber"), ("5 Review", "discuss, fix", "green"), ("6 Merge", "delete branch", "green")]
    for i, (t, s, k) in enumerate(steps):
        x = 10 + i * 120
        d.box(x, 40, 100, 70, [(t, "bold"), (s, "small")], k)
        if i < 5:
            d.arrow([(x + 100, 75), (x + 118, 75)], kind="blue")
    d.arrow([(580, 110), (580, 140), (130, 140), (130, 112)], kind="red", dashed=True, label="changes requested: commit and push again", lx=355, ly=156)
    return d.render()


@diagram
def g09_rebase():
    d = D("g09-rebase", 720, 405, "Merge versus rebase",
          "Rebase lifts your branch's commits and replays them on top of the latest main, giving a straight history.")
    d.text(10, 14, "BEFORE", "title", anchor="start")
    m = row(d, 125, [60, 150, 240], ["1", "2", "3"])
    f = [(240, 72), (320, 72)]
    node(d, *f[0], "A", "green")
    node(d, *f[1], "B", "green")
    link(d, f[0], m[1])
    link(d, f[1], f[0])
    tag(d, 240, 125, "main", "blue", below=True)
    tag(d, 320, 72, "feature", "green")
    d.text(10, 215, "AFTER  git switch feature  →  git rebase main", "title", anchor="start")
    oy = 310
    r = row(d, oy, [60, 150, 240, 330, 420], ["1", "2", "3", "A'", "B'"], ["blue", "blue", "blue", "green", "green"])
    node(d, 330, oy - 60, "A", "ghost")
    node(d, 420, oy - 60, "B", "ghost")
    link(d, (330, oy - 60), r[1], dashed=True)
    link(d, (420, oy - 60), (330, oy - 60), dashed=True)
    tag(d, 240, oy, "main", "blue", below=True)
    tag(d, 420, oy, "feature", "green", below=True)
    d.text(500, oy - 60, "old A, B are abandoned", "small", anchor="start")
    d.text(500, oy, "A', B' = copies on the new base", "small", anchor="start")
    return d.render()


@diagram
def g09_cherry():
    d = D("g09-cherry", 720, 230, "Cherry-pick",
          "Cherry-pick copies one chosen commit from another branch onto the branch you are on.")
    m = row(d, 160, [60, 150, 240], ["1", "2", "3"])
    f = [(240, 60), (330, 60), (420, 60)]
    for p, lab in zip(f, "ABC"):
        node(d, p[0], p[1], lab, "green")
    link(d, f[0], m[1])
    link(d, f[1], f[0])
    link(d, f[2], f[1])
    node(d, 330, 160, "B'", "amber")
    link(d, (330, 160), m[2])
    d.arrow([(330, 78), (330, 140)], kind="red", dashed=True, label="copy", lx=355, ly=108)
    tag(d, 330, 160, "main", "blue", below=True)
    tag(d, 420, 60, "feature", "green")
    d.text(480, 160, "git cherry-pick <B's id>", "code", anchor="start")
    return d.render()


@diagram
def g09_stash():
    d = D("g09-stash", 720, 200, "Stash: a shelf for half-done work",
          "git stash puts your uncommitted changes on a shelf and cleans the folder; git stash pop brings them back.")
    d.box(15, 40, 170, 80, [("Half-done work", "bold"), ("uncommitted changes", "small")], "amber")
    d.box(275, 40, 170, 80, [("The stash shelf", "bold"), ("folder is clean now", "small")], "blue")
    d.box(535, 40, 170, 80, [("Work is back", "bold"), ("carry on", "small")], "green")
    d.arrow([(185, 80), (273, 80)], kind="blue", label="git stash", lx=229, ly=64)
    d.arrow([(445, 80), (533, 80)], kind="green", label="git stash pop", lx=489, ly=64)
    d.text(360, 160, "in between: switch branch · fix the urgent bug · switch back", "small")
    return d.render()


@diagram
def g10_centralized():
    d = D("g10-centralized", 720, 250, "Centralized workflow",
          "Everyone pushes straight to a single main branch; the history is one straight line.")
    for i, n in enumerate(["Asha", "Ravi", "Meena"]):
        d.box(20, 30 + i * 70, 120, 44, (n, "bold"), "box")
        d.arrow([(140, 52 + i * 70), (310, 120 + (i - 1) * 10)], kind="blue", label="push" if i == 1 else None, lx=225, ly=100)
    d.box(310, 80, 150, 80, [("Central repo", "bold"), ("only branch: main", "small")], "blue")
    d.arrow([(460, 120), (508, 120)], kind="blue")
    pts = [(545 + i * 50, 120) for i in range(4)]
    for i, p in enumerate(pts):
        node(d, p[0], p[1], "", "blue", r=12)
        if i:
            link(d, p, pts[i - 1], r=12)
    d.text(620, 165, "one straight line", "small")
    d.text(360, 225, "rule of thumb: git pull before you git push", "small")
    return d.render()


@diagram
def g10_feature():
    d = D("g10-feature", 720, 280, "Feature branch workflow",
          "Each piece of work lives on its own branch and is merged into main after review.")
    ys = 205
    m = [(50, ys), (150, ys), (330, ys), (520, ys), (660, ys)]
    for i, p in enumerate(m):
        node(d, p[0], p[1], "", "blue", r=13)
        if i:
            link(d, p, m[i - 1], r=13)
    a = [(210, 125), (255, 125), (295, 125)]
    for i, p in enumerate(a):
        node(d, p[0], p[1], "", "green", r=13)
    link(d, a[0], m[1], r=13)
    link(d, a[1], a[0], r=13)
    link(d, a[2], a[1], r=13)
    link(d, m[2], a[2], r=13)
    b = [(385, 85), (430, 85), (475, 85)]
    for p in b:
        node(d, p[0], p[1], "", "amber", r=13)
    link(d, b[0], m[2], r=13)
    link(d, b[1], b[0], r=13)
    link(d, b[2], b[1], r=13)
    link(d, m[3], b[2], r=13)
    tag(d, 255, 125, "feature/login", "green", r=13)
    tag(d, 430, 85, "feature/search", "amber", r=13)
    tag(d, 660, ys, "main", "blue", below=True, r=13)
    d.text(360, 268, "every change lives on its own branch until a teammate has reviewed it", "small")
    return d.render()


@diagram
def g10_gitflow():
    d = D("g10-gitflow", 720, 300, "Git Flow",
          "Five kinds of branches: main for releases, develop for integration, feature, release and hotfix branches that come and go.")
    lanes = {"main": 40, "hotfix": 95, "release": 150, "develop": 205, "feature": 260}
    kinds = {"main": "red", "hotfix": "amber", "release": "purple", "develop": "blue", "feature": "green"}
    for name, y in lanes.items():
        d.line(110, y, 610, y)
        d.text(622, y, name if name in ("main", "develop") else name + "/*", "code", anchor="start")
    r = 9
    P = {}

    def n(key, x, lane):
        P[key] = (x, lanes[lane])
        node(d, x, lanes[lane], "", kinds[lane], r=r)

    for key, x in [("D1", 150), ("D2", 210), ("D3", 280), ("D4", 400), ("D5", 520), ("D6", 580)]:
        n(key, x, "develop")
    for key, x in [("F1", 190), ("F2", 240)]:
        n(key, x, "feature")
    for key, x in [("R1", 310), ("R2", 350)]:
        n(key, x, "release")
    n("M1", 150, "main")
    n("M2", 400, "main")
    n("M3", 520, "main")
    n("H1", 460, "hotfix")
    pairs = [("D2", "D1"), ("D3", "D2"), ("D4", "D3"), ("D5", "D4"), ("D6", "D5"), ("F1", "D1"), ("F2", "F1"), ("D3", "F2"), ("R1", "D3"), ("R2", "R1"),
             ("M2", "M1"), ("M2", "R2"), ("D4", "R2"), ("H1", "M2"), ("M3", "M2"), ("M3", "H1"), ("D5", "H1")]
    for a, b in pairs:
        link(d, P[a], P[b], r=r)
    d.text(400, 20, "v1.0", "code")
    d.text(520, 20, "v1.0.1", "code")
    return d.render()


@diagram
def g10_githubflow():
    d = D("g10-githubflow", 720, 230, "GitHub Flow",
          "A simple loop: branch from main, commit, open a pull request, review, merge, deploy; main is always ready to ship.")
    d.text(360, 20, "main is always ready to ship", "title")
    steps = [("1 Branch", "off main", "blue"), ("2 Commit", "small steps", "blue"), ("3 Open PR", "pull request", "amber"),
             ("4 Review", "discuss + test", "amber"), ("5 Merge", "into main", "green"), ("6 Deploy", "to users", "green")]
    for i, (t, s, k) in enumerate(steps):
        x = 10 + i * 120
        d.box(x, 45, 100, 70, [(t, "bold"), (s, "small")], k)
        if i < 5:
            d.arrow([(x + 100, 80), (x + 118, 80)], kind="blue")
    d.arrow([(610, 115), (610, 160), (60, 160), (60, 117)], kind="blue", dashed=True, label="repeat for the next change", lx=335, ly=180)
    return d.render()


@diagram
def g10_trunk():
    d = D("g10-trunk", 720, 260, "Trunk-based development",
          "Everyone commits to one trunk in tiny steps; any branch lives for hours, and unfinished work hides behind a feature flag.")
    t = [(40 + 40 * i, 160) for i in range(15)]
    r = 10
    for i, p in enumerate(t):
        node(d, p[0], p[1], "", "blue", r=r)
        if i:
            link(d, p, t[i - 1], r=r)
    for i in (2, 6, 10):
        b = (t[i + 1][0], 100)
        node(d, b[0], b[1], "", "green", r=r)
        link(d, b, t[i], r=r)
        link(d, t[i + 2], b, r=r)
    tag(d, t[-1][0], 160, "trunk (main)", "blue", below=True, r=r)
    d.text(130, 60, "short branch: lives hours, not weeks", "small", anchor="start")
    d.text(360, 25, "many small commits · always integrated · always releasable", "title")
    d.box(110, 212, 500, 36, [("unfinished feature? hide it:  if (flag.login_v2) { ... }", "code")], "amber")
    return d.render()


@diagram
def g10_choose():
    d = D("g10-choose", 720, 330, "Choosing a workflow",
          "Match your team and release style to a workflow: centralized, feature branch or GitHub Flow, Git Flow, forking, or trunk-based.")
    rows = [("Just you, or a tiny team that trusts each other?", "Centralized", "blue"),
            ("Small team, review by pull request, deploy often?", "Feature branch / GitHub Flow", "green"),
            ("Numbered versions (v1.x, v2.x) supported in parallel?", "Git Flow", "purple"),
            ("Strangers contribute to your project?", "Forking workflow", "amber"),
            ("Strong tests + CI, shipping many times a day?", "Trunk-based development", "red")]
    for i, (q, a, k) in enumerate(rows):
        y = 12 + i * 62
        d.box(15, y, 400, 46, (q, ""), "box")
        d.arrow([(415, y + 23), (455, y + 23)], kind="blue")
        d.box(457, y, 248, 46, (a, "bold"), k)
    return d.render()


if __name__ == "__main__":
    for fn in ALL:
        fn()
    print(f"{len(ALL)} diagrams written")
