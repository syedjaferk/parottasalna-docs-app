# Session 4 · Setup and clean-up: on_start, on_stop and test events

## The big idea

Some work should happen **once per user** (log in before shopping, log out afterwards) and some **once per
test** (create test data first, print a summary at the end). Locust gives you hooks for both:
`on_start` and `on_stop` on every user, and the `test_start` and `test_stop` events for the whole test.

**Everyday example:** a restaurant's day. The owner opens the shop and switches on the lights once
(`test_start`). Each waiter, when their shift starts, puts on an apron (`on_start`), serves tables all day (tasks), and
hands in the till at the end of the shift (`on_stop`). At closing time the owner counts the day's money once (`test_stop`).

```{raw} html
:file: ../diagrams/locust-lifecycle.html
```

## The hooks in action

```{literalinclude} ../code/04_lifecycle.py
:language: python
```

Two users for 3 seconds:

```bash
locust -f 04_lifecycle.py --headless -u 2 -r 2 -t 3s --only-summary --loglevel WARNING
```

```{literalinclude} ../code/04_lifecycle.out
:language: text
```

Reading the order:

1. `TEST START` appears **once**, before any user exists.
2. Each user prints its `on_start` line **once** when it is created. `user-2` starts a moment after `user-1`
   because the spawn rate is limited (`-r 2`), and the first user may already be running tasks by then.
3. The `task` lines interleave, since the users run side by side.
4. When the time limit hits, every user runs `on_stop` once, then `TEST STOP` appears **once**.

## When to use which

| Hook | Runs | Typical use |
|---|---|---|
| `events.test_start` | Once, before the load starts | Create test data, record the start time |
| `User.on_start` | Once per user | Log in, fetch a token, pick a product |
| `User.on_stop` | Once per user | Log out, delete the user's temporary data |
| `events.test_stop` | Once, after the load stops | Print or save a summary, clean up shared data |

Log-in is the classic case. If every user logged in inside a task, the login would be hit thousands of times;
in `on_start` it is hit once per user, like a real session (Session 5 does this with HTTP).

## Common mistakes

- **Putting a login in a normal `@task`.** It repeats on every loop and floods the login endpoint.
- **Doing slow setup in `on_start` for 1000 users.** The setup can become the load. Prepare shared data in
  `test_start` instead.
- **Assuming the order of users.** Users start and stop in an unpredictable order; do not depend on `user-1`
  finishing first.
- **Forgetting `on_stop` isn't guaranteed on a crash.** If the process is killed, the hook does not run. Do critical
  clean-up another way, too.
- **Using `__init__` for setup.** Locust-specific setup belongs in `on_start`; the constructor is used by Locust itself.

## Hands-on exercises

**Exercise 1.** Make `test_stop` print how many users ran, using a counter incremented in `on_start`.

<details class="solution"><summary>Solution</summary>

```python
started = 0

class Customer(User):
    def on_start(self):
        global started
        started += 1
    ...

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print(f"{started} users ran")
```

With `-u 2` it prints `2 users ran`.

</details>

**Exercise 2.** Which hook would you use to create a product that all users will then browse?

<details class="solution"><summary>Solution</summary>

`events.test_start`: it runs once, before the users, so the product exists when the first user arrives. Creating
it in `on_start` would make N copies.

</details>

**Exercise 3.** Why is a "log out" in `on_stop` better than at the end of a task?

<details class="solution"><summary>Solution</summary>

A task runs again and again, so it would log the user out in the middle of the session. `on_stop` runs once, when the
user's life ends.

</details>

## Practice

Take the **Session 4 quiz**. The original pages on `on_start`/`on_stop` and on `test_start`/`test_stop` are in the
reference section.
