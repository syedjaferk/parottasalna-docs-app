# telegram_api.py - a tiny wrapper around the Telegram Bot API (just `requests`, no special library)
import os

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API = os.getenv("TELEGRAM_API_BASE", "https://api.telegram.org")   # only changed in tests


class TelegramError(Exception):
    pass


def call(method, **params):
    """Call any Telegram Bot API method and return its 'result'."""
    if not TOKEN:
        raise TelegramError("TELEGRAM_BOT_TOKEN is missing. Add it to your .env file.")
    try:
        response = requests.post(f"{API}/bot{TOKEN}/{method}", json=params, timeout=40)
        data = response.json()
    except (requests.RequestException, ValueError) as error:
        raise TelegramError(f"Could not reach Telegram ({error.__class__.__name__})")
    if not data.get("ok"):
        raise TelegramError(f"Telegram said: {data.get('description', 'unknown error')}")
    return data["result"]


def get_updates(offset=None, wait=25):
    """Long polling: Telegram keeps the call open for up to `wait` seconds until a message arrives."""
    params = {"timeout": wait, "allowed_updates": ["message"]}
    if offset is not None:
        params["offset"] = offset
    return call("getUpdates", **params)


def send_message(chat_id, text):
    """Send text. Telegram allows at most 4096 characters, so we split long answers."""
    text = text or "(empty reply)"
    for start in range(0, len(text), 4000):
        call("sendMessage", chat_id=chat_id, text=text[start:start + 4000])


def send_typing(chat_id):
    """Show 'typing...' in the chat while we think."""
    try:
        call("sendChatAction", chat_id=chat_id, action="typing")
    except TelegramError:
        pass
