"""Diagrams for Sessions 4-6."""
from _dg import D, diagram


# ------------------------------------------------------------------ Session 4
@diagram
def s04_prompt_levels():
    d = D("s04-prompt-levels", 720, 240, "Three prompt techniques",
          "Each step makes the output more predictable: say what you want, limit the format, then show examples.")
    items = [("1 Instructions", ["Classify the", "sentiment."], "ghost", "→ long paragraph"),
             ("2 + Constraints", ["Reply with ONE", "word only."], "blue", "→ \"mixed\""),
             ("3 + Examples", ["\"Loved it\" → positive", "\"Awful\" → negative"], "green", "→ \"mixed\" (reliable)")]
    for i, (t, lines, k, out) in enumerate(items):
        x = 20 + i * 235
        d.text(x + 105, 20, t, "title")
        d.box(x, 35, 210, 90, [(ln, "code") for ln in lines], k)
        d.arrow([(x + 105, 125), (x + 105, 150)], kind="blue")
        d.box(x, 150, 210, 50, (out, "bold"), "box")
    d.text(360, 225, "More specific prompt  =  more reliable answer", "small")
    return d.render()


@diagram
def s04_structured():
    d = D("s04-structured", 720, 230, "Free text vs JSON",
          "Free text is for humans. JSON lets your code read each value directly.")
    d.box(20, 30, 300, 100, [("Free text", "bold"), ("\"Mostly positive, I'd say 7/10,", "small"), ("about food and service.\"", "small")], "ghost")
    d.box(400, 30, 300, 100, [("JSON", "bold"), ('{"sentiment": "mixed",', "code"), (' "score": 7, "topics": [...]}', "code")], "green")
    d.arrow([(322, 80), (398, 80)], kind="blue", label="ask for JSON", lx=360, ly=66)
    d.box(20, 160, 300, 50, ("your code must guess ✗", ""), "red")
    d.box(400, 160, 300, 50, ('result["score"]   → 7 ✓', "code"), "green")
    return d.render()


@diagram
def s04_tool_flow():
    d = D("s04-tool-flow", 720, 280, "How tool calling works",
          "The AI only asks. Your code runs the tool and sends back the result. Then the AI writes the final answer.")
    d.box(20, 20, 150, 60, [("You", "bold"), ("question", "small")], "blue")
    d.box(280, 20, 160, 60, [("Your code", "bold"), ("(Python)", "small")], "amber")
    d.box(550, 20, 150, 60, [("AI model", "bold"), ("(the brain)", "small")], "green")
    d.arrow([(170, 50), (278, 50)], kind="blue", label="1", lx=224, ly=36)
    d.arrow([(440, 40), (548, 40)], kind="blue", label="2 question + tool menu", lx=494, ly=24, lcls="small")
    d.arrow([(548, 70), (442, 70)], kind="green", label="3 'call get_weather'", lx=496, ly=88)
    d.box(280, 140, 160, 60, [("Real function", "bold"), ("get_weather()", "code")], "box")
    d.arrow([(360, 80), (360, 138)], kind="blue", label="4 run", lx=384, ly=110)
    d.arrow([(440, 190), (630, 190), (630, 82)], kind="blue", label="5 send result", lx=540, ly=206)
    d.arrow([(550, 62), (500, 62), (500, 245), (95, 245), (95, 82)], kind="green", dashed=True)
    d.text(300, 262, "6 final answer back to the user", "small")
    return d.render()


@diagram
def s04_tool_sequence():
    d = D("s04-tool-sequence", 720, 290, "The messages in a tool conversation",
          "The history grows: user, the AI's tool request, the tool result (role 'tool'), then the final assistant answer.")
    rows = [("user", "What is the weather in Chennai?", "blue"),
            ("assistant", "tool_calls: get_weather({city: chennai})", "amber"),
            ("tool", "Chennai: 29.4 °C, wind 11 km/h", "box"),
            ("assistant", "It's 29.4 °C in Chennai.", "green")]
    for i, (r, t, k) in enumerate(rows):
        y = 20 + i * 62
        d.box(20, y, 120, 46, (r, "code"), k)
        d.box(150, y, 420, 46, (t, "code" if i in (1, 2) else ""), "box")
        d.text(640, y + 23, ["you", "AI asks", "your code", "AI answers"][i], "small")
    d.text(360, 275, "tool_call_id links the 'tool' message to the AI's request", "small")
    return d.render()


