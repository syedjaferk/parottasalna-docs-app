# agent.py - an AI agent built from scratch: think -> act -> observe -> repeat
import json

from llm import LLMError, call_api, chat
from tools import TOOL_FUNCTIONS, TOOL_SPECS

SYSTEM_PROMPT = (
    "You are Jarvis, a helpful assistant that can use tools. "
    "Use a tool whenever it helps: never guess maths, weather, the time or saved notes. "
    "You may use several tools one after another. When you have enough information, "
    "reply to the user in 1-3 short, friendly sentences."
)


class Agent:
    def __init__(self, max_steps=6, max_messages=12, verbose=True):
        self.max_steps = max_steps          # stopping condition: never loop forever
        self.max_messages = max_messages    # when history is longer than this, summarise the old part
        self.verbose = verbose
        self.messages = []                  # short-term memory: the recent conversation
        self.summary = ""                   # summary memory: a short note about older conversation

    # ------------------------------------------------------------------ helpers
    def log(self, text):
        if self.verbose:
            print(text)

    def system_message(self):
        text = SYSTEM_PROMPT
        if self.summary:
            text += "\n\nWhat you remember from earlier in this conversation:\n" + self.summary
        return {"role": "system", "content": text}

    def run_tool(self, name, raw_arguments):
        """Run one tool safely. ALWAYS returns text, even when something goes wrong."""
        function = TOOL_FUNCTIONS.get(name)
        if function is None:
            return f"Error: there is no tool called '{name}'. Available: {', '.join(TOOL_FUNCTIONS)}"
        try:
            arguments = json.loads(raw_arguments or "{}")
        except json.JSONDecodeError:
            return "Error: the arguments were not valid JSON."
        try:
            return str(function(**arguments))
        except TypeError as error:                       # wrong or missing arguments
            return f"Error: bad arguments for {name}: {error}"
        except Exception as error:                       # a bug inside the tool must not crash the agent
            return f"Error: {name} failed: {error}"

    # ------------------------------------------------------------------ the agent loop
    def ask(self, user_text):
        self.messages.append({"role": "user", "content": user_text})
        already_done = set()                              # (tool, arguments) pairs we have run this turn

        for step in range(1, self.max_steps + 1):
            self.log(f"\n[step {step}] THINK: asking the AI what to do next...")
            data = call_api({"messages": [self.system_message()] + self.messages,
                             "tools": TOOL_SPECS, "temperature": 0, "max_tokens": 400})
            message = data["choices"][0]["message"]
            # keep only the fields we need (some providers add extras that they later reject)
            clean = {"role": "assistant", "content": message.get("content")}
            if message.get("tool_calls"):
                clean["tool_calls"] = message["tool_calls"]
            self.messages.append(clean)

            calls = message.get("tool_calls")
            if not calls:                                 # no tool needed: this is the final answer
                self.log(f"[step {step}] DONE: final answer ready.")
                self.compress_memory()
                return (message.get("content") or "").strip()

            for call in calls:                            # ACT, then OBSERVE
                name = call["function"]["name"]
                raw = call["function"]["arguments"]
                self.log(f"[step {step}] ACT    : {name}({raw})")
                key = (name, raw)
                if key in already_done:                   # stopping condition: stop pointless repeats
                    result = "Error: you already ran this exact call. Use the earlier result and answer the user."
                else:
                    result = self.run_tool(name, raw)
                    already_done.add(key)
                self.log(f"[step {step}] OBSERVE: {result}")
                self.messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})

        self.compress_memory()
        return f"Sorry, I stopped after {self.max_steps} steps without finishing. Try a simpler request."

    # ------------------------------------------------------------------ summary memory
    def compress_memory(self):
        """If the conversation is long, turn the old part into a short summary."""
        if len(self.messages) <= self.max_messages:
            return
        # Cut at a 'user' message, so we never separate a tool request from its result.
        cut = max((i for i, m in enumerate(self.messages[:-4]) if m["role"] == "user"), default=0)
        if cut == 0:
            return
        old, self.messages = self.messages[:cut], self.messages[cut:]
        transcript = "\n".join(f"{m['role']}: {m.get('content') or '(used a tool)'}" for m in old)
        prompt = ("Summarise this conversation in under 80 words. Keep names, preferences, numbers and "
                  "anything the user asked you to remember.\n\nPrevious summary: "
                  f"{self.summary or '(none)'}\n\nConversation:\n{transcript}")
        try:
            self.summary, _ = chat([{"role": "user", "content": prompt}], temperature=0, max_tokens=150)
            self.log(f"(memory) older messages compressed into a summary: {self.summary.strip()[:100]}...")
        except LLMError:
            self.messages = old + self.messages       # could not summarise: keep everything


def main():
    agent = Agent()
    print("Jarvis agent ready. Type /memory to see its summary, /reset to forget, /quit to stop.\n")
    while True:
        text = input("You: ").strip()
        if not text:
            continue
        if text == "/quit":
            break
        if text == "/reset":
            agent = Agent()
            print("(agent reset)")
            continue
        if text == "/memory":
            print("Summary:", agent.summary or "(empty)", "\nRecent messages:", len(agent.messages))
            continue
        try:
            print("\nJarvis:", agent.ask(text), "\n")
        except LLMError as error:
            print("Jarvis (error):", error, "\n")


if __name__ == "__main__":
    main()
