"""Diagrams for Sessions 7-9."""
from _dg import D, diagram


# ------------------------------------------------------------------ Session 7
@diagram
def s07_three_powers():
    d = D("s07-three-powers", 720, 220, "Three Hermes superpowers",
          "Memory remembers you, skills are reusable recipes, and scheduled tasks make Hermes work by itself.")
    items = [("Memory", "a diary it reads", "every morning", "green"), ("Skills", "a recipe book it", "follows and extends", "blue"),
             ("Scheduler", "an alarm clock that", "runs a job for you", "amber")]
    for i, (t, a, b, k) in enumerate(items):
        x = 20 + i * 235
        d.box(x, 30, 210, 130, [(t, "bold"), (a, "small"), (b, "small")], k)
    d.text(360, 195, "fixes: forgetting  ·  repeating yourself  ·  only working when asked", "small")
    return d.render()


@diagram
def s07_memory_layers():
    d = D("s07-memory-layers", 720, 250, "Hermes memory layers",
          "Conversation history is for this chat; MEMORY.md and USER.md hold small lasting facts; session search finds old chats.")
    d.box(20, 30, 210, 150, [("This chat", "bold"), ("conversation history", "small"), ("gone with /new", "small")], "blue")
    d.box(255, 30, 210, 150, [("Lasting facts", "bold"), ("USER.md  (you)", "code"), ("MEMORY.md  (notes)", "code"), ("loaded each session", "small")], "green")
    d.box(490, 30, 210, 150, [("All past chats", "bold"), ("state.db", "code"), ("searchable", "small"), ("hermes sessions list", "small")], "amber")
    d.text(360, 215, "small and cheap  ←→  big and searchable", "small")
    return d.render()


@diagram
def s07_skill_anatomy():
    d = D("s07-skill-anatomy", 720, 290, "Anatomy of SKILL.md",
          "A skill is a markdown file: front matter says what it is; the body says when to use it and the steps to follow.")
    d.box(20, 20, 330, 250, [], "box")
    rows = [("---", "ghost"), ("name: daily-brief", "blue"), ("description: ...", "blue"), ("---", "ghost"),
            ("## When to Use", "amber"), ("## Procedure", "amber"), ("## Pitfalls", "amber"), ("## Verification", "amber")]
    for i, (t, k) in enumerate(rows):
        d.box(36, 32 + i * 29, 298, 24, (t, "code"), k, rx=4)
    notes = [(44, "front matter (YAML): facts ABOUT the skill"), (73, "name → becomes the command /daily-brief"), (102, "description → how Hermes decides to use it"),
             (160, "When to Use: the triggers"), (189, "Procedure: the numbered steps"), (218, "Pitfalls: mistakes to avoid"), (247, "Verification: how to check it worked")]
    for y, t in notes:
        d.arrow([(352, y), (400, y)], kind="blue", head=False)
        d.text(410, y, t, "small"); d.els[-1] = d.els[-1].replace('text-anchor="middle"', 'text-anchor="start"')
    return d.render()


@diagram
def s07_cron_flow():
    d = D("s07-cron-flow", 720, 230, "How a scheduled task runs",
          "The gateway checks the clock every minute; when a job is due it runs the prompt through the agent and delivers the result.")
    d.box(20, 70, 130, 70, [("Job", "bold"), ("every day 9am", "small")], "ghost")
    d.box(200, 70, 150, 70, [("Gateway", "bold"), ("checks every 60 s", "small")], "amber")
    d.box(400, 70, 130, 70, [("Agent", "bold"), ("runs the prompt", "small")], "blue")
    d.box(580, 20, 120, 50, [("Telegram", "bold")], "green")
    d.box(580, 90, 120, 50, [("local file", "bold")], "green")
    d.arrow([(150, 105), (198, 105)], kind="blue"); d.arrow([(350, 105), (398, 105)], kind="blue")
    d.arrow([(530, 95), (578, 50)], kind="green"); d.arrow([(530, 115), (578, 115)], kind="green")
    d.text(360, 185, "If the gateway is not running, nothing fires. Start it: hermes gateway", "small")
    return d.render()


