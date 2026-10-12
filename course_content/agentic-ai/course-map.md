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
| Workflows (LCEL) | snapping steps together, one after another or side by side | [12](sessions/12-lcel.md) |
| Human approval | a person signs off before risky actions | [13](sessions/13-human-in-the-loop.md) |

## The full syllabus

The course runs day by day in the order below. Each day builds on the ones before it.

**Legend:** ✅ taught in class · **Notes** links to pages in this course that already cover the topic. New notes are added after each class.

### Part 1 · Foundations: AI and Python

| Day | Topic | Status | Notes |
|---|---|---|---|
| 1 | Intro to AI: traditional vs generative AI, the AI hierarchy (AI > ML > DL > GenAI), GenAI vs agentic AI preview |  |  |
| 2 | Python basics: list, dictionary, tuple | ✅ | [Session 1](sessions/01-python-basics.md), [Session 2](sessions/02-data-structures.md) |
| 3 | Number guessing game (Python mini project) | ✅ | [Session 3](sessions/03-number-guessing-game.md) |
| 4 | AI/ML deep dive: core terminology, classification, regression, clustering, NLP, computer vision, GANs |  |  |
| 5 | Introduction to LLMs and AI terminology | ✅ | [Session 4](sessions/04-llm-terminology.md) |
| 6 | OOP in Python for AI engineers (with venv / poetry setup) |  |  |
| 7 | APIs and async Python |  | [Session 8](sessions/08-async.md) |
| 8 | Project structure and Pydantic |  | [Session 9](sessions/09-data-validation.md) |

### Part 2 · Prompt engineering

| Day | Topic | Status | Notes |
|---|---|---|---|
| 9 | Prompt engineering 101 | ✅ | [Session 5](sessions/05-prompt-engineering.md) |
| 10 | Prompt engineering 101: code implementation with LangChain | ✅ | [Session 5](sessions/05-prompt-engineering.md) |
| 11 | Advanced prompt engineering: CoT, ToT, ReAct, self-consistency, prompt chaining, prompt caching, injection / jailbreak defence, LLM-as-judge evaluation |  | [Session 5](sessions/05-prompt-engineering.md) |

### Part 3 · From AI apps to reliable AI systems

| Day | Topic | Status | Notes |
|---|---|---|---|
| 12 | AI apps vs AI agents: core differences |  |  |
| 13 | JSON mode and structured output with LangChain |  | [Session 9](sessions/09-data-validation.md) |
| 14 | Context engineering and prompt assembly |  |  |
| 15 | Building reliable AI systems: error handling, retries, fallbacks |  |  |

### Part 4 · Tools and workflows

| Day | Topic | Status | Notes |
|---|---|---|---|
| 16 | Function calling and custom tools with LangChain |  | [Session 6](sessions/06-tool-calling.md), [Session 11](sessions/11-tools-and-mcp.md) |
| 17 | Connecting tools to external APIs and databases |  | [Session 11](sessions/11-tools-and-mcp.md) |
| 18 | Human-in-the-loop integrations | ✅ | [Session 13](sessions/13-human-in-the-loop.md) |
| 19 | Sequential and parallel workflows (LCEL) | ✅ | [Session 12](sessions/12-lcel.md) |
| 20 | Conditional workflows and branching logic |  |  |

### Part 5 · Memory and context

| Day | Topic | Status | Notes |
|---|---|---|---|
| 21 | Short-term memory in LangChain (buffer, window) |  | [Session 10](sessions/10-memory.md) |
| 22 | Long-term memory and persistence (token, summary, semantic) |  | [Session 10](sessions/10-memory.md) |
| 23 | Conversation management and context window optimisation |  | [Session 10](sessions/10-memory.md) |
| 24 | Personalisation architectures for AI agents |  |  |

### Part 6 · RAG

| Day | Topic | Status | Notes |
|---|---|---|---|
| 25 | RAG as an agent tool: recap of chunking, embeddings and retrieval, reframed as a retriever tool |  | [Session 7](sessions/07-rag.md) |
| 26 | Advanced RAG: hybrid search, reranking, HyDE, multi-query retrieval, contextual retrieval |  |  |
| 27 | RAG evaluation: RAGAS (faithfulness, relevancy), comparing pipelines with numbers |  |  |

### Part 7 · Model Context Protocol (MCP)

| Day | Topic | Status | Notes |
|---|---|---|---|
| 28 | MCP fundamentals: architecture (host / client / server), primitives, transports, official servers |  | [Session 11](sessions/11-tools-and-mcp.md) |
| 29 | Building custom MCP servers and clients in Python (FastMCP), deploying a remote MCP server |  |  |

### Part 8 · Building agents

| Day | Topic | Status | Notes |
|---|---|---|---|
| 30 | Agent fundamentals: planning, reasoning and reflection (the agentic loop, ReAct paradigm) |  | [Session 5](sessions/05-prompt-engineering.md), [Session 11](sessions/11-tools-and-mcp.md) |
| 31 | Autonomous agent loops with LangChain (ReAct, built from scratch) |  |  |
| 32 | Failure recovery and human feedback in agents |  |  |
| 33 | Reliable agent design patterns |  |  |
| 34 | n8n AI agent workflows + RAGFlow no-code agentic RAG: code vs visual vs platform |  |  |

### Part 9 · Advanced agents

| Day | Topic | Status | Notes |
|---|---|---|---|
| 35 | Mem0 and memory taxonomy; plan-and-execute, ReWOO, Reflexion; Self-RAG, CRAG, adaptive RAG |  |  |
| 36 | Multi-agent systems: supervisor, hierarchical, network and swarm; A2A protocol, AutoGen GroupChat, CrewAI |  |  |
| 37 | Computer use and browser agents: Anthropic computer use, Playwright, E2B sandbox, safety implications |  |  |
| 38 | Agent evaluation and observability: trajectory vs end-result evaluation, LLM-as-judge, LangSmith / Langfuse / AgentOps |  |  |
| 39 | Guardrails, safety and cost: Guardrails AI, Presidio PII redaction, retry / fallback, prompt caching for cost |  |  |

### Part 10 · Putting it together

| Day | Topic | Status | Notes |
|---|---|---|---|
| 40 | Wiring RAG + tools + memory into one agent |  |  |
| 41 | Testing and debugging agent behaviour |  |  |
| 42 | **Capstone:** architect, build and deploy a production agentic AI system (FastAPI + Docker + AWS / Azure, MCP + multi-agent + memory + observability) |  |  |
