# Session 7 · Hermes Deep Dive

**Day 2 · ⏱ about 100 minutes · 🧰 you need: [Session 6](06-meet-hermes.md) done, and `hermes` runs on your machine (`hermes doctor` is happy)**

## The big idea

On Day 1 you built an agent that forgets when you close it and only works when you talk to it. Today Hermes
gets three superpowers that fix exactly those two weaknesses:

| Superpower | The problem it solves | Everyday comparison |
|---|---|---|
| 🧠 **Persistent memory** | "It forgot who I am again!" | a diary the assistant reads every morning |
| 📘 **Skills** | "I keep explaining the same steps" | a recipe book the assistant follows and can add to |
| ⏰ **Scheduled tasks** | "It only works when I ask" | an alarm clock that makes the assistant do a job by itself |

```{raw} html
:file: ../diagrams/s07-three-powers.html
```

**By the end** you'll have an agent that remembers you, follows a custom skill **you wrote**, and sends itself a daily
summary without being asked.

## Before you start (checklist)

- [ ] `hermes` starts and answers a question (Session 6).
- [ ] You know where Hermes keeps its files: 🐧 `~/.hermes/`, 🪟 `%LOCALAPPDATA%\hermes\`.
- [ ] A practice folder open in your terminal (do **not** run Hermes from your home folder).

## 1. Memory: how Hermes remembers

### Two different kinds of memory (you saw both in Session 5!)

```{raw} html
:file: ../diagrams/s07-memory-layers.html
```

| Kind | Where it lives | What it holds | Like in your agent |
|---|---|---|---|
| **Conversation history** | the current session | everything said in *this* chat | `self.messages` |
| **Persistent memory** | two small text files | facts worth keeping **forever** | `notes.txt` + `summary` |
| **Session search** | a database of all past chats | "what did we discuss last week?" | (you didn't build this) |

### The two memory files

They live in the folder `memories` inside the Hermes folder:

| File | What goes in it | Size limit |
|---|---|---|
| **`MEMORY.md`** | the agent's own notes: how your computer is set up, your project conventions, lessons learned | about 2,200 characters |
| **`USER.md`** | *you*: your name, preferences, how you like answers | about 1,375 characters |

They are **small on purpose**. Every character is sent to the AI at the start of each session (and costs tokens!), so
Hermes keeps only the most useful facts. When the files are full, it must tidy up and merge or remove old entries.

:::{important}
**Memory is loaded when a session starts.** If Hermes saves a new fact in the middle of a chat, the file is updated immediately,
but the AI will only *see* it in the **next** session. Type `/new` to start a fresh session and load the updated memory.
:::

### Lab 1 · Teach Hermes about you

**Step 1.** Start Hermes and tell it three facts:

```text
Please remember these about me:
1. My name is <your name> and I am learning to build AI agents.
2. I prefer short answers with one example.
3. My laptop runs <Linux or Windows>, and I use VS Code.
```

Hermes decides what to save. You may see it use a **memory tool**. You can also say it directly: *"Save to memory that I prefer short answers."*

**Step 2.** **Look at the file yourself.** (Hermes may take a moment. Ask *"Did you save that?"* if nothing appears.)

**🐧 Linux**

```bash
cat ~/.hermes/memories/USER.md
cat ~/.hermes/memories/MEMORY.md
```

**🪟 Windows (PowerShell)**

```powershell
Get-Content "$env:LOCALAPPDATA\hermes\memories\USER.md"
Get-Content "$env:LOCALAPPDATA\hermes\memories\MEMORY.md"
```

You should see short lines with your facts, separated by a `§` symbol. If the file doesn't exist yet, Hermes hasn't saved anything. Ask it again to
*"save that to your memory"*.

**Step 3.** Prove it survives: type `/new` (a brand-new chat), then ask: *"What do you know about me?"*

```text
You: What do you know about me?
Hermes: You're <your name>, learning to build AI agents. You prefer short answers with one example, and you use VS Code on <your OS>.
```

**Step 4 · The bigger memory.** Hermes also stores *every* session in a database, so it can search old conversations. In the terminal:

```bash
hermes sessions list
```

Then in a new chat try: *"Search our earlier chats: what did I ask you about weather?"*

### Keep memory safe and clean

| Good habit | Why |
|---|---|
| Never tell the agent passwords or API keys | memory is plain text, and it is sent to the AI provider |
| Ask it to *"forget"* wrong facts, or edit the file | wrong memories make wrong answers |
| There is a setting `memory.write_approval: true` (in `config.yaml`) | Hermes then asks before it saves, so you control the diary |
| You can pause and approve: `/memory pending`, `/memory approve all` | for when approval is on |

## 2. Skills: reusable recipes

A **skill** is a **markdown file** with instructions: *"when the user wants X, do these steps"*. It's not code. It is a recipe
written in plain language that the AI reads and follows with its tools.

```{raw} html
:file: ../diagrams/s07-skill-anatomy.html
```

**Why use a skill instead of just asking each time?**

1. You write the steps **once**; Hermes follows them every time, consistently.
2. It saves tokens, because the skill is only loaded when it's needed.
3. You can **share** skills (they follow an open standard, *agentskills.io*).

### Where skills live

| | Folder |
|---|---|
| 🐧 | `~/.hermes/skills/` |
| 🪟 | `%LOCALAPPDATA%\hermes\skills\` |

Each skill is a **folder** that contains a file named exactly **`SKILL.md`**. You can group skills inside category folders.

### Anatomy of a `SKILL.md`

```markdown
---
name: daily-brief
description: Make a short morning brief with the weather for a city and the top 5 Hacker News stories.
version: 1.0.0
metadata:
  hermes:
    tags: [daily, news, weather]
    category: personal