@diagram
def s07_day_in_life():
    d = D("s07-day-in-life", 720, 210, "A day with Hermes",
          "Morning: a scheduled skill sends your brief. Midday: it remembers you. Evening: it searches old chats.")
    items = [("09:00", "scheduler + skill", "daily brief → Telegram", "amber"), ("12:00", "memory", "knows your name & style", "green"), ("20:00", "session search", "\"what did we decide?\"", "blue")]
    for i, (t, a, b, k) in enumerate(items):
        x = 20 + i * 235
        d.text(x + 105, 22, t, "title")
        d.box(x, 35, 210, 100, [(a, "bold"), (b, "small")], k)
    d.arrow([(40, 165), (680, 165)], kind="blue")
    return d.render()


# ------------------------------------------------------------------ Session 8
@diagram
def s08_gateway():
    d = D("s08-gateway", 720, 220, "A gateway connects chat apps to your agent",
          "Like a waiter: it carries messages from customers (chat apps) to the kitchen (your agent) and brings answers back.")
    d.box(20, 20, 150, 50, ("Telegram", "bold"), "blue"); d.box(20, 85, 150, 50, ("Discord", "bold"), "ghost"); d.box(20, 150, 150, 50, ("Slack", "bold"), "ghost")
    d.box(250, 60, 160, 90, [("GATEWAY", "bold"), ("the waiter", "small")], "amber")
    d.box(500, 60, 190, 90, [("YOUR AGENT", "bold"), ("the kitchen", "small")], "green")
    for y in (45, 110, 175):
        d.arrow([(170, y), (248, 105)], kind="blue")
    d.arrow([(410, 90), (498, 90)], kind="blue"); d.arrow([(498, 125), (412, 125)], kind="green")
    return d.render()


@diagram
def s08_polling():
    d = D("s08-polling", 720, 270, "Long polling",
          "Your program asks 'any new messages?'. Telegram waits up to 25 seconds and answers as soon as one arrives.")
    d.box(30, 20, 180, 230, [], "box"); d.text(120, 38, "YOUR PROGRAM", "title")
    d.box(510, 20, 180, 230, [], "box"); d.text(600, 38, "TELEGRAM", "title")
    d.arrow([(210, 70), (508, 70)], kind="blue", label="getUpdates(offset=11)", lx=360, ly=54)
    d.text(360, 100, "…waiting (up to 25 s)…", "small")
    d.arrow([(508, 135), (210, 135)], kind="green", label="[ message 11: hello ]", lx=360, ly=119)
    d.arrow([(210, 175), (508, 175)], kind="blue", label="sendMessage(\"You said hello\")", lx=360, ly=159)
    d.arrow([(210, 220), (508, 220)], kind="blue", label="getUpdates(offset=12)", lx=360, ly=204)
    d.text(120, 238, "offset = last update_id + 1", "small")
    return d.render()


# ------------------------------------------------------------------ Session 9
@diagram
def s09_two_systems():
    d = D("s09-two-systems", 720, 250, "System 1 and System 2 AI",
          "A small classifier answers fast with labels; an LLM thinks slowly and writes text. Use each for what it is good at.")
    d.box(20, 20, 330, 200, [], "box"); d.text(185, 38, "SYSTEM 1 · fast, automatic", "title")
    d.box(40, 55, 290, 36, ("Laya: label + probability", ""), "green")
    d.box(40, 100, 290, 36, ("cheap · local · repeatable", ""), "green")
    d.box(40, 145, 290, 36, ("sort · block · route", ""), "green")
    d.text(185, 205, "the receptionist", "small")
    d.box(370, 20, 330, 200, [], "box"); d.text(535, 38, "SYSTEM 2 · slow, careful", "title")
    d.box(390, 55, 290, 36, ("LLM: writes and reasons", ""), "blue")
    d.box(390, 100, 290, 36, ("costs tokens · seconds", ""), "blue")
    d.box(390, 145, 290, 36, ("explain · plan · use tools", ""), "blue")
    d.text(535, 205, "the specialist doctor", "small")
    return d.render()