# ------------------------------------------------------------------ Session 5
@diagram
def s05_agent_loop():
    d = D("s05-agent-loop", 720, 280, "The agent loop",
          "Think (ask the AI), Act (run a tool), Observe (read the result), and repeat until the AI can answer.")
    d.box(40, 110, 130, 60, [("Task", "bold"), ("from the user", "small")], "ghost")
    d.box(250, 30, 150, 60, [("THINK", "bold"), ("what next?", "small")], "amber")
    d.box(480, 110, 150, 60, [("ACT", "bold"), ("run a tool", "small")], "blue")
    d.box(250, 190, 150, 60, [("OBSERVE", "bold"), ("read the result", "small")], "green")
    d.arrow([(170, 130), (250, 70)], kind="blue")
    d.arrow([(400, 60), (480, 125)], kind="blue")
    d.arrow([(520, 170), (400, 215)], kind="blue")
    d.arrow([(250, 220), (200, 220), (200, 70), (248, 62)], kind="green", dashed=True)
    d.box(540, 220, 160, 44, [("Final answer", "bold")], "green")
    d.arrow([(400, 45), (540, 45), (620, 45), (620, 218)], kind="green", label="no tool needed → done", lx=560, ly=32)
    return d.render()


@diagram
def s05_three_kinds():
    d = D("s05-three-kinds", 720, 230, "Chatbot, workflow, agent",
          "A chatbot just replies. A workflow follows steps you wrote. An agent decides the steps itself.")
    cols = [("Chatbot", ["question", "↓", "reply"], "ghost"), ("Workflow", ["step 1 → step 2", "→ step 3", "(fixed by you)"], "blue"),
            ("Agent", ["decides:", "tool? which? again?", "(chosen by the AI)"], "green")]
    for i, (t, lines, k) in enumerate(cols):
        x = 20 + i * 235
        d.text(x + 105, 18, t, "title")
        d.box(x, 30, 210, 130, [(ln, "code" if j else "bold") for j, ln in enumerate(lines)], k)
    d.text(125, 185, "predictable", "small"); d.text(360, 185, "predictable", "small"); d.text(595, 185, "flexible, needs guard rails", "small")
    d.arrow([(40, 205), (680, 205)], kind="blue")
    d.text(60, 222, "less freedom", "small"); d.text(650, 222, "more freedom", "small")
    return d.render()


@diagram
def s05_parts():
    d = D("s05-parts", 720, 250, "The four parts of an agent",
          "Brain (LLM), tools, memory, and the loop with its limits.")
    d.box(250, 90, 220, 70, [("AGENT LOOP", "bold"), ("+ safety limits", "small")], "blue")
    d.box(20, 20, 190, 70, [("Brain", "bold"), ("the LLM decides", "small")], "amber")
    d.box(510, 20, 190, 70, [("Tools", "bold"), ("functions it can call", "small")], "green")
    d.box(20, 160, 190, 70, [("Memory", "bold"), ("messages · summary · notes", "small")], "box")
    d.box(510, 160, 190, 70, [("You", "bold"), ("approvals & limits", "small")], "ghost")
    for p in [((210, 55), (252, 105)), ((510, 55), (468, 105)), ((210, 195), (252, 148)), ((510, 195), (468, 148))]:
        d.arrow(list(p), kind="blue", head=False)
    return d.render()


@diagram
def s05_memory():
    d = D("s05-memory", 720, 260, "Three kinds of agent memory",
          "Short-term keeps recent messages; summary squeezes old ones; notes live in a file and survive restarts.")
    d.box(20, 30, 210, 160, [("Short-term", "bold"), ("last ~12 messages", "small"), ("exact words", "small"), ("lost when cut", "small")], "blue")
    d.box(255, 30, 210, 160, [("Summary", "bold"), ("old chat → 80 words", "small"), ("names, preferences", "small"), ("detail is lost", "small")], "amber")
    d.box(490, 30, 210, 160, [("Notes file", "bold"), ("notes.txt", "code"), ("survives restart", "small"), ("agent must choose to save", "small")], "green")
    d.arrow([(230, 110), (253, 110)], kind="blue", label="too long", lx=242, ly=95, lcls="small")
    d.text(360, 225, "In the prompt every time          ·          Written to disk", "small")
    return d.render()


