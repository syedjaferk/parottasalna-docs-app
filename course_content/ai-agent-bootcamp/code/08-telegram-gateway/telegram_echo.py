# telegram_echo.py - the smallest possible Telegram bot: it repeats what you say.
# Use it to check your token, and to find your numeric Telegram user id.
from telegram_api import TelegramError, get_updates, send_message

print("Echo bot is running. Send it a message in Telegram. Press Ctrl+C to stop.")
offset = None                                     # "the next update I have not seen yet"

while True:
    try:
        updates = get_updates(offset)
    except TelegramError as error:
        print("Problem:", error)
        break
    for update in updates:
        offset = update["update_id"] + 1          # mark this update as done
        message = update.get("message")
        if not message or "text" not in message:
            continue
        user = message["from"]
        print(f"Message from {user.get('first_name')} (user id {user['id']}): {message['text']}")
        send_message(message["chat"]["id"], f"You said: {message['text']}\nYour user id is {user['id']}")
