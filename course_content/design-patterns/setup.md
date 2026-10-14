# Setup

You only need **Python 3.10 or newer**. Every example uses the standard library and runs offline.

```bash
python3 --version
```

## Get the code

Each session's **Full source** section has every file, ready to copy or download. Save a file and
run it:

```bash
python3 1.singleton_new.py
```

The files are numbered in the order of the session: `0.` is the code **without** the pattern,
`1.` is the same job **with** it, and the later numbers show variations and the AI example.

## The AI examples

The AI examples (`*llm*`, `*rag*`, `*agent*`, `3.guardrails.py`, …) use a tiny **fake LLM** so they
run without an API key and without cost. They show the real provider code alongside it. To try a
real model, install LangChain's Groq package and set your key:

```bash
pip install langchain-groq
```

```bash
export GROQ_API_KEY=your-key-here
```

Then swap the fake for the real client, e.g. `ChatGroq(model="openai/gpt-oss-120b")`. The patterns
work exactly the same.

## Before you start

You should be comfortable with Python classes: `__init__`, methods, inheritance, and
`abc.ABC` with `@abstractmethod`. If `class Cat(Animal):` and `super().__init__()` look new,
revise classes and inheritance first.