---

# Daily Brief

## When to Use
...conditions that should trigger this skill...

## Procedure
1. ...steps...

## Pitfalls
- ...known mistakes...

## Verification
...how to know it worked...
```

| Part | Meaning |
|---|---|
| The part between `---` lines | **front matter**: facts *about* the skill (name, description, tags). It's YAML, the same format as `config.yaml` |
| `name` | the skill's identifier. This becomes the slash command **`/daily-brief`** |
| `description` | **the most important line.** Hermes uses it to decide *when* the skill applies (like a tool description in Session 4!) |
| `When to Use` | triggers, in plain language |
| `Procedure` | numbered steps. **Be specific**: URLs, formats, limits |
| `Pitfalls` | mistakes to avoid. *Teach it what goes wrong* |
| `Verification` | a quick self-check |

### Lab 2 · Install and use a skill that someone wrote

Download the two ready-made skills and put them in place:

* {download}`daily-brief/SKILL.md <../code/07-hermes-deep-dive/skills/daily-brief/SKILL.md>`
* {download}`study-buddy/SKILL.md <../code/07-hermes-deep-dive/skills/study-buddy/SKILL.md>`

**🐧 Linux**

```bash
mkdir -p ~/.hermes/skills/personal/daily-brief ~/.hermes/skills/personal/study-buddy
cp ~/Downloads/daily-brief/SKILL.md  ~/.hermes/skills/personal/daily-brief/SKILL.md
cp ~/Downloads/study-buddy/SKILL.md  ~/.hermes/skills/personal/study-buddy/SKILL.md
```

(Adjust `~/Downloads/...` to wherever the browser saved the files.)

**🪟 Windows (PowerShell)**

```powershell
$skills = "$env:LOCALAPPDATA\hermes\skills\personal"
New-Item -ItemType Directory -Force "$skills\daily-brief", "$skills\study-buddy" | Out-Null
Copy-Item "$HOME\Downloads\daily-brief\SKILL.md" "$skills\daily-brief\SKILL.md"
Copy-Item "$HOME\Downloads\study-buddy\SKILL.md" "$skills\study-buddy\SKILL.md"
```

:::{caution}
The file must be named **exactly `SKILL.md`**, with the capital letters, inside its **own folder**. A skill that isn't found is almost always a wrong file name or a wrong folder.
:::

**Use it.** Start Hermes (`hermes`) or type `/new`, and run:

```text
/skills
```

You should see `daily-brief` and `study-buddy` in the list. Now run a skill by typing its **name as a slash command**; anything after it is your instruction:

```text
/daily-brief for Chennai
```

**Expected result** (your numbers and stories will differ):

```text
Good morning! ☀️
Weather in Chennai: 29.4 °C, wind 11.2 km/h
Top stories:
1. Show HN: ...
2. ...
3. ...
4. ...
5. ...
```

Hermes read the skill's **Procedure**, used its own web/terminal tools to call the two public APIs *(the same Open-Meteo API from Session 1!)*, and
followed the **exact format** you specified. Try the other skill: `/study-buddy quiz me on Python lists`.

### Lab 3 · Write your own skill

Create a skill called **`explain-like-5`**:

1. Make the folder: 🐧 `mkdir -p ~/.hermes/skills/personal/explain-like-5` · 🪟 `New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\hermes\skills\personal\explain-like-5"`
2. Create `SKILL.md` in it (open it in VS Code: `code <path>`), with this content:

