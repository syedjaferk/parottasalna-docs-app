# Session 8 · Telegram Gateway

**Day 2 · ⏱ about 100 minutes · 🧰 you need: [Session 7](07-hermes-deep-dive.md) done, a Telegram account ([Setup](../setup.md) step 9)**

## The big idea

Until now you talked to your agent in a black terminal window. Real people don't live there. They live in **WhatsApp, Telegram, Slack**.
A **gateway** is the bridge that carries messages between a chat app and your agent, so you can talk to it from **your phone**, from anywhere.

**Everyday example:** a restaurant kitchen (your agent) is hidden at the back. The **waiter** (the gateway) takes orders from customers
(chat messages), carries them to the kitchen, and brings the food (the answer) back. The customers never see the kitchen.

```{raw} html
:file: ../diagrams/s08-gateway.html
```

**By the end** you'll have your own bot on Telegram, built **two ways**:

1. 🛠️ **From scratch** in ~60 lines of Python (so you understand how it works).
2. 🤖 **With Hermes's gateway** (the easy, production way).

## Before you start (checklist)

- [ ] Telegram installed and signed in on your phone (or desktop).
- [ ] Your Session 5 agent works (`python agent.py`), and Hermes works (`hermes`).
- [ ] Your `.env` has the AI settings. We'll add two Telegram lines.

## 1. How a Telegram bot works

A Telegram **bot** is a special account run by a program, not a person. Three words to know:

| Word | Meaning |
|---|---|
| **BotFather** | Telegram's own bot that **creates** bots for you (it's free, takes a minute) |
| **Bot token** | the bot's **password**: a long text like `123456789:ABCdef...`. Whoever has it controls your bot |
| **User ID** | your **number** on Telegram (not your @username). We use it to decide who may talk to the bot |

### How does your program get the messages? Long polling

```{raw} html
:file: ../diagrams/s08-polling.html
```

