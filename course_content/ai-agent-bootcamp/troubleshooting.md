# Troubleshooting

When something breaks, **don't panic and don't guess**. Do these three things:

1. **Read the last line of the error.** It usually names the problem.
2. **Find your problem in the tables below.** Each row has the fix for 🐧 Linux and 🪟 Windows.
3. Still stuck? Copy the **whole error** (and what you typed) when you ask for help. Never paste your API key or token.

:::{tip}
**Three checks fix half of all problems:** (1) Is the virtual environment on (`(.venv)` at the start of the prompt)? (2) Are you in the right folder (`pwd` on 🐧, `pwd` or `cd` on 🪟)? (3) Did you save the file?
:::

## Python, venv and pip

| Symptom | Cause | Fix |
|---|---|---|
| 🐧 `python: command not found` | Linux calls it `python3` | use `python3`, or activate the venv and use `python` |
| 🪟 `'python' is not recognized` | Python isn't on PATH | re-run the installer and tick **Add python.exe to PATH**; open a **new** PowerShell |
| 🪟 `python` opens the Microsoft Store | Python isn't installed | `winget install -e --id Python.Python.3.12`, then a new PowerShell |
| 🪟 `running scripts is disabled on this system` | PowerShell safety setting | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (answer `Y`) |
| 🐧 `externally-managed-environment` | `pip` used outside a venv | activate the venv first: `source .venv/bin/activate` |
| 🐧 `No module named venv` | the venv package is missing | `sudo apt install python3-venv` |
| `ModuleNotFoundError: No module named 'requests'` | venv is off or package missing | activate the venv; `pip install requests python-dotenv` |
| `ModuleNotFoundError: No module named 'llm'` | `llm.py` isn't in the same folder | copy it next to your script |
| `IndentationError` | uneven spaces | use 4 spaces; never mix tabs and spaces |
| `pip` is very slow | slow internet | wait, or retry later |

**How to check which Python you are using**

```bash
python -c "import sys; print(sys.executable)"
```

It should print a path that contains `.venv`.

## `.env` and keys

| Symptom | Cause | Fix |
|---|---|---|
| `No API key found` / `None` | you're in the wrong folder, or no `.env` | `cd` to the folder that contains `.env` |
| 🪟 `.env.txt` | Notepad added `.txt` | create it in VS Code; check with `dir -Force` |
| `401` / "rejected your key" | key wrong, or has spaces/quotes | copy it again. No quotes, no spaces around `=` |
| `.env` changes are ignored | the old value is still in your terminal | open a new terminal, or restart the program |
| You pasted a key somewhere public | leaked | **delete the key** on the provider's website and create a new one |

## AI provider errors (Groq, OpenRouter, Ollama)

| Symptom | Cause | Fix |
|---|---|---|
| `404 model not found` | model name changed or typo | run `python check_setup.py`; copy a name from its list into `LLM_MODEL` |
| `429` rate limit | free tier is busy | wait a minute; use a smaller model; our `call_api` retries by itself |
| `ConnectionError` / timeout | no internet, or wrong `LLM_BASE_URL` | check the URL (Groq ends in `/openai/v1`) |
| Answer is cut off | `max_tokens` too small | raise it |
| `KeyError: 'choices'` | the API returned an error, not an answer | use `call_api` and print the response text |
| Tools never get called | vague description, or a model without tool support | improve the description; use a Llama 3.x model on Groq |
| `400` after a long agent chat | a tool result lost its request (bad trimming) | cut history only at `user` messages |
| Ollama is slow or runs out of memory | model too big for your RAM | use a smaller model (`llama3.2`), or Groq |

## Hermes

| Symptom | Cause | Fix |
|---|---|---|
| `hermes: command not found` | PATH not updated | 🐧 `source ~/.bashrc`; 🪟 open a **new** PowerShell, or run `& "$env:LOCALAPPDATA\hermes\bin\hermes.exe"` |
| Anything unclear | many causes | run **`hermes doctor`**. It explains what is missing |
| `API key not set` | the key isn't in **Hermes's** `.env` | `hermes config set GROQ_API_KEY ...`. It is separate from your project's `.env` |
| YAML parse error | tab, wrong indentation or BOM | spaces only; save as **UTF-8 without BOM** |
| "context too small" | model/endpoint under 64K tokens | use Groq/OpenRouter; for Ollama start with `OLLAMA_CONTEXT_LENGTH=64000` |
| `/skills` doesn't show my skill | wrong file/folder | `~/.hermes/skills/<category>/<name>/SKILL.md` (exact name); `/new` |
| Scheduled job never runs | gateway isn't running | `hermes gateway`; check `hermes cron status` |
| 🪟 `WinError 193` | a `.cmd` tool was called as `.exe` | run `hermes doctor` and follow the advice |
| Gateway ignores you | allowed-users missing | set `TELEGRAM_ALLOWED_USERS` in Hermes's `.env`; restart the gateway |

## Telegram

| Symptom | Cause | Fix |
|---|---|---|
| `Unauthorized` | wrong or revoked token | copy it again from BotFather |
| `Conflict: terminated by other getUpdates request` | two programs use the same token | stop one, or create a second bot |
| The bot never answers | you didn't press **Start**, or the program stopped | open the bot, press Start, read the terminal |
| "private assistant" shown to **you** | your id isn't in the allow-list | run `telegram_echo.py` to see your id |
| `ValueError: invalid literal for int()` | text in the id list | only numbers separated by commas |
| Summary can't be sent to you | you never messaged the bot | send it a message first |

## Laya and PyTorch

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: laya` | wrong venv | activate it; `pip install laya` |
| Install fails on `torch` | old Python or no space | Python 3.10+; free 3 GB; `pip install torch --index-url https://download.pytorch.org/whl/cpu` first |
| First question takes 10 s or more | the model loads on first use | normal. Create the `Router` **once** |
| Very slow every time | `Router` re-created per message | keep one global `router` |
| Out of memory | little RAM | close other apps; `Router(max_loaded=1)` |
| Warning lines (`return Agent(repo...`) | harmless library messages | ignore, unless a red `Traceback` follows |
| Everything is `other` | non-English text | use `model="multilingual"` |

## SQLite, scheduling and Git

| Symptom | Cause | Fix |
|---|---|---|
| `no such table: messages` | wrong folder, or `store.init()` not run | run from `session11`; `bot.py`/`simulate.py` call it |
| Memory empty after restart | a new `support.db` in another folder | always run from the same folder |
| Scheduled job does nothing | plain `python` / wrong folder | use the **full path** to the venv's Python and `cd` first; read the log |
| 🐧 cron didn't run | tiny `PATH` | absolute paths; `grep CRON /var/log/syslog` |
| 🪟 `schtasks` access denied | policy | run PowerShell as administrator, or use the Task Scheduler window |
| `git status` lists `.env` | not ignored | add `.env` to `.gitignore`, then `git rm --cached .env` |
| `git push` rejects your password | GitHub needs a token | create a personal access token, or `gh auth login` |

## Still stuck?

Write down: **what you typed**, **the full error**, **your operating system**, and **what you already tried**. That makes a question easy to answer. You can reach the organisers at the contact on the [bootcamp page](https://jarvis.parottasalna.com/).