```markdown
---
name: explain-like-5
description: Explain any technical idea so a 5-year-old would understand, using one everyday comparison.
version: 1.0.0
metadata:
  hermes:
    tags: [learning, explain]
    category: personal
---

# Explain Like I'm 5

## When to Use
Use this when the user says "explain like I'm 5", "ELI5", or asks to explain a hard idea very simply.

## Procedure
1. Give a one-sentence answer using only simple words.
2. Give ONE everyday comparison (food, school, cricket, family, a bus...).
3. End with a question to check understanding.

## Pitfalls
- No jargon. If you must use a technical word, explain it immediately.
- Keep the whole answer under 80 words.

## Verification
The answer contains one comparison and ends with a question.
```

3. In Hermes: `/new` then `/explain-like-5 what is an API?`

**Another way:** you can also *ask Hermes to write a skill for you*, or after a long, successful task it may offer to save the steps as a skill. Always **read** what it writes
before trusting it.

### Skills vs tools (a common confusion)

| | **Tool** | **Skill** |
|---|---|---|
| What is it? | code that *does* something (a function) | instructions that tell the AI *how* to do a job |
| Written in | Python | plain markdown |
| Example | `get_weather()` | "daily brief: fetch weather, then news, in this format" |
| Needs programming? | yes | no |

A skill **uses** tools. The two work together: tools are the hands, skills are the recipes.

## 3. Scheduled tasks: work without being asked

Hermes has a built-in scheduler (like the alarm on your phone, but the "ring" is *run this prompt*).

```{raw} html
:file: ../diagrams/s07-cron-flow.html
```

### How scheduling works inside (build a tiny one yourself)

A scheduler is just a loop that wakes up every few seconds and asks *"is any job due?"* Run this to see the idea:

```{literalinclude} ../code/07-hermes-deep-dive/mini_scheduler.py
:language: python
```

```bash
python mini_scheduler.py
```

```text
Scheduler started. It checks the clock every second. Press Ctrl+C to stop.
  [08:00:10] Job ran! (imagine: fetch news, send to Telegram)
  [08:00:20] Job ran! (imagine: fetch news, send to Telegram)
  [08:00:30] Job ran! (imagine: fetch news, send to Telegram)
All jobs finished.
```

Hermes's scheduler does the same, but its job is *"run this prompt through the agent"*, and its output is delivered to a place you choose.

### Three ways to create a job

**A. From chat, with `/cron`:**

```text
/cron add "in 5m" "Remind me to stand up and stretch"
/cron add "every 2h" "Check the weather in Chennai and tell me if it will rain"
/cron add "every 1h" "Summarise today's top Hacker News story" --skill daily-brief
```

**B. From the normal terminal (no chat needed):**

```bash
hermes cron create "every 2h" "Check server status"
```

**C. Just ask in plain language:**

```text
Every morning at 9am, run my daily-brief skill and send me the result.
```

### How to write the schedule

