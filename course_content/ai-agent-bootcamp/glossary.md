# Glossary

Every word you meet in the course, in plain language. Use `Ctrl + F` to find a word.

## A

**Agent**
: A program that uses an AI model to decide **what to do next**, uses **tools**, looks at the results and repeats until the job is done. (Think → Act → Observe.) → [Session 5](sessions/05-build-an-agent.md)

**API** (Application Programming Interface)
: A "door" on a website that **programs** can knock on to get data (usually JSON). → [Session 1](sessions/01-python-for-ai.md)

**API key**
: A secret text that proves who you are to an API, like a library card number. Keep it in `.env`, never in code.

**Assistant (role)**
: The role used for the AI's own messages in a chat. → [Session 3](sessions/03-calling-apis-and-chatbots.md)

**Allow-list**
: A list of user ids that are allowed to use your bot. Everyone else is refused. → [Session 8](sessions/08-telegram-gateway.md)

## B

**Backoff (exponential)**
: Waiting longer after each failed try (1 s, 2 s, 4 s ...) before trying again, so you don't hammer a busy server.

**Bot token**
: The password of a Telegram bot, given by BotFather. Whoever has it controls the bot.

**BotFather**
: Telegram's official bot that creates other bots for you (`/newbot`).

## C

**Chatbot**
: A program that only **talks**. An agent can also **act**.

**Choice (Laya question)**
: A question where the model must pick **one label** from a list. → [Session 9](sessions/09-system1-vs-system2.md)

**Confidence**
: How sure a classifier is about its answer (a probability from 0 to 1). We act on high confidence and ask a bigger model or a human when it's low.

**Context window**
: The most text (in tokens) an LLM can look at **in one go**: instructions, history and the answer it is writing. → [Session 2](sessions/02-how-llms-work.md)

**Cron**
: The Linux scheduler that runs commands at set times. Windows has **Task Scheduler**. → [Session 11](sessions/11-capstone.md)

## D

**Defence in depth**
: Using several cheap safety layers so an attack must beat all of them. → [Session 10](sessions/10-laya-guardrails.md)

**Dictionary (dict)**
: A Python collection of **label → value** pairs, like `{"name": "Asha"}`.

## E

**`.env` file**
: A text file of secrets (like `LLM_API_KEY=...`) kept next to your code but **never** uploaded.

**Evals**
: Automated tests that score an AI system on your own examples, so you can tell whether a change really helped.

## F

**f-string**
: A Python string with an `f` in front where `{variables}` are filled in: `f"Hello {name}"`.

**Few-shot prompting**
: Showing the AI two or three solved examples inside the prompt.

**Function**
: A named, reusable recipe in code. Every agent **tool** is a function.

## G

**Gateway**
: A bridge that connects a chat app (Telegram, Discord...) to your agent. In Hermes it also runs scheduled jobs. → [Session 8](sessions/08-telegram-gateway.md)

**Git / GitHub**
: Git remembers every version of your project; GitHub is a website that stores it online.

**Guardrail (guard)**
: A check that runs **before** the main AI to block or flag risky messages.

## H

**Hallucination**
: A confident answer that sounds right but is false, because the model guesses likely text.

**Hermes Agent**
: An open-source production agent (by Nous Research) with tools, memory, skills, scheduling and messaging. → [Session 6](sessions/06-meet-hermes.md)

**Human in the loop**
: A person must approve risky actions before the agent does them.

## J

**Jailbreak**
: A message that tries to make an AI ignore its rules.

**JSON**
: A text format that looks like a Python dictionary. Used by almost every web API. (`dumps` / `loads`.)

**JSON mode**
: A request option that forces the AI's reply to be valid JSON.

## L

**Laya**
: A small open-source "decision model" that answers typed questions (choice, yes/no, score) with probabilities in one quick pass. → [Session 9](sessions/09-system1-vs-system2.md)

**LLM** (Large Language Model)
: The AI "brain" behind chatbots and agents: a very good next-word guesser.

**Long polling**
: Asking Telegram for updates; it keeps the request open until a message arrives. → [Session 8](sessions/08-telegram-gateway.md)

## M

**MCP** (Model Context Protocol)
: A standard way to plug tools into agents. (A topic for after the course.)

**Memory (agent)**
: Short-term (recent messages), summary (compressed old chat) and notes/persistent (files or a database).

**Model routing**
: Sending easy messages to a cheap model and hard ones to a strong model.

## N

**Noul (Laya question)**
: A yes/no question answered as a probability from 0.0 to 1.0.

## O

**OpenAI-compatible API**
: The common way to talk to AI providers. Groq, OpenRouter and Ollama all use it, so one code works with all.

**Ollama**
: A program that runs AI models on your own computer.

## P

**Parameters (model)**
: The internal numbers of a model. "8B" means about 8 billion of them.

**Prompt**
: The text you send to an AI. A **system prompt** sets rules; a **user prompt** is the question.

**Prompt injection**
: Hiding instructions inside text so the AI obeys an attacker. → [Session 10](sessions/10-laya-guardrails.md)

## R

**RAG** (retrieval-augmented generation)
: Letting the AI search your documents and answer from them. (A topic for after the course.)

**Rate limit**
: A cap on how many requests or tokens you may use per minute or day. The API answers **429** when you pass it.

**`requests`**
: The Python library for calling web APIs.

**Role**
: Who says a message: `system`, `user`, `assistant` or `tool`.

## S

**Score (Laya question)**
: A question answered with a number on a scale, like anger from 0 to 3.

**Skill (Hermes)**
: A markdown file (`SKILL.md`) with instructions the agent follows. → [Session 7](sessions/07-hermes-deep-dive.md)

**SQLite**
: A database that lives in one file and comes built into Python.

**Status code**
: A number in an API reply: `200` OK, `401` bad key, `404` not found, `429` too many requests, `500` server problem.

**System 1 / System 2**
: Fast automatic thinking vs slow careful thinking. In AI: a small classifier vs an LLM.

## T

**Temperature**
: A dial for how adventurous the model's word choice is. Low = steady, high = creative.

**Token**
: A small piece of text (about ¾ of an English word). Models read, limit and charge in tokens.

**Tool / tool calling**
: A function the AI can **ask** your code to run. The AI never runs it itself. → [Session 4](sessions/04-structured-output-and-tools.md)

## V

**Virtual environment (venv)**
: A private box of packages for one project.

## W

**Webhook**
: A way for a service to call **your** web address when something happens (the opposite of polling).

**Workflow**
: Steps you wrote in code in a fixed order. Cheaper and more predictable than an agent.

## Y

**YAML**
: A readable settings format (like `config.yaml`). It needs **spaces, never tabs**, and exact indentation.
