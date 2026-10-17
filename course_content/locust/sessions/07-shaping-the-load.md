# Session 7 · Shaping the load: step tests and logging

## The big idea

A single fixed number of users answers "does it survive 500 users?" A **step test** answers a better question:
"at which load do things start to go wrong?" It adds a few users every few seconds, so you can see response time and
failures change at each step. In Locust you write this as a **LoadTestShape** class. Alongside it, good **logging**
tells you what the test was doing at each moment.

**Everyday example:** a doctor's treadmill test. The speed is raised a notch every minute while a monitor shows the
heart rate. You learn *at which speed* trouble starts, which a single steady run could never tell you.

```{raw} html
:file: ../diagrams/step-shape.html
```

## A step shape

```{literalinclude} ../code/07_shape.py
:language: python
```

Locust calls `tick()` about once a second. It returns `(users, spawn_rate)` for that moment, or `None` to end the
test. This shape adds 2 users every 3 seconds: 2, 4, then 6 users, and ends after 9 seconds. There is no `-u` or `-t`
on the command line, because the shape controls both.

```bash
locust -f 07_shape.py --headless --host http://127.0.0.1:8765 --only-summary --loglevel WARNING
```

```{literalinclude} ../code/07_shape.out
:language: text
```

The `step` lines are the shape's own print statements: a simple, useful form of logging that marks where each stage starts.
The `Aggregated` line is the whole-run total (242 requests in this run, none failed).

## Reading a step test

In a real test, watch the charts (or the stats) per step:

- If response time stays flat from step to step, the service has headroom.
- If it **climbs sharply** at a step, you have found a limit. Note the user count at that step.
- If **failures appear**, the service has passed its breaking point.

This tiny local shop never slows down at 6 users, so the numbers stay flat. Against a real service, the step where the
numbers bend is the finding.

## Logging that helps

- **`print`** is fine for short experiments, as above.
- **Command-line flags** control Locust's own logging. We used `--loglevel WARNING` to hide routine messages;
  `--loglevel DEBUG` shows everything, and `--logfile test.log` writes the log to a file.
- **Python's `logging` module** works inside your locustfile: create `logging.getLogger("shop")` and log interesting events,
  such as the reason for a failed check. Add the user's name or id so you can follow a single user.
- **Keep it quiet under load.** Thousands of users each writing a line per request makes the log itself slow
  your test.

## Common mistakes

- **Using both a shape and `-u`/`-t`.** The shape wins; the other flags are ignored.
- **Making steps too short.** Give each step long enough for the numbers to settle (tens of seconds in real tests, not 3).
- **Jumping too many users per step.** Small steps let you see exactly where trouble begins.
- **Forgetting to return `None`.** Without it the test never ends.
- **Logging every request in a big test.** The output becomes noise and slows the generator.

## Hands-on exercises

**Exercise 1.** Change the shape to add 5 users every 4 seconds for 12 seconds. What are the user counts?

<details class="solution"><summary>Solution</summary>

```python
step_time = 4
step_users = 5
total_time = 12
```

Steps: 5 users (0 to 4 s), 10 users (4 to 8 s), 15 users (8 to 12 s).

</details>

**Exercise 2.** The shape returns `step * self.step_users, self.step_users`. What does each number mean?

<details class="solution"><summary>Solution</summary>

The first is the **total number of users wanted now** (2, then 4, then 6). The second is the **spawn rate**, how many
users Locust may start per second to get there.

</details>

**Exercise 3.** You see response times jump from 200 ms to 2 s between the 400-user and 600-user steps. What do you report?

<details class="solution"><summary>Solution</summary>

"Response times degrade between 400 and 600 concurrent users." Then repeat with smaller steps (e.g. every 25 users from 400)
to narrow it down, and check the server's CPU, memory and database during those steps to find the cause.

</details>

## Practice

Take the **Session 7 quiz**. The original pages *Iterative Load Testing with Step Size* and *Enhancing Your Locust
Tests with Custom Logging* are in the reference section.
