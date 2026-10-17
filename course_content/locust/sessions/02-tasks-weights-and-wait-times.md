# Session 2 · Users, tasks and wait times

## The big idea

A Locust test is made of **users**. A user is a Python class; its methods marked `@task` are the things it
does. Each user repeatedly picks a task, runs it, and then **waits** a little before the next one, like a real
person who reads a page before clicking. You control how often each task is picked (its **weight**) and how long users wait.

**Everyday example:** shoppers in a mall. Most people window-shop (browse) and a few actually buy. They do not
click every millisecond; they pause between actions. A test where every user hammers the server with no pause is
not a mall, it is a stampede.

```{raw} html
:file: ../diagrams/user-loop.html
```

## Tasks and weights

`@task` marks a method as a task. `@task(3)` gives it weight 3, so it is picked three times as often as a
task with weight 1. This locustfile has no HTTP in it; it just counts which task ran.

```{literalinclude} ../code/02_tasks.py
:language: python
```

Run it headless with 4 users for 6 seconds:

```bash
locust -f 02_tasks.py --headless -u 4 -r 4 -t 6s --only-summary --loglevel WARNING
```

`-u` is the number of users, `-r` how many to start per second, `-t` the run time. The line it printed:

```{literalinclude} ../code/02_tasks.out
:language: text
```

`browse` was picked about three times as often as `buy` (74% against a target of 75%). The exact counts change from run to run because
the choice is random; the ratio stays close.

## Wait times

The wait time decides the pause between tasks. There are three built-in kinds:

```{raw} html
:file: ../diagrams/wait-types.html
```

```{literalinclude} ../code/02_waits.py
:language: python
```

Each class was run alone for 6 seconds (`locust -f 02_waits.py ConstantUser -u 1 ...`). The task takes 0.3 s.

```{literalinclude} ../code/02_waits.out
:language: text
```

- **`constant(1)`**: waits 1 s *after* each task, so one round is 1.3 s long, giving about 5 runs in 6 seconds.
- **`between(0.5, 1.5)`**: a random pause, 1.3 s on average, so roughly the same count (a little random).
- **`constant_pacing(1)`**: starts a task every 1 s *including* its running time, so you get steady throughput (6 runs)
  however long the task takes. Use it when you want an exact rate.

No `wait_time` at all means no pause, which hammers the server as fast as it will go. Real users always pause.

## Common mistakes

- **Forgetting `wait_time`.** The users never pause and flood the server much harder than real people would.
- **Thinking `@task(3)` means "three times per second".** It is a *relative weight*, not a rate.
- **Reading `constant(1)` as "one task per second".** It waits one second *after* each task; use
  `constant_pacing` for a fixed rate.
- **Heavy work inside tasks.** Do not parse big files or call slow libraries in a task; it makes your load
  generator the bottleneck.
- **Expecting identical numbers each run.** Choices are random; compare ratios and trends.

## Hands-on exercises

**Exercise 1.** Add a third task `search` with weight 6 to `Visitor`. About what share of the tasks should it be?

<details class="solution"><summary>Solution</summary>

The weights are 3, 1 and 6, so `search` should be 6 / 10 = 60% of tasks, `browse` 30% and `buy` 10%. Run it and
compare the counts; they should be close to those shares.

</details>

**Exercise 2.** You want exactly 2 requests per second per user. Which wait time?

<details class="solution"><summary>Solution</summary>

`constant_pacing(0.5)`: a new task starts every 0.5 s regardless of how long the task takes (as long as the task
itself takes under 0.5 s).

</details>

**Exercise 3.** Change `PacedUser`'s task to sleep 1.5 s instead of 0.3. How many runs do you expect in 6 seconds? (Try it.)

<details class="solution"><summary>Solution</summary>

Pacing cannot start a task before the previous one finishes, so each round takes 1.5 s. Completions land at 1.5, 3.0, 4.5
and 6.0 seconds, so you expect 3 or 4 runs. When we ran it we measured **3**, because the fourth would finish exactly as
the test stopped. Locust cannot keep the rhythm when the task is slower than the pace.

</details>

## Practice

Take the **Session 2 quiz**. The original pages *@task decorator*, *task attribute* and *Understanding wait times*
are in the reference section.
