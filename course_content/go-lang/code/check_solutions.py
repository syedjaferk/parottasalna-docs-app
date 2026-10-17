"""Check the Go snippets written inside the session pages.

Every ```go block that contains `package main` is compiled and run. If the next fenced block is
```text, its content must equal what the program printed. Run:

    python course_content/go-lang/code/check_solutions.py [session-filter]
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SESSIONS = HERE.parent / "sessions"
FENCE = re.compile(r"^```(\w*)[^\n]*\n(.*?)^```", re.S | re.M)
NO_RUN = "<!-- no-run -->"


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    bad = checked = 0
    for page in sorted(SESSIONS.glob("*.md")):
        if only not in page.name:
            continue
        blocks = [(m.group(1), m.group(2), m.start()) for m in FENCE.finditer(page.read_text(encoding="utf-8"))]
        text = page.read_text(encoding="utf-8")
        for i, (lang, body, start) in enumerate(blocks):
            if lang != "go" or "package main" not in body:
                continue
            if NO_RUN in text[max(0, start - 40):start]:
                continue
            want = blocks[i + 1][1] if i + 1 < len(blocks) and blocks[i + 1][0] == "text" else None
            with tempfile.TemporaryDirectory() as tmp:
                tmp = Path(tmp)
                for name in ("go.mod", "go.sum"):
                    (tmp / name).write_bytes((HERE / name).read_bytes())
                (tmp / "main.go").write_text(body, encoding="utf-8")
                r = subprocess.run(["go", "run", "main.go"], cwd=tmp, capture_output=True, text=True, timeout=120)
            checked += 1
            got = (r.stdout + r.stderr).strip()
            if r.returncode and want is None:
                bad += 1
                print(f"FAIL {page.name} block {i}: {got[:300]}")
            elif want is not None and got != want.strip():
                bad += 1
                print(f"MISMATCH {page.name} block {i}\n--- want\n{want.strip()}\n--- got\n{got}\n")
    print(f"checked {checked} snippets, {bad} problems")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
