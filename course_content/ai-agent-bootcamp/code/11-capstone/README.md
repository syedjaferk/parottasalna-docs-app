# ChaiCart Support Bot

A Telegram support bot that is safe, cheap and remembers its customers.

**What it does**
- Blocks prompt-injection attacks before any LLM sees them (Laya guard, "both detectors must agree")
- Sends suspicious or upset messages to a human instead of answering automatically
- Triages every message (category, urgency, anger, difficulty) in one quick Laya call
- Routes easy messages to a cheap model and hard ones to a strong model
- Remembers each customer's conversation in SQLite
- Sends a daily summary to the owner

**Run it**
1. `python -m venv .venv` and activate it
2. `pip install torch --index-url https://download.pytorch.org/whl/cpu` then `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill it in
4. `python simulate.py` (test without Telegram), then `python bot.py`
5. Schedule `python daily_summary.py` once a day

**Safety notes**
- Customers never see your keys; `.env` is in `.gitignore`
- Rate limit: 5 messages per minute per customer; messages over 1000 characters are refused
- No dangerous tools: the bot can only reply with text
- Known limits: the guard is not perfect (see the test results in `test_guard.py`)
