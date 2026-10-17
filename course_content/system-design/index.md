# System Design

System design is the skill of turning a vague idea ("build something like TinyURL") into a
working plan: what it does, how big it must be, which pieces it needs and what you give up with
each choice. This course teaches that skill in small steps, with pictures and real numbers.

:::{note}
**Two ways to learn, side by side.** Read the chapters here to learn the ideas. Then open the
**[System Design playground](/system-design/)**: the problem is on the left and a guided,
question-by-question solution is on the right. You decide first, then it shows the correct
reasoning and moves you on.
:::

```{raw} html
:file: diagrams/framework.html
```

## How each chapter works

1. **The big idea** in plain words, with an everyday example.
2. **A picture** of the idea.
3. **Worked numbers** or a small example, so nothing stays abstract.
4. **Common mistakes** and what interviewers look for.
5. **Try it in the playground** once the concept is covered.

:::{tip}
Keep a notebook. For each chapter write one line: *"I would use X when Y, and it costs Z."*
That sentence is exactly what an interviewer wants to hear.
:::

```{toctree}
:maxdepth: 1
:caption: Foundations

sessions/01-interview-framework
sessions/02-back-of-envelope
sessions/03-api-and-data-model
```

```{toctree}
:maxdepth: 1
:caption: Building blocks

sessions/04-unique-ids
sessions/05-caching
sessions/06-scaling-data
sessions/07-networking-and-traffic
sessions/08-databases-cap-and-consistency
sessions/09-async-and-resilience
```

```{toctree}
:maxdepth: 1
:caption: Case studies

sessions/10-design-url-shortener
sessions/11-design-autocomplete
sessions/12-design-load-balancer
sessions/13-design-cdn
sessions/14-design-parking-garage
sessions/15-design-vending-machine
sessions/16-design-key-value-store
sessions/17-design-distributed-cache
sessions/18-design-authentication-system
sessions/19-design-upi-payments
```