| You write | It means |
|---|---|
| `in 30m`, `in 2h`, `in 1d` | **once**, after a delay |
| `every 30m`, `every 2h`, `every hour` | repeats at that interval |
| `every day at 9am`, `weekdays at 9am`, `every monday 9am` | at a time of day |
| `0 9 * * *` | a **cron expression**: minute hour day month weekday → "09:00 every day" |
| `2026-12-01T09:00:00` | once, at an exact time |

### Where does the result go? (delivery)

| `deliver` | Where the output goes |
|---|---|
| `local` | saved to a file in `~/.hermes/cron/output/` (the default when you create jobs from the terminal) |
| `origin` | back to the chat where you created it (the default inside Telegram) |
| `telegram` | your Telegram "home channel" (set up in Session 8) |
| `telegram:123456` | one specific Telegram chat |

### Manage your jobs

```bash
hermes cron list                 # see all jobs and their ids
hermes cron status               # is the scheduler alive?
hermes cron pause <name_or_id>   # stop without deleting
hermes cron resume <name_or_id>
hermes cron run <name_or_id>     # run it on the next tick (great for testing!)
hermes cron edit <name_or_id>    # change schedule / prompt / delivery
hermes cron remove <name_or_id>  # delete it
```

:::{important}
**Jobs run inside the *gateway*.** The gateway is a background program (Session 8) that checks for due jobs **every 60 seconds**.
If the gateway isn't running, nothing fires. When you start it later, the waiting jobs run. Start it with:

```bash
hermes gateway
```

(leave that terminal open), or install it as a background service that starts at login: `hermes gateway install`.
🪟 On Windows this uses a *Scheduled Task*, so it starts when you log in.
:::

### Lab 4 · Your first automated task

**Step 1.** In one terminal start the gateway and leave it running:

```bash
hermes gateway
```

**Step 2.** In a **second** terminal create a quick, one-time job:

```bash
hermes cron create "in 5m" "Give me one motivational sentence for a beginner who is learning AI agents."
hermes cron list
```

**Step 3.** Wait five minutes (the gateway checks every 60 seconds). Then look at the saved result:

**🐧 Linux**

```bash
ls ~/.hermes/cron/output/
cat ~/.hermes/cron/output/*
```

**🪟 Windows**

```powershell
dir "$env:LOCALAPPDATA\hermes\cron\output"
Get-Content "$env:LOCALAPPDATA\hermes\cron\output\*"
```

**Step 4.** Now a recurring job that uses your skill:

```bash
hermes cron create "every day at 9am" "Run the daily-brief skill for Chennai." --skill daily-brief
hermes cron list
hermes cron run <id from the list>      # test it now instead of waiting until 9am
```

Delivery to your **phone** comes in Session 8.

## 4. Putting it all together: a day in the life

```{raw} html
:file: ../diagrams/s07-day-in-life.html
```

1. **09:00**: the scheduler fires `daily-brief`. The *skill* tells Hermes the steps. The *tools* fetch weather and news. *Memory* knows you like short answers. The result goes to Telegram.
2. **Midday**: you chat. Hermes remembers your name and projects.
3. **Evening**: `/new` and ask *"what did we decide yesterday?"*. *Session search* finds the old chat.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `/skills` doesn't show my skill | wrong folder or file name | file must be `SKILL.md` inside `skills/<category>/<name>/`; run `/new` or restart Hermes |
| The skill loads but is ignored | the `description` is vague | rewrite it: *what* it does and *when* to use it |
| `YAML` error when loading the skill | a tab in the front matter, or a missing `---` | use spaces; keep both `---` lines |
| Memory file is empty | Hermes didn't save, or you haven't started a new session | ask it to *save to memory*; then `/new` |
| "Memory is full" style errors | files are limited to about 2,200 / 1,375 characters | ask Hermes to consolidate, or edit the file |
| The scheduled job never runs | the gateway isn't running | `hermes gateway` (leave it open) or `hermes gateway install`; check `hermes cron status` |
| Job ran but I can't find the output | delivery is `local` | look in `~/.hermes/cron/output/` or choose `deliver` to `telegram` |
| 🪟 Gateway stops after a restart | a group policy blocks the logon trigger | run `hermes gateway status`; see Hermes's Windows guide |
| Wrong time | the schedule uses your computer's time zone | check your system clock/time zone |

