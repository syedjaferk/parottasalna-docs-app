"""Checks that your computer is ready for the AI Agent Bootcamp.

Run it from your project folder, with the virtual environment turned on:

    python check_setup.py
"""
import os
import sys

OK, BAD = "[ OK ]", "[FAIL]"
problems = 0


def report(ok, text, fix=""):
    global problems
    print(f"{OK if ok else BAD} {text}")
    if not ok:
        problems += 1
        if fix:
            print(f"       -> {fix}")


# 1. Python version -----------------------------------------------------------
v = sys.version_info
report(v >= (3, 10), f"Python {v.major}.{v.minor}.{v.micro}", "Install Python 3.10 or newer (see Setup, step 2).")

# 2. Virtual environment ------------------------------------------------------
in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
report(in_venv, "Virtual environment is active", "Activate it: Linux 'source .venv/bin/activate', Windows '.\\.venv\\Scripts\\Activate.ps1'.")

# 3. Packages -----------------------------------------------------------------
try:
    import requests
    report(True, f"requests {requests.__version__}")
except ImportError:
    requests = None
    report(False, "requests is not installed", "Run: pip install requests")
try:
    from dotenv import load_dotenv
    report(True, "python-dotenv is installed")
except ImportError:
    load_dotenv = None
    report(False, "python-dotenv is not installed", "Run: pip install python-dotenv")

# 4. The .env file ------------------------------------------------------------
if load_dotenv:
    found = load_dotenv()
    report(found, ".env file found", "Create a file named .env in this folder (see Setup, step 7).")
key = os.getenv("LLM_API_KEY", "")
base = os.getenv("LLM_BASE_URL", "")
model = os.getenv("LLM_MODEL", "")
report(bool(key) and "paste" not in key.lower(), "LLM_API_KEY is set", "Add LLM_API_KEY=... to your .env file.")
report(bool(base), f"LLM_BASE_URL = {base or '(missing)'}", "Add LLM_BASE_URL=... to your .env file.")
report(bool(model), f"LLM_MODEL = {model or '(missing)'}", "Add LLM_MODEL=... to your .env file.")

# 5. Can we really talk to the AI provider? ----------------------------------------
if requests and key and base:
    try:
        r = requests.get(f"{base.rstrip('/')}/models", headers={"Authorization": f"Bearer {key}"}, timeout=20)
        if r.status_code == 200:
            names = sorted(m["id"] for m in r.json().get("data", []))
            report(True, f"The provider accepted your key ({len(names)} models available)")
            report(model in names or not names, f"Model '{model}' is available",
                   "Pick one from the list below and put it in LLM_MODEL.")
            print("       Some available models:", ", ".join(names[:8]))
        elif r.status_code in (401, 403):
            report(False, "The provider rejected your key", "Copy the key again, with no spaces or quotes.")
        else:
            report(False, f"The provider answered with status {r.status_code}", r.text[:150])
    except requests.RequestException as e:
        report(False, "Could not reach the provider", f"Check your internet connection and LLM_BASE_URL. ({e.__class__.__name__})")

print()
print("All good! You are ready." if problems == 0 else f"{problems} thing(s) to fix. Fix them, then run this again.")
sys.exit(1 if problems else 0)
