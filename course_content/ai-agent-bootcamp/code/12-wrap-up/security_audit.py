# security_audit.py - a 1-minute safety check to run BEFORE you publish a project.
#   python security_audit.py            (checks the current folder)
#   python security_audit.py path/to/project
import os
import re
import sys

PATTERNS = {
    "Groq API key": r"gsk_[A-Za-z0-9]{20,}",
    "OpenRouter API key": r"sk-or-[A-Za-z0-9_-]{20,}",
    "OpenAI-style key": r"sk-[A-Za-z0-9]{32,}",
    "Telegram bot token": r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b",
    "Private key block": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "Hard-coded password": r"(?i)\bpassword\s*=\s*['\"][^'\"]{4,}['\"]",
}
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules"}
SKIP_FILES = {".env.example"}
SKIP_SUFFIXES = (".db", ".pyc", ".png", ".jpg", ".zip", ".safetensors")


def main(root):
    problems = 0

    # 1. Secrets written inside files
    for folder, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name in SKIP_FILES or name.endswith(SKIP_SUFFIXES):
                continue
            path = os.path.join(folder, name)
            try:
                text = open(path, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            for label, pattern in PATTERNS.items():
                if name == ".env" and label != "Private key block":
                    continue                      # the real .env is allowed to hold secrets. It must just never be uploaded
                for match in re.finditer(pattern, text):
                    line = text[:match.start()].count("\n") + 1
                    print(f"[FAIL] {label} found in {os.path.relpath(path, root)} line {line}")
                    problems += 1

    # 2. Is .env protected from git?
    gitignore = os.path.join(root, ".gitignore")
    ignored = open(gitignore).read().splitlines() if os.path.exists(gitignore) else []
    if os.path.exists(os.path.join(root, ".env")):
        if ".env" in [line.strip() for line in ignored]:
            print("[ OK ] .env exists and is listed in .gitignore")
        else:
            print("[FAIL] .env exists but is NOT in .gitignore: it would be uploaded to GitHub!")
            problems += 1
    for needed in ("support.db", "decisions.jsonl"):
        if os.path.exists(os.path.join(root, needed)) and needed not in [l.strip() for l in ignored]:
            print(f"[WARN] {needed} holds customer data and is not in .gitignore")
            problems += 1

    # 3. Is .env readable by other users? (Linux/macOS only)
    env = os.path.join(root, ".env")
    if os.path.exists(env) and os.name == "posix":
        mode = os.stat(env).st_mode & 0o077
        if mode:
            print("[WARN] .env can be read by other users. Fix: chmod 600 .env")
            problems += 1

    print("\nNo problems found. Safe to publish." if problems == 0 else f"\n{problems} problem(s). Fix them BEFORE you publish.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