## Tasks

**Task 1 · Warm-up (15 min).** Tell Hermes one thing you *don't* like (*"I don't like long explanations"*). Open `USER.md`. In which file did it save the fact, and why that file and not `MEMORY.md`?

<details class="solution">
<summary>Answer</summary>

It goes into **`USER.md`**, because that file is the *user profile* (your preferences and style). **`MEMORY.md`** holds the agent's own notes: your environment,
project conventions and lessons learned. If it landed in the other file, that's fine too; the line between them is a guideline.

</details>

**Task 2 · Build (30 min).** Write a skill **`bug-explainer`**: when the user pastes an error message, it (1) says in one sentence what the error means, (2) lists the 3 most likely causes, (3) gives one fix to try first. Test it with: `/bug-explainer ModuleNotFoundError: No module named 'requests'`.

<details class="solution">
<summary>Answer</summary>

`~/.hermes/skills/personal/bug-explainer/SKILL.md`:

```markdown
---
name: bug-explainer
description: Explain a programming error message in simple words and suggest what to try first.
version: 1.0.0
metadata:
  hermes:
    tags: [debugging, learning]
    category: personal
---

# Bug Explainer

## When to Use
Use this when the user pastes an error message or traceback and asks what it means.

## Procedure
1. In ONE simple sentence, say what the error means.
2. List the 3 most likely causes, shortest first.
3. Give ONE fix to try first, with the exact command or code line.

## Pitfalls
- Do not guess a cause that doesn't match the error text.
- If the message is cut off, ask the user for the full traceback.

## Verification
The reply has one sentence, three causes and one fix.
```

For the example error, a good answer mentions an inactive virtual environment and `pip install requests`.

</details>

**Task 3 · Challenge (45 min).** Create a **scheduled job** that runs *every weekday at 8am* and uses `study-buddy` to ask you **one** Python question, saved with `deliver` to `local`. Use `hermes cron run` to test it now. Then pause it with `hermes cron pause`.

<details class="solution">
<summary>Answer</summary>

```bash
hermes cron create "weekdays at 8am" "Run the study-buddy skill: ask me ONE Python beginner question. Do not wait for an answer." --skill study-buddy
hermes cron list                    # copy the job id or name
hermes cron run <id>                # test now, then read ~/.hermes/cron/output/
hermes cron pause <id>              # stop it without deleting
```

A scheduled job runs **unattended**: nobody is there to answer, so the prompt says *"do not wait for an answer"*. Remember to keep unattended jobs harmless: only ask them to
read, summarise and report, never to delete or send money.

</details>

## Quiz

Take **"Session 7 · Quiz"** from the portal's **Quizzes** page (memory files, `/new`, skills, `SKILL.md`, scheduling, delivery, gateway).

## Recap

- ✅ **Memory**: `USER.md` (about you) and `MEMORY.md` (agent notes) are small, loaded at **session start**; `/new` reloads them. Past chats are searchable.
- ✅ **Skills**: a folder with `SKILL.md` (front matter + When to Use / Procedure / Pitfalls / Verification), run as `/<name>`.
- ✅ **Scheduled tasks**: `/cron add` or `hermes cron create`; schedules like `every 2h` or `weekdays at 9am`; manage with `list`, `pause`, `run`, `remove`.
- ✅ Jobs run inside the **gateway**, which must be running.
- ✅ Tools are hands, skills are recipes, memory is a diary, the scheduler is an alarm clock.

**Next:** [Session 8 · Telegram Gateway](08-telegram-gateway.md). We put your agent on your **phone**.

## Session materials

- {download}`daily-brief/SKILL.md <../code/07-hermes-deep-dive/skills/daily-brief/SKILL.md>`
- {download}`study-buddy/SKILL.md <../code/07-hermes-deep-dive/skills/study-buddy/SKILL.md>`
- {download}`mini_scheduler.py <../code/07-hermes-deep-dive/mini_scheduler.py>`
