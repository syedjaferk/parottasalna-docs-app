# Course map

This page shows the big picture: what you've learned so far and what's coming next.

## The building blocks of an agent

Building an agent is like building a robot helper. It needs a **brain** (the AI model), **hands**
(tools), a **library** to look things up in (RAG), a **memory**, a way to **give clean answers**
(typed output), and the ability to **do many things at once** (async). Each session adds one piece.

```{raw} html
:file: diagrams/map-agent.html
```

| Building block | In simple words | Session |
|---|---|---|
| Python foundations | the language everything is written in | [1](sessions/01-python-basics.md), [2](sessions/02-data-structures.md), [3](sessions/03-number-guessing-game.md) |
| The model | the "brain" that understands and writes text | [4](sessions/04-llm-terminology.md), [5](sessions/05-prompt-engineering.md) |
| Tools | "hands" that let the brain do real things | [6](sessions/06-tool-calling.md), [11](sessions/11-tools-and-mcp.md) |
| Knowledge (RAG) | a library the brain can look things up in | [7](sessions/07-rag.md) |
| Speed (async) | doing many slow things at the same time | [8](sessions/08-async.md) |
| Typed output | answers your program can trust and use | [9](sessions/09-data-validation.md) |
| Memory | remembering the conversation and the user | [10](sessions/10-memory.md) |

## Where this fits in the full track

This course follows the **AI Agent Engineering** track: 17 modules that go from Python basics to
shipping a production multi-agent system. Sessions are taught in the order that builds skills
fastest, so they don't always follow module numbers.

**Legend:** ✅ covered · 🟡 started (more to come) · ⏳ upcoming

| # | Module | Status | Sessions |
|---|---|---|---|
| 1 | Python essentials for AI engineers | 🟡 | 1, 2, 3, 8, 9 |
| 2 | AI & large language models | 🟡 | 4 |
| 3 | Prompt engineering | ✅ | 5 |
| 4 | Principles of AI applications (structured output, LCEL) | 🟡 | 9 |
| 5 | Tool calling & workflows | 🟡 | 6, 11 |
| 6 | Memory for AI agents | ✅ | 10 |
| 7 | Retrieval-augmented generation (RAG) | 🟡 | 7 |
| 8 | Building AI agents (ReAct, LangGraph) | 🟡 | 5 (ReAct), 8 |
| 9 | Multi-agent systems | ⏳ | |
| 10 | Model Context Protocol (MCP) | 🟡 | 11 |
| 11 | Production AI engineering (FastAPI, Docker, deployment) | ⏳ | FastAPI first appears in 8 |
| 12 | Evaluation & observability | ⏳ | |
| 13 | Advanced LangChain & LangGraph | ⏳ | |
| 14 | AI agent security & safety | ⏳ | |
| 15 | Multimodal & advanced agents | ⏳ | |
| 16 | Fine-tuning & model customization | ⏳ | |
| 17 | Advanced RAG, testing & frameworks | ⏳ | |
|   | **Capstone:** build & ship a production multi-agent platform | ⏳ | |

New session notes are added here after each class.
