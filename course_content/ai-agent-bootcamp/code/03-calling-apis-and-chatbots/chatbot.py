# chatbot.py - a command-line chatbot with a personality and memory
import json

from llm import LLMError, chat

PERSONAS = {
    "tutor": "You are a patient Python tutor for complete beginners. Use simple words, "
             "give one small example, and end with a short question to check understanding.",
    "pirate": "You are a friendly pirate. Answer helpfully, but speak like a pirate. Keep answers under 60 words.",
    "chai": "You are a cheerful chai-shop owner in Chennai. Give practical life advice in short, "
            "warm sentences, mixing a little Tamil flavour.",
}
MAX_TURNS = 10          # remember only the last 10 user+assistant pairs


def new_history(persona):
    return [{"role": "system", "content": PERSONAS[persona]}]


def trim(history):
    """Keep the system message + the most recent messages, so we never overflow the context window."""
    system, rest = history[0], history[1:]
    return [system] + rest[-MAX_TURNS * 2:]


def main():
    persona = "tutor"
    history = new_history(persona)
    print("Chatbot ready. Commands: /persona <tutor|pirate|chai>  /reset  /save  /quit")
    print(f"Current personality: {persona}\n")

    while True:
        text = input("You: ").strip()
        if not text:
            continue
        if text == "/quit":
            print("Bye!")
            break
        if text == "/reset":
            history = new_history(persona)
            print("(memory cleared)")
            continue
        if text == "/save":
            with open("chat.json", "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            print("(saved to chat.json)")
            continue
        if text.startswith("/persona"):
            name = text.split(maxsplit=1)[-1] if " " in text else ""
            if name in PERSONAS:
                persona = name
                history = new_history(persona)
                print(f"(personality is now '{persona}', memory cleared)")
            else:
                print("Choose one of:", ", ".join(PERSONAS))
            continue

        history.append({"role": "user", "content": text})
        try:
            reply, usage = chat(trim(history), temperature=0.7, max_tokens=250)
        except LLMError as error:
            history.pop()                        # forget the question that failed
            print("Bot (error):", error)
            continue
        history.append({"role": "assistant", "content": reply})
        print(f"Bot: {reply.strip()}")
        print(f"     [{usage.get('total_tokens', '?')} tokens]\n")


if __name__ == "__main__":
    main()
