"""Diagrams for the Git & Version Control course. Run:  python course_content/git/diagrams/make_diagrams.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "docs"))
from diagram_kit import D  # noqa: E402


def new(name, w, h, title, caption):
    return D(name, w, h, title, caption, HERE)


def copies_vs_history():
    d = new("copies-vs-history", 760, 250, "File copies versus a history",
            "Copying files gives you report_final_v2_REALLY_final.txt. A version control system keeps one file and a list of snapshots with who, when and why.")
    d.box(20, 20, 330, 36, ("By hand", "bold"), "red")
    for i, t in enumerate(["report.txt", "report_final.txt", "report_final_v2.txt", "report_final_v2_REALLY_final.txt"]):
        d.box(20, 66 + i * 38, 330, 32, (t, "code"), "box", rx=6)
    d.box(410, 20, 330, 36, ("With Git", "bold"), "green")
    for i, (h, m) in enumerate([("460c381", "Shorten summary"), ("b26a7ba", "Add summary"), ("f4109a5", "First draft")]):
        y = 66 + i * 50
        d.circle(440, y + 16, 14, "green")
        d.text(440, y + 16, str(3 - i), "small")
        d.text(470, y + 16, f"{h}  {m}", "code", anchor="start")
        if i:
            d.arrow([(440, y + 2), (440, y - 20)], kind="green")
    d.text(575, 225, "one file, every version, who and why", "small")
    return d.render()


def generations():
    d = new("vcs-generations", 760, 230, "Three generations of version control",
            "Local tools (RCS) kept history on one computer. Central servers (CVS, Subversion) shared it. Distributed tools (Git) give everyone the full history.")
    cols = [("Local", "RCS", "history on one computer", "amber"), ("Centralized", "CVS · Subversion", "one server, everyone connects", "blue"), ("Distributed", "Git · Mercurial", "everyone has the full history", "green")]
    for i, (a, b, c, k) in enumerate(cols):
        x = 20 + i * 245
        d.box(x, 30, 220, 130, [(a, "bold"), (b, "code"), (c, "small")], k)
        if i:
            d.arrow([(x - 22, 95), (x - 2, 95)], kind="blue")
    d.text(380, 195, "each step fixed a weakness of the one before", "small")
    return d.render()


def config_levels():
    d = new("config-levels", 760, 270, "Git settings: three levels",
            "System settings apply to every user, global settings to you, and local settings to one repository. The most specific level wins.")
    rows = [("system", "/etc/gitconfig", "everyone on this computer", "ghost"), ("global", "~/.gitconfig", "you, in every repository", "blue"),
            ("local", ".git/config", "this repository only", "green")]
    for i, (a, b, c, k) in enumerate(rows):
        y = 20 + i * 66
        w = 700 - i * 100
        d.box(30 + i * 50, y, w - 0, 54, [(f"{a}   {b}", "code"), (c, "small")], k)
    d.arrow([(380, 215), (380, 200)], kind="green")
    d.text(380, 235, "more specific wins:  local  >  global  >  system", "small")
    return d.render()


def three_areas():
    d = new("three-areas", 760, 250, "Working folder, staging area, repository",
            "You edit files in the working folder, choose what goes into the next snapshot with git add, and git commit stores it in the repository.")
    areas = [("Working folder", "files you edit", "box"), ("Staging area", "the next snapshot, being prepared", "amber"), ("Repository", "saved history (.git)", "green")]
    for i, (a, b, k) in enumerate(areas):
        x = 20 + i * 250
        d.box(x, 40, 215, 100, [(a, "bold"), (b, "small")], k)
    d.arrow([(237, 90), (268, 90)], kind="blue", label="git add", lx=252, ly=70)
    d.arrow([(487, 90), (518, 90)], kind="green", label="git commit", lx=502, ly=70)
    d.arrow([(268, 120), (237, 120)], kind="red", dashed=True, label="git restore --staged", lx=252, ly=165)
    d.text(380, 215, "git status shows the difference between each pair of areas", "small")
    return d.render()


def concept_map():
    d = new("git-concepts", 760, 260, "Git terms on one page",
            "Your computer has a repository with commits and branches. A remote repository is a copy on a server; clone, push and pull move commits between them.")
    d.box(20, 40, 340, 170, [("Your computer", "bold")], "ghost")
    d.box(40, 85, 300, 50, [("Local repository", "bold"), ("commits · branches · .git", "small")], "green")
    d.box(40, 145, 300, 45, [("Working folder", "bold")], "box")
    d.box(480, 85, 260, 70, [("Remote repository", "bold"), ("GitHub · GitLab · a server", "small")], "blue")
    d.arrow([(342, 100), (478, 100)], kind="blue", label="push", lx=410, ly=82)
    d.arrow([(478, 140), (342, 140)], kind="green", label="pull / fetch", lx=410, ly=158)
    d.text(610, 195, "clone = first copy, with history", "small")
    return d.render()


def ignore_flow():
    d = new("ignore-flow", 760, 250, "How Git decides what to skip",
            "Git checks .gitignore, then .git/info/exclude and the global ignore file. A file already tracked is never ignored.")
    d.box(20, 30, 150, 60, [("new file", "bold"), ("untracked", "small")], "box")
    d.box(230, 30, 210, 60, [("matches an ignore rule?", "bold"), (".gitignore · exclude", "small")], "amber")
    d.box(520, 10, 220, 50, [("yes: skipped by git add", "small")], "green")
    d.box(520, 70, 220, 50, [("no: shows up in status", "small")], "blue")
    d.arrow([(172, 60), (228, 60)], kind="blue")
    d.arrow([(442, 50), (518, 35)], kind="green")
    d.arrow([(442, 70), (518, 95)], kind="blue")
    d.box(20, 150, 720, 70, [("Already committed? Ignore rules do nothing.", "bold"), ("git rm --cached FILE  stops tracking it and keeps the file on disk", "code")], "red")
    return d.render()


if __name__ == "__main__":
    fns = [copies_vs_history, generations, config_levels, three_areas, concept_map, ignore_flow]
    for fn in fns:
        fn()
    print(len(fns), "diagrams written")
