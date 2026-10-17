# Session 3 · Different users and ordered tasks

## The big idea

Real traffic is a mix: most visitors browse, a few buy. Locust lets you define several **user classes**, each
with a **weight**, and Locust starts them in that proportion. When a user must do things **in order** (log in, pick a
product, check out), group the steps in a **SequentialTaskSet**.

**Everyday example:** a railway station at rush hour. Some people are just passing through (browsers), others
queue at the ticket counter (buyers). A buyer follows a fixed order: join the queue, tell the destination, pay,
take the ticket. You cannot pay before you have a destination.

```{raw} html
:file: ../diagrams/user-loop.html
```

## Two user types and a journey

```{literalinclude} ../code/03_users.py
:language: python
```

Run with 8 users:

```bash
locust -f 03_users.py --headless -u 8 -r 8 -t 4s --only-summary --loglevel WARNING
```

```{literalinclude} ../code/03_users.out
:language: text
```

What it shows:

- **Weights decide the mix.** With `weight = 3` and `weight = 1`, 8 users became 6 Browsers and 2 Buyers
  (`{'Browser': 6, 'Buyer': 2}`).
- **`SequentialTaskSet` runs tasks in the order written**, from the top, then repeats. Buyer 1 did *log in, pick
  product, check out*, again and again.
- **`self.interrupt()`** at the end of the last step leaves the task set and returns control to the user. The user
  then enters the journey again from the first step after its wait time.
- Inside a task set, `self.user` is the owning user, which is how the journey reads `self.user.buyer`.

## Choosing: User, TaskSet or SequentialTaskSet?

| You want | Use |
|---|---|
| One kind of user doing random actions | A `User` with several `@task` methods |
| Several kinds of users in a mix | Several `User` classes with `weight` |
| A fixed sequence of steps | `SequentialTaskSet` |
| A group of random actions to reuse in several users | A `TaskSet` |

You can also run one class alone from the command line: `locust -f 03_users.py Buyer`.

## Common mistakes

- **Putting a sequence in a plain `User`.** `@task` methods are picked at *random*, so "log in first" is not
  guaranteed. Use a `SequentialTaskSet`.
- **Forgetting `interrupt()` or `tasks = [...]`.** Without `tasks = [BuyerJourney]` the task set is never used,
  and without `interrupt()` the user just loops inside the journey forever (which is fine, but then it never
  returns to its other tasks).
- **Expecting the exact mix from tiny user counts.** With 3 users and weights 3:1 you cannot get 2.25 browsers;
  the mix only becomes accurate at larger counts.
- **Sharing state carelessly.** The module-level `steps` list is fine for a demo; with many users it is shared
  by all of them. Keep per-user data on `self`.
- **Counting tasks that never ran.** Check the stats table: a task that never appears never ran.

## Hands-on exercises

**Exercise 1.** With weights 3 and 1, how many of each user type do you get for 12 users?

<details class="solution"><summary>Solution</summary>

9 Browsers and 3 Buyers. (8 users gave 6 and 2 in the real run above; 12 follows the same 3:1 ratio.)

</details>

**Exercise 2.** Add a fourth step `rate_product` to the journey, to run after `check_out`. What else must you change?

<details class="solution"><summary>Solution</summary>

Tasks run in the order written, so write `rate_product` below `check_out`, and move `self.interrupt()` from
`check_out` to the new last step. The last task is the one that should end the journey.

</details>

**Exercise 3.** Run only `Buyer` users from the command line.

<details class="solution"><summary>Solution</summary>

```bash
locust -f 03_users.py Buyer --headless -u 2 -r 2 -t 3s --only-summary --loglevel WARNING
```

Naming a class after the file selects only that user class.

</details>

## Practice

Take the **Session 3 quiz**. The original pages *Simulating Multiple User Types* and *Sequential Task Set* are in
the reference section.
