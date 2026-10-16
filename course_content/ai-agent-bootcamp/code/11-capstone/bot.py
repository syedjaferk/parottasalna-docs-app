# bot.py - the Telegram side: receive messages, call support.handle_text, send the reply.
import os

import store
from support import handle_text
from telegram_api import TelegramError, get_updates, send_message, send_typing

ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0") or 0)     # your own user id: only you may use /stats

WELCOME = ("Hi! 👋 I'm the ChaiCart support assistant. Ask me about orders, payments, "
           "your account or anything else, and I'll do my best to help.")


def handle_update(message):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = (message.get("text") or "").strip()
    if not text:
        return
    if text == "/start":
        send_message(chat_id, WELCOME)
    elif text == "/stats" and user_id == ADMIN_ID:
        send_message(chat_id, str(store.stats()))
    else:
        send_typing(chat_id)
        reply = handle_text(user_id, chat_id, text)
        if reply:
            send_message(chat_id, reply)


def main():
    store.init()
    print("Support bot is running. Press Ctrl+C to stop.")
    offset = None
    while True:
        try:
            updates = get_updates(offset)
        except TelegramError as error:
            print("Telegram problem:", error)
            break
        for update in updates:
            offset = update["update_id"] + 1
            if "message" in update:
                try:
                    handle_update(update["message"])
                except Exception as error:               # one bad message must never stop the bot
                    print("Error while handling a message:", error)


if __name__ == "__main__":
    main()
