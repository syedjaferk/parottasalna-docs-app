"""Run every Go example and save what it prints next to it as <name>.out.

The session pages show these files, so the output on the page is always real.
Usage:  python course_content/go-lang/code/run_examples.py [filter]
Each program runs in a fresh temporary folder, so file examples never touch the repo.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
# (file, extra args after the file, stdin, go flags) -> output file suffix
EXTRA = {
    "09-cli/args.go": [([], ".out"), (["Asha"], ".asha.out")],
    "09-cli/flags.go": [(["-dir=./src", "-ext=.go", "-verbose", "-limit=5", "extra"], ".out"), ([], ".missing.out")],
    "09-cli/finder.go": [(["-dir=09-cli/finder_tree", "-ext=.go"], ".out"), (["-dir=nope"], ".bad.out")],
    "10-logging/config.go": [([], ".out")],
}
SKIP = {"11-http/server.go"}  # needs a real port; see the session for curl output
TIMEOUT = 60


def run(cmd, cwd):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return "(timed out)\n"
    text = r.stdout + r.stderr
    text = text.replace(str(HERE), "<course>")
    text = re.sub(r"\n?exit status \d+\n?$", "\n", text)
    return text


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    for src in sorted(HERE.glob("*/*.go")):
        rel = src.relative_to(HERE).as_posix()
        if only not in rel or src.name.endswith("_test.go") or rel in SKIP or rel.startswith("18-testing/"):
            continue
        for args, suffix in EXTRA.get(rel, [([], ".out")]):
            with tempfile.TemporaryDirectory() as tmp:
                work = Path(tmp)
                if rel.startswith(("09-cli", "10-logging")):
                    work = HERE  # these read files that live next to the course code
                # compile first, then run the binary from the working folder, so paths in output are tidy
                exe = Path(tmp) / "prog"
                b = subprocess.run(["go", "build", "-o", str(exe), str(src)], cwd=HERE, capture_output=True, text=True)
                if b.returncode:
                    print("BUILD FAIL", rel, b.stderr)
                    continue
                out = run([str(exe), *args], work)
            (src.with_suffix("").parent / (src.stem + suffix)).write_text(out, encoding="utf-8")
            print("ok", rel, suffix)


if __name__ == "__main__":
    main()
