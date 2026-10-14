# Design Patterns in Python

Welcome! This course covers the 18 design patterns you'll meet most often in real Python code, one
session each. Every session starts from code **without** the pattern, shows the problem, then fixes
it **with** the pattern, and ends with an example from AI apps (LLMs, RAG and agents).

:::{note}
**What is a design pattern, in one line?** A well-known, named solution to a problem that keeps
coming back in software, like "only one of these may exist" or "add a feature without editing the
class". Knowing the name lets you spot the problem faster and explain your design in one word.
:::

```{raw} html
:file: diagrams/map-patterns.html
```

## How each session works

1. **The big idea**: the problem in plain words, with an everyday example.
2. **Without the pattern**: code that works but hurts as it grows.
3. **With the pattern**: the same job, done cleanly, with a diagram.
4. **The pattern + AI**: where it shows up in LLM, RAG and agent code.
5. **Common mistakes** and **hands-on exercises**, with solutions you can reveal.
6. **Practice**: a quiz and a flashcard deck for the session.

:::{tip}
New here? Do **[Setup](setup.md)** first. **[Patterns at a glance](patterns-at-a-glance.md)**
compares all 18 side by side and ends with a "which pattern fits?" quiz. Try it after you finish
each family.
:::

:::{important}
**Don't force patterns.** Every pattern adds a little structure. Use one when you feel the pain it
fixes (the same `if/elif` in five places, a class that keeps growing), not just because it has a
name. Each session's *Common mistakes* tells you when *not* to use it.
:::

```{toctree}
:maxdepth: 1
:caption: Getting started

setup
patterns-at-a-glance
```

```{toctree}
:maxdepth: 1
:caption: Creational · how objects are made

sessions/01-singleton-pattern
sessions/02-factory-method-pattern
sessions/03-abstract-factory-pattern
sessions/04-builder-pattern
sessions/05-prototype-pattern
```

```{toctree}
:maxdepth: 1
:caption: Structural · how objects fit together

sessions/06-adapter-pattern
sessions/07-decorator-pattern
sessions/08-facade-pattern
sessions/09-proxy-pattern
sessions/10-composite-pattern
sessions/11-bridge-pattern
sessions/12-flyweight-pattern
```

```{toctree}
:maxdepth: 1
:caption: Behavioural · how objects work together

sessions/13-strategy-pattern
sessions/14-observer-pattern
sessions/15-command-pattern
sessions/16-state-pattern
sessions/17-template-method-pattern
sessions/18-chain-of-responsibility-pattern
```
