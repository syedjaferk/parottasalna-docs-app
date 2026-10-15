# AI Agent Bootcamp: Build, Secure & Ship Your Own AI Agent

Welcome! In this course you will go from **"I know a little programming"** to **"I built, secured and
deployed my own AI agent"**. You don't need any AI background. We explain every word, show every
command for **Linux and Windows**, and build one small piece at a time.

:::{note}
**What is an AI agent, in one line?** A chatbot only *talks*. An **agent** also *does things*: it can
check the weather, do maths, read a file, or send you a message on Telegram, and it decides **by itself**
which of these to do and in what order.
:::

📣 Based on the [AI Agent Bootcamp](https://jarvis.parottasalna.com/) by Parottasalna.

## Where you will be at the end

```{raw} html
:file: diagrams/course-ladder.html
```

| Before the course | After the course |
|---|---|
| You can write simple loops and functions | You can build a real tool-using agent from scratch in Python |
| "AI" is a mystery | You can explain tokens, context window, temperature and hallucination |
| You've only chatted with ChatGPT | You call LLM APIs from code, handle errors and rate limits |
| You've never connected an app to Telegram | You run an agent that you chat with from your phone |
| You don't know how to make AI safe | You block prompt injection, route messages and control cost |

## What you will build

1. 🧠 **A custom Python agent** with the *think → act → observe* loop, tools and memory (Sessions 1-5).
2. 🤖 **A Hermes Agent**, a production-grade agent that remembers, learns skills, runs scheduled tasks and
   lives on Telegram (Sessions 6-8).
3. 🛡️ **A guarded Telegram support bot** that blocks prompt injections, triages messages and sends cheap
   questions to cheap models (Sessions 9-11).

## How to use this course

* **Do the [Setup](setup.md) first.** About 30 minutes, once.
* **Go in order.** Every session builds on the last.
* **Type the code yourself** (don't only copy). Typing is how your fingers and brain learn.
* **Do the tasks.** Each session ends with 3 tasks: *Warm-up*, *Build* and *Challenge*. Answers are hidden
  under "Answer" so you can try first.
* **Take the quiz** at the end of each session (see the **Quizzes** link in the portal).

## How every session page is laid out

Every session follows the same pattern, so you always know where to look:

1. **The big idea**: the concept in plain words with an everyday example.
2. **What you'll build** and **before you start** checklist.
3. **Concepts with diagrams**: pictures first, then words.
4. **Hands-on lab, step by step**: exact commands for 🐧 Linux and 🪟 Windows, with the output you should
   see. The code is explained **line by line**.
5. **Common mistakes** and a fix table.
6. **Tasks** (3 levels, with answers) and a **quiz**.
7. **Recap**: what you now know and what is next.

:::{important}
**AI answers vary.** The outputs shown are what a typical run looks like. When you run the code, the AI's
wording will differ a little. That is normal, and the *idea* stays the same.
:::

## What you need

* A laptop (Windows 10/11, Linux or macOS) with an internet connection and about 3 GB free disk space.
* Basic programming knowledge (what a variable, a loop and a function are). Session 1 refreshes these in Python.
* A free API key (Groq or OpenRouter) and a Telegram account. [Setup](setup.md) shows how.

```{toctree}
:maxdepth: 1
:caption: Start here

setup
glossary
troubleshooting
```

```{toctree}
:maxdepth: 1
:caption: Day 1 · Python, LLMs & Agent fundamentals

sessions/01-python-for-ai
sessions/02-how-llms-work
sessions/03-calling-apis-and-chatbots
sessions/04-structured-output-and-tools
sessions/05-build-an-agent
sessions/06-meet-hermes
```

```{toctree}
:maxdepth: 1
:caption: Day 2 · Hermes, Laya guardrails & capstone

sessions/07-hermes-deep-dive
sessions/08-telegram-gateway
sessions/09-system1-vs-system2
sessions/10-laya-guardrails
sessions/11-capstone
sessions/12-wrap-up
```