Your program **asks Telegram: "any new messages?"** (`getUpdates`). If there are none, Telegram **waits** up to 25 seconds before
answering (that's the "long" in *long polling*). When a message arrives, Telegram answers at once. Your program replies with
`sendMessage` and asks again. Each message has an `update_id`, and you tell Telegram *"I've seen everything up to this number"*
(the `offset`), so it won't send the same message twice.

*(The other way is a **webhook**: Telegram calls **your** web address. That needs a public server, so we use polling. It works from your laptop.)*

## 2. Create your bot

1. In Telegram, search for **`@BotFather`** (it has a blue tick ✔) and open it.
2. Send: `/newbot`
3. It asks for a **name** (anything: `My Jarvis`) and a **username** (must be unique and end in `bot`: `asha_jarvis_bot`).
4. BotFather replies with your **token**. Copy it.

```text
Done! Congratulations on your new bot. You will find it at t.me/asha_jarvis_bot.
Use this token to access the HTTP API:
123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

:::{caution}
**The token is a password.** Never post it in a group, a screenshot, a video or GitHub. If it leaks: message BotFather, send `/revoke`, pick
your bot, and it will give you a new token (the old one stops working immediately).
:::

5. Find your **user ID**: message **`@userinfobot`** (or `@get_id_bot`). It replies with a number like `123456789`. That's your **user ID**. (You can also get it from the echo bot below.)

6. Add both to your project **`.env`** file (no quotes, no spaces):

```text
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ALLOWED_USERS=123456789
```

## 3. Part A · Build it from scratch

Put these files together in a folder (use `session8` inside your project, with a copy of `.env`):

* {download}`telegram_api.py <../code/08-telegram-gateway/telegram_api.py>`
* {download}`telegram_echo.py <../code/08-telegram-gateway/telegram_echo.py>`
* {download}`telegram_agent_bot.py <../code/08-telegram-gateway/telegram_agent_bot.py>`
* plus your Session 5 files: {download}`agent.py <../code/08-telegram-gateway/agent.py>`, {download}`tools.py <../code/08-telegram-gateway/tools.py>`, {download}`llm.py <../code/08-telegram-gateway/llm.py>`

**🐧 Linux**

```bash
cd ~/ai-agent-bootcamp
mkdir -p session8 && cd session8
cp ../.env .
source ../.venv/bin/activate
```

**🪟 Windows**

```powershell
cd ~\ai-agent-bootcamp
mkdir session8 -Force; cd session8
copy ..\.env .
..\.venv\Scripts\Activate.ps1
```

### Step 1 · The Telegram helper

```{literalinclude} ../code/08-telegram-gateway/telegram_api.py
:language: python
```

| Code | Meaning |
|---|---|
| `https://api.telegram.org/bot<TOKEN>/<method>` | **every** Telegram call has this shape. The token is part of the address |
| `call(method, **params)` | one function for any method. `**params` collects keyword arguments into a dictionary, which we send as JSON |
| `if not data.get("ok")` | Telegram answers `{"ok": true, "result": ...}` or `{"ok": false, "description": "..."}` |
| `get_updates` + `"timeout": wait` | long polling: Telegram holds the call open for up to 25 seconds |
| `requests.post(..., timeout=40)` | our own timeout must be **longer** than Telegram's 25 s, or we'd give up first |
| `send_message` splits at 4000 characters | Telegram refuses messages over 4096 characters |
| `send_typing` | shows "typing…" so the user knows we're working |

### Step 2 · The echo bot (test your token and find your ID)

```{literalinclude} ../code/08-telegram-gateway/telegram_echo.py
:language: python
```

```bash
python telegram_echo.py
```

Now open your bot in Telegram (the link `t.me/<your bot username>`), press **Start** and send `hello`.

**In your terminal:**

```text
Echo bot is running. Send it a message in Telegram. Press Ctrl+C to stop.
Message from Asha (user id 123456789): hello
```

**In Telegram, the bot replies:**

```text
You said: hello
Your user id is 123456789
```

**The loop in plain words:** ask for updates → for each one, remember `update_id + 1` as the new `offset` → read the text and who sent it → reply.
Stop it with `Ctrl + C`.

### Step 3 · Put your agent behind the bot

```{literalinclude} ../code/08-telegram-gateway/telegram_agent_bot.py
:language: python
```

```bash
python telegram_agent_bot.py
```

```text
Jarvis bot is running for 1 allowed user(s). Press Ctrl+C to stop.
```

Now chat with it **from your phone**:

```text
You:    What is the weather in Chennai and what is 17.5% of 2480?
Jarvis: It's 29.4 °C in Chennai, and 17.5% of 2480 is 434.
You:    Remember that I like filter coffee.
Jarvis: Noted! I'll remember that you like filter coffee.
```

**What's new in the code:**

| Code | Meaning |
|---|---|
| `ALLOWED = {int(x) for x in ... .split(",") if x}` | a **set** of allowed user ids read from `.env` (a set is a list with no repeats and a quick "is it in here?" test) |
| `if user["id"] not in ALLOWED:` | **access control**: strangers get a polite "private assistant" and the agent is never called |
| `agents = {}` + `agent_for(chat_id)` | **one agent (one memory) per chat**, so two people never share conversation history |
| `try/except Exception` in the main loop | one bad message must **never** crash the bot |
| `raise SystemExit("Set TELEGRAM_ALLOWED_USERS...")` | refuse to start without an allow-list. **Safe by default** |

:::{important}
**Why the allow-list matters:** anyone on Telegram who finds your bot's username can message it. Without a check, strangers could use **your**
AI quota and your tools (and your agent can read/write files on *your* computer). **Always allow-list.**
:::

### Try the blocked path

Ask a friend to message your bot. In your terminal you'll see `Blocked a message from user id 987654321`, and they get "Sorry, this is a private assistant." Your agent was never involved.

## 4. Part B · Hermes's gateway (the easy way)

Hermes has all of this built in (and more: Discord, Slack, WhatsApp...). **Stop your Python bot first** (`Ctrl + C`).

:::{caution}
**Only one program may use a bot token at a time.** If two programs poll the same bot, Telegram shows a **409 Conflict** error ("terminated by other getUpdates request"). Use a **separate bot** for Hermes (make another with `/newbot`) or stop the first program.
:::

### Step 1 · Configure

```bash
hermes gateway setup
```

Choose **Telegram**, paste your bot **token**, and your **allowed user ID(s)** when asked.

**Or do it by hand.** Add two lines to **Hermes's own** `.env` file:

| | File |
|---|---|
| 🐧 | `~/.hermes/.env` |
| 🪟 | `%LOCALAPPDATA%\hermes\.env` |

```text
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ALLOWED_USERS=123456789
```

(For several users, separate the ids with commas.)

### Step 2 · Start it

```bash
hermes gateway
```

Leave that terminal open. Now send **`hello`** to your bot on Telegram. Hermes answers.

### Step 3 · Useful commands inside Telegram

| Command | What it does |
|---|---|
| `/help` | list commands |
| `/new` | start a fresh conversation |
| `/model` | switch the model |
| `/sethome` | make **this chat** the "home": where scheduled jobs deliver their results |
| `/whoami` | who Hermes thinks you are |
| `/stop` | interrupt a long task |
| `/daily-brief` | any skill works as a command (Session 7) |

### Step 4 · Connect Session 7: scheduled jobs to your phone

In Telegram, send `/sethome` to your bot (this chat is now the home). Then:

```bash
hermes cron create "every day at 9am" "Run the daily-brief skill for Chennai." --skill daily-brief --deliver telegram
hermes cron list
hermes cron run <id>        # test it now
```

*(If your version names the delivery option differently, run `hermes cron create --help` to see the flags.)* The morning brief arrives on your phone. 🎉

### Step 5 · Keep it running

| Goal | Command |
|---|---|
| run in the foreground (you see logs) | `hermes gateway` |
| install as a background service that starts when you log in | `hermes gateway install` |
| check / start / stop / restart | `hermes gateway status` · `start` · `stop` · `restart` |
| remove the service | `hermes gateway uninstall` |

🪟 On Windows the service is a **Scheduled Task**. If it doesn't start after a reboot, run `hermes gateway status`.

## 5. Who may use the bot? (security)

| Setting (in Hermes's `.env`) | Meaning |
|---|---|
| `TELEGRAM_ALLOWED_USERS` | the user ids allowed to chat. **If nothing is set, everybody is denied**, which is the safe default |
| `TELEGRAM_GROUP_ALLOWED_USERS` / `TELEGRAM_GROUP_ALLOWED_CHATS` | for groups only: allowed senders, or allowed group ids |
| `GATEWAY_ALLOW_ALL_USERS=true` | lets **anyone** use it. ❌ Don't. |

**Your safety checklist for any chat bot:**

1. ✅ Allow-list user ids (don't depend on usernames. They can change).
2. ✅ Keep the token only in `.env`. Never in code or screenshots.
3. ✅ Keep tools **read-only** for chat users, and ask for approval for anything risky.
4. ✅ Remember: a chat user can try to *trick* your agent (**prompt injection**, Sessions 9-10). Allow-lists stop strangers. They don't stop an allowed user, or content the agent reads, from containing tricks.
5. ✅ If the token leaks → `/revoke` in BotFather.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `Telegram said: Unauthorized` | wrong or revoked token | copy the token again from BotFather, no spaces |
| `Telegram said: Conflict: terminated by other getUpdates request` | **two programs** use the same token | stop one, or make a second bot |
| The bot never answers | you didn't press **Start**, or the program stopped | open the bot, press Start, check the terminal |
| "Sorry, this is a private assistant" (to *you*) | your user id isn't in `TELEGRAM_ALLOWED_USERS` | run `telegram_echo.py` to see your id; fix `.env` |
| `ValueError: invalid literal for int()` | a username or spaces in the id list | the list must be **numbers** only: `123,456` |
| `TELEGRAM_BOT_TOKEN is missing` | wrong folder, so `.env` isn't found | `cd` to the folder with `.env` |
| Nothing arrives in groups | bots only see some group messages by default | message the bot directly, or use `/setprivacy` in BotFather |
| Replies are cut off | the answer was longer than 4096 characters | we split into chunks; check `send_message` |
| Hermes gateway starts but ignores you | the allowed-users line is wrong/missing | set `TELEGRAM_ALLOWED_USERS` in **Hermes's** `.env`, then restart the gateway |
| Works on 🐧 but `.env` isn't read on 🪟 | file saved as `.env.txt` | see Setup step 7 |

## Tasks

**Task 1 · Warm-up (10 min).** Run `telegram_echo.py`, message your bot and write down your user ID. Then ask a friend to do the same.
What differs between the two ids, and why do we use the id and not the username?

<details class="solution">
<summary>Answer</summary>

Every account has a different, permanent **number**. A *username* can be changed or removed at any time, and someone else could later take an old name. The numeric id
never changes, which makes it a safe thing to trust in an allow-list.

</details>

**Task 2 · Build (25 min).** Add a `/time` command to `telegram_agent_bot.py` that replies with the current time **without using the AI** (cheap and instant).

<details class="solution">
<summary>Answer</summary>

At the top: `from datetime import datetime`. Then in `handle()`, next to the other commands:

```python
    elif text == "/time":
        send_message(chat_id, datetime.now().strftime("It is %H:%M on %A, %d %B %Y."))
```

Commands that don't need intelligence should be plain code. It's faster and costs zero tokens. (Session 9 builds on this idea.)

</details>

**Task 3 · Challenge (45 min).** Add a **rate limit**: one user may send at most **5 messages per minute** to the agent. If they go over, reply *"Slow down, please. Try again in a minute."* and **don't call the AI**.

<details class="solution">
<summary>Answer</summary>

```python
import time
from collections import defaultdict, deque

recent = defaultdict(deque)          # user id -> times of their latest messages
LIMIT, WINDOW = 5, 60                # 5 messages per 60 seconds


def too_fast(user_id):
    now = time.time()
    times = recent[user_id]
    while times and now - times[0] > WINDOW:   # forget messages older than a minute
        times.popleft()
    if len(times) >= LIMIT:
        return True
    times.append(now)
    return False
```

In `handle()`, in the `else:` branch (the AI branch), start with:

```python
        if too_fast(user["id"]):
            send_message(chat_id, "Slow down, please. Try again in a minute.")
            return
```

This protects your free-tier quota and your wallet. Every public bot needs it. (Session 12 covers cost control.)

</details>

## Quiz

Take **"Session 8 · Quiz"** from the portal's **Quizzes** page (BotFather, token safety, user id, long polling, allow-lists, Hermes gateway).

## Recap

- ✅ A **gateway** connects a chat app to your agent so you can use it from your phone.
- ✅ Telegram bot: **BotFather** → token (a password!) → your **user id** (a number).
- ✅ **Long polling**: `getUpdates` with an `offset`, then `sendMessage`.
- ✅ **Allow-list** by user id, **one agent per chat**, never crash on one bad message.
- ✅ Hermes: `hermes gateway setup` / `hermes gateway`, `/sethome`, and delivery of scheduled jobs to Telegram.
- ✅ Only **one program per token** (409 conflict).

**Next:** [Session 9 · System 1 vs System 2 AI Thinking](09-system1-vs-system2.md). Why sending *every* message to a big LLM is slow, costly and unsafe, and what to use instead.

## Session materials

- {download}`telegram_api.py <../code/08-telegram-gateway/telegram_api.py>`
- {download}`telegram_echo.py <../code/08-telegram-gateway/telegram_echo.py>`
- {download}`telegram_agent_bot.py <../code/08-telegram-gateway/telegram_agent_bot.py>`
