# Chapter 1 · The interview framework

## The big idea

A system design question is deliberately vague: *"Design TinyURL."* Nobody expects you to know the
answer. They want to see **how you think** when the problem is open. The fix is a repeatable
routine, so you never stare at a blank whiteboard.

**Everyday example:** an architect asked to "build a house". They do not start laying bricks. They ask
how many people will live there, what the budget is and where the plot is. Then they sketch rooms,
then pipes and wiring, then check what could go wrong. You do the same with software.

:::{admonition} In plain words
:class: tip
Ask first, count second, sketch third, go deep on the hard part, then look for what can break and say
what you gave up. Say your reasoning out loud the whole time.
:::

```{raw} html
:file: ../diagrams/framework.html
```

## The seven steps

### 1. Clarify requirements (3-5 min)

Do not touch the whiteboard yet. Ask:

- **Functional:** what are the core features, and what is explicitly *out* of scope?
  For a URL shortener: create and redirect, maybe analytics, probably not user accounts.
- **Non-functional:** latency, availability versus consistency, durability, security.
- **Users:** who uses it, from where, and how many?

Then **state your assumptions out loud** so the interviewer can correct you early.

### 2. Estimate scale (2-3 min)

Rough math shapes every later choice: users to requests per second, read/write ratio, storage per
record times records per year, bandwidth. You only need to know whether you are at 100 requests per
second or 100,000, because that changes the architecture. See [chapter 2](02-back-of-envelope.md).

### 3. Define the API and data model (3-5 min)

List the main endpoints with inputs and outputs, then the core entities. Pick a store from the
**access pattern**. See [chapter 3](03-api-and-data-model.md).

### 4. Sketch the high-level design (5-10 min)

Start simple and end-to-end: client, load balancer, app servers, database. Walk **one request** through
the whole path for each core use case. Get a working design on the board before optimising.

### 5. Deep dive into the hard parts (10-15 min)

Pick what is genuinely hard for *this* problem and go deep: scaling the data layer, caching,
async processing, consistency, unique IDs, rate limiting, fan-out.

### 6. Address reliability and bottlenecks (5 min)

Walk the design looking for weak points: single points of failure, what happens when a node or zone
dies, retries and timeouts, backups, monitoring.

### 7. Discuss trade-offs and wrap up

Every choice costs something. Say what you chose, what you gave up and what would make you change it.

## Habits that matter most

- **Think out loud.** The reasoning is worth more than the diagram.
- **Start simple, then evolve.** Do not open with Kafka and microservices.
- **Tie every decision to a requirement or a number** from steps 1 and 2.
- **Name trade-offs** instead of presenting choices as obviously right.
- **Drive, but check in:** "Should I go deeper on storage or on the read path?"
- **Manage time.** Spending 25 minutes on requirements and estimates is a common failure.

## Common mistakes

- Jumping straight to a favourite technology.
- Designing for a million users when the numbers say ten thousand.
- Never saying what is **out of scope**.
- Describing components without walking a request through them.
- Calling a choice "best" without naming its cost.

## Try it yourself

1. You are asked to "design a parking garage". Write five clarifying questions you would ask before drawing anything.
2. Name the seven steps of the framework in order, and say which one produces the numbers.
3. An interviewer says "just add a cache". What do you reply?

<details class="solution"><summary>Answers</summary>

1. Examples: which vehicle types? how many floors and entrances? how is the fee calculated? must the design handle many garages? what is out of scope (reservations, hardware)?
2. Clarify requirements, estimate scale (this step produces the numbers), API and data model, high-level design, deep dive, reliability, trade-offs and wrap-up.
3. "A cache helps if the numbers show a read-heavy load. Here is the read rate, the hit rate I expect, and what it costs in staleness and invalidation. If reads were low I would skip it."

</details>

:::{admonition} Try it in the playground
:class: important
The [TinyURL problem](/system-design/tinyurl/) follows exactly these seven steps. Start with step 1 and
see whether your own list of requirements matches the one an interviewer would hope for.
:::

:::{admonition} Next
:class: important
The framework starts with numbers. Next: [back-of-envelope estimation](02-back-of-envelope.md).
:::
