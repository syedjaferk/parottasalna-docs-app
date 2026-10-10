# Agentic AI

Welcome! This course takes you from **talking to an AI model** all the way to **building AI agents**
that look things up, remember, and use tools. Most of the time goes into **RAG** (Retrieval
Augmented Generation): the technique that lets an AI answer from *your* documents instead of
guessing.

:::{note}
**What is an AI agent, in one line?** A program where an AI model decides what to do next: which
document to read, which tool to call, what to remember. Then it gives you an answer.
:::

## How each session page works

1. **The big idea**: the concept in a few sentences, with an everyday example.
2. **How it works**: the key code from class, with what goes in and what comes out.
3. **Common mistakes**: what usually goes wrong, so you can avoid it.
4. **Try it yourself**: short exercises to do on your own computer.
5. **Full source**: every file from the live class, ready to read or download.

AI answers shown on these pages are what a typical run looks like. Yours may be worded
differently; the idea stays the same.

:::{tip}
New here? Do **[Setup](setup.md)** first, then follow the sessions in order.
:::

| Part | Sessions | You'll be able to… |
|---|---|---|
| 1 · Prompting | 1–2 | get reliable, well-formatted answers from a model |
| 2 · RAG | 3–12 | make a model answer from your own PDFs and data, quickly and accurately |
| 3 · Engineering | 13–14 | run many AI calls at once and get typed, trustworthy output |
| 4 · Agents | 15–16 | give an agent memory and tools, including over MCP |

```{toctree}
:maxdepth: 1
:caption: Getting started

setup
```

```{toctree}
:maxdepth: 1
:caption: Part 1 · Prompting

sessions/01-talking-to-an-llm
sessions/02-reasoning-prompts
```

```{toctree}
:maxdepth: 1
:caption: Part 2 · Retrieval Augmented Generation (RAG)

sessions/03-embeddings-and-vector-databases
sessions/04-sparse-and-hybrid-search
sessions/05-chunking
sessions/06-your-first-rag-pipeline
sessions/07-rag-with-n8n
sessions/08-metadata-filtering-and-reranking
sessions/09-semantic-caching
sessions/10-better-queries-and-smaller-context
sessions/11-advanced-retrievers
sessions/12-production-rag
```

```{toctree}
:maxdepth: 1
:caption: Part 3 · Engineering for AI apps

sessions/13-async-python
sessions/14-data-validation-with-pydantic
```

```{toctree}
:maxdepth: 1
:caption: Part 4 · Agents

sessions/15-agent-memory
sessions/16-tools-and-mcp
```
