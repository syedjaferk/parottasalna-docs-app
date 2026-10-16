# telegram_agent_bot.py - your Session 5 agent, living in Telegram
import os

from agent import Agent
from llm import LLMError
from telegram_api import TelegramError, get_updates, send_message, send_typing

# Only these Telegram user ids may talk to the bot (comma-separated numbers in .env).
ALLOWED = {int(x) for x in os.getenv("TELEGRAM_ALLOWED_USERS", "").replace(" ", "").split(",") if x}

agents = {}                                        # one Agent (one memory) per chat


def agent_for(chat_id):
    if chat_id not in agents:
        agents[chat_id] = Agent(verbose=False)
    return agents[chat_id]


def handle(message):
    chat_id = message["chat"]["id"]
    user = message["from"]
    text = (message.get("text") or "").strip()
    if not text:
        return

    # ---- Access control: the most important safety rule of a public bot
    if user["id"] not in ALLOWED:
        print(f"Blocked a message from user id {user['id']}")
        send_message(chat_id, "Sorry, this is a private assistant.")
        return

    if text == "/start":
        send_message(chat_id, "Hi! I'm Jarvis. Ask me about the weather, maths, the time, or tell me to remember something.")
    elif text == "/reset":
        agents.pop(chat_id, None)
        send_message(chat_id, "Memory cleared.")
    elif text == "/whoami":
        send_message(chat_id, f"Your Telegram user id is {user['id']}.")
    else:
        send_typing(chat_id)
        try:
            send_message(chat_id, agent_for(chat_id).ask(text))
        except LLMError as error:
            send_message(chat_id, f"Sorry, my AI provider had a problem: {error}")


def main():
    if not ALLOWED:
        raise SystemExit("Set TELEGRAM_ALLOWED_USERS in .env first (run telegram_echo.py to find your id).")
    print(f"Jarvis bot is running for {len(ALLOWED)} allowed user(s). Press Ctrl+C to stop.")
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
                    handle(update["message"])
                except Exception as error:          # one bad message must never kill the bot
                    print("Error while handling a message:", error)


if __name__ == "__main__":
    main()
