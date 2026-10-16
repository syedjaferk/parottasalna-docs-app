# daily_summary.py - once a day: read today's messages, ask the LLM for a short report, send it to YOU.
# Run it by hand to test, then schedule it (see Session 11: cron on Linux, Task Scheduler on Windows).
#
#   python daily_summary.py          # builds the summary and sends it to TELEGRAM_ADMIN_CHAT
#   python daily_summary.py --print  # only print it
import json
import os
import sys

import store
from llm import LLMError, call_api
from support import STRONG_MODEL
from telegram_api import TelegramError, send_message


def build_summary():
    stats = store.stats()
    if stats["messages"] == 0:
        return f"Support summary for {stats['date']}: no customer messages today."
    # We send the LLM only NUMBERS and short snippets of urgent messages, never the whole chat history.
    prompt = (
        "Write a short daily support report for the shop owner: 5 bullet points maximum, plain words. "
        "Mention the volume, the busiest category, how many messages were blocked or need human review, "
        "and list the urgent ones. End with one suggestion.\n\nData:\n" + json.dumps(stats, ensure_ascii=False)
    )
    try:
        data = call_api({"model": STRONG_MODEL, "temperature": 0.2, "max_tokens": 300,
                         "messages": [{"role": "user", "content": prompt}]})
        return data["choices"][0]["message"]["content"].strip()
    except LLMError:
        return "Support summary (the AI was unavailable, so here are the raw numbers):\n" + json.dumps(stats, indent=2)


def main():
    store.init()
    summary = build_summary()
    print(summary)
    chat = os.getenv("TELEGRAM_ADMIN_CHAT", "")
    if "--print" in sys.argv or not chat:
        if not chat:
            print("\n(TELEGRAM_ADMIN_CHAT is not set, so nothing was sent.)")
        return
    try:
        send_message(int(chat), summary)
        print("\nSent to Telegram.")
    except TelegramError as error:
        print("\nCould not send to Telegram:", error)


if __name__ == "__main__":
    main()