@diagram
def s09_everything_llm():
    d = D("s09-everything-llm", 720, 230, "Everything to the LLM",
          "If every message goes to a big model, you pay, wait and expose yourself, even for 'thanks!' and attacks.")
    msgs = ["Thanks!", "Opening hours?", "Ignore your rules...", "Refund please"]
    for i, m in enumerate(msgs):
        d.box(20, 20 + i * 48, 170, 38, (m, ""), "box")
        d.arrow([(190, 39 + i * 48), (330, 115)], kind="red" if i == 2 else "blue")
    d.box(330, 80, 160, 70, [("BIG LLM", "bold"), ("sees everything", "small")], "amber")
    d.box(540, 20, 160, 50, [("slow", "bold")], "red"); d.box(540, 85, 160, 50, [("costly", "bold")], "red"); d.box(540, 150, 160, 50, [("unsafe", "bold")], "red")
    d.arrow([(490, 100), (538, 45)], kind="red"); d.arrow([(490, 115), (538, 110)], kind="red"); d.arrow([(490, 130), (538, 175)], kind="red")
    return d.render()


@diagram
def s09_gatekeeper():
    d = D("s09-gatekeeper", 720, 230, "A fast gatekeeper in front",
          "System 1 sorts every message first: attacks are blocked, easy ones get a cheap answer, only hard ones reach the strong LLM.")
    d.box(20, 85, 130, 60, [("Message", "bold")], "ghost")
    d.box(200, 70, 150, 90, [("Laya gate", "bold"), ("System 1", "small")], "green")
    d.arrow([(150, 115), (198, 115)], kind="blue")
    d.box(430, 10, 160, 50, [("Block", "bold")], "red"); d.box(430, 85, 160, 50, [("Cheap model", "bold")], "blue"); d.box(430, 160, 160, 50, [("Strong LLM", "bold")], "amber")
    d.arrow([(350, 90), (428, 35)], kind="red"); d.arrow([(350, 115), (428, 110)], kind="blue"); d.arrow([(350, 140), (428, 185)], kind="blue")
    d.text(645, 35, "attacks", "small"); d.text(645, 110, "easy", "small"); d.text(645, 185, "hard", "small")
    return d.render()


@diagram
def s09_laya_io():
    d = D("s09-laya-io", 720, 250, "What goes into Laya and what comes out",
          "You give a state (the text) and typed questions; one quick pass returns an answer plus a probability for each question.")
    d.box(20, 20, 200, 80, [("state", "bold"), ('{"message": "I was', "code"), ('charged twice!"}', "code")], "blue")
    d.box(20, 120, 200, 110, [("questions", "bold"), ("choice  → one label", "small"), ("noul    → yes/no (0-1)", "small"), ("score   → a number", "small")], "amber")
    d.box(280, 70, 150, 90, [("Laya", "bold"), ("one forward pass", "small")], "green")
    d.arrow([(220, 60), (278, 100)], kind="blue"); d.arrow([(220, 175), (278, 130)], kind="blue")
    d.box(490, 20, 210, 210, [("answers", "bold"), ("category: billing  0.99", "code"), ("is_urgent: 0.95", "code"), ("anger: 2.65 / 3", "code"), ("output_tokens: 0", "small")], "box")
    d.arrow([(430, 115), (488, 115)], kind="green")
    return d.render()


@diagram
def s09_confidence():
    d = D("s09-confidence", 720, 230, "Trust Laya only when it is sure",
          "High confidence: act immediately. Low confidence: ask the LLM (or a human) instead of guessing.")
    d.box(20, 80, 140, 60, [("Laya answer", "bold"), ("label + confidence", "small")], "green")
    d.box(230, 80, 150, 60, [("confidence ≥ 0.70?", "bold")], "amber")
    d.arrow([(160, 110), (228, 110)], kind="blue")
    d.box(470, 20, 230, 56, [("Yes → trust it, act now", "bold"), ("route · block · reply", "small")], "green")
    d.box(470, 140, 230, 56, [("No → ask the LLM / a human", "bold"), ("don't guess", "small")], "red")
    d.arrow([(380, 95), (468, 50)], kind="green", label="yes", lx=420, ly=60); d.arrow([(380, 125), (468, 168)], kind="red", label="no", lx=420, ly=160)
    return d.render()