@diagram
def s05_stops():
    d = D("s05-stops", 720, 220, "Three ways an agent stops",
          "It finishes normally, hits the step limit, or is stopped from repeating the same call.")
    d.box(20, 40, 210, 110, [("1  Finished", "bold"), ("no tool needed →", "small"), ("final answer", "small")], "green")
    d.box(255, 40, 210, 110, [("2  max_steps", "bold"), ("after 6 steps →", "small"), ("stop and apologise", "small")], "amber")
    d.box(490, 40, 210, 110, [("3  No repeats", "bold"), ("same call twice →", "small"), ("refuse, say so", "small")], "red")
    d.text(360, 185, "Without limits an agent can loop forever and run up your bill", "small")
    return d.render()


# ------------------------------------------------------------------ Session 6
@diagram
def s06_compare():
    d = D("s06-compare", 720, 260, "Your agent vs Hermes",
          "Same loop inside. Hermes adds many more tools, long-term memory, skills, scheduling, messaging and safety features.")
    d.box(20, 20, 300, 210, [], "box")
    d.text(170, 40, "YOUR AGENT (bicycle)", "title")
    for i, t in enumerate(["5 tools", "messages + summary + notes", "runs in your terminal", "you wrote every line"]):
        d.box(40, 55 + i * 42, 260, 34, (t, ""), "blue")
    d.box(400, 20, 300, 210, [], "box")
    d.text(550, 40, "HERMES (motorcycle)", "title")
    for i, t in enumerate(["terminal · files · web · browser", "persistent memory + skills", "scheduler + Telegram gateway", "approvals & safety blocklist"]):
        d.box(420, 55 + i * 42, 260, 34, (t, ""), "green")
    d.arrow([(320, 125), (398, 125)], kind="blue", label="same loop", lx=359, ly=108)
    return d.render()


@diagram
def s06_hermes_parts():
    d = D("s06-hermes-parts", 720, 270, "Inside Hermes",
          "You talk to Hermes from the terminal or a chat app. It uses a model, tools, memory and skills, and can run jobs on a schedule.")
    d.box(20, 20, 150, 60, [("Terminal", "bold"), ("hermes", "code")], "blue")
    d.box(20, 100, 150, 60, [("Telegram", "bold"), ("hermes gateway", "code")], "blue")
    d.box(20, 180, 150, 60, [("Scheduler", "bold"), ("hermes cron", "code")], "blue")
    d.box(250, 70, 200, 130, [("HERMES CORE", "bold"), ("agent loop", "small"), ("approvals", "small")], "amber")
    for y in (50, 130, 210):
        d.arrow([(170, y), (248, 135)], kind="blue")
    d.box(530, 20, 170, 56, [("Model", "bold"), ("Groq · OpenRouter · Ollama", "small")], "green")
    d.box(530, 94, 170, 56, [("Tools", "bold"), ("files · terminal · web", "small")], "green")
    d.box(530, 168, 170, 56, [("Memory + Skills", "bold"), ("~/.hermes", "code")], "green")
    for y in (48, 122, 196):
        d.arrow([(450, 135), (528, y)], kind="green")
    return d.render()


@diagram
def s06_folders():
    d = D("s06-folders", 720, 240, "Where Hermes keeps things",
          "Everything lives in one folder: settings in config.yaml, secrets in .env, memory, skills, logs.")
    d.box(20, 20, 680, 200, [], "box")
    d.text(130, 42, "~/.hermes/   (Windows: %LOCALAPPDATA%\\hermes\\)", "code")
    d.els[-1] = d.els[-1].replace('text-anchor="middle"', 'text-anchor="start"').replace('x="130"', 'x="40"')
    items = [("config.yaml", "settings", "blue"), (".env", "secrets 🔒", "red"), ("memories/", "MEMORY.md USER.md", "green"),
             ("skills/", "SKILL.md recipes", "green"), ("logs/", "what happened", "ghost"), ("state.db", "past sessions", "ghost")]
    for i, (n, t, k) in enumerate(items):
        x = 40 + (i % 3) * 220
        y = 65 + (i // 3) * 75
        d.box(x, y, 200, 60, [(n, "code"), (t, "small")], k)
    return d.render()
