# Session 3 · Project: Number Guessing Game

## The big idea

Now we build a real, complete program. The computer picks a secret number; you keep guessing; it
says "higher" or "lower" until you win or run out of tries. Winners go on a leaderboard.

The most important lesson isn't the game. It's **how to organise code**: break a big job into
small **functions** that each do one thing.

**Everyday example:** a restaurant kitchen. One cook makes the dosa, one makes the chutney, one
plates the food. Each does one job well, and the head chef just calls them in order. Our
`main()` is the head chef.

```{raw} html
:file: ../diagrams/s03-flow.html
```

## 1. Settings stored as data

The difficulty levels live in **one dictionary**:

```python
MODES = {
    "easy":   {"start": 1, "end": 20,  "attempts": 10},
    "medium": {"start": 1, "end": 50,  "attempts": 7},
    "hard":   {"start": 1, "end": 100, "attempts": 6},
}
```

Want an "expert" level? Add one line. You don't have to touch the game logic. (Writing the name in
CAPITALS is a Python habit meaning "this is a setting, don't change it while running".)

## 2. Functions: one job each

A **function** is a named mini-program. You define it once with `def`, then **call** it by name.

```python
def generate_secret_number(start: int, end: int):
    return random.randint(start, end)      # a random whole number from start to end

secret = generate_secret_number(1, 20)     # e.g. 14
```

- `start: int` is a **type hint**: a note saying "this should be a whole number". Python doesn't
  enforce it, but it helps people (and tools) understand the code. It becomes important in
  [Session 6](06-tool-calling.md), where AI tools are built from type hints.
- `return` sends the answer back to whoever called the function.

### Giving back several values at once

```python
def get_start_end_attempts(user_selected_mode: str):
    value = {}
    if user_selected_mode == "1":
        value = MODES["easy"]
    elif user_selected_mode == "2":
        value = MODES["medium"]
    elif user_selected_mode == "3":
        value = MODES["hard"]
    return value.get("start"), value.get("end"), value.get("attempts")

start, end, attempts = get_start_end_attempts("1")    # start=1, end=20, attempts=10
```

## 3. The game loop

```python
def play(secret_number, attempts):
    while attempts > 0:                          # keep going while tries are left
        user_guess = int(input("Enter your Guess : "))
        if user_guess == secret_number:
            print("Hurraaayyyy !! Congratulations You Won")
            return True                          # stop right now: we won
        elif user_guess > secret_number:
            print("Your guess is higher")
        else:
            print("Your guess is lower")
        attempts = attempts - 1                  # one try used up

    print("Dont Worry !!! You have lost the game. Better luck next time.")
    return False
```

**A sample game** (secret = 14, easy mode):

```text
Enter your Guess : 10
Your guess is lower
Enter your Guess : 16
Your guess is higher
Enter your Guess : 14
Hurraaayyyy !! Congratulations You Won
```

- `while attempts > 0:` repeats **as long as** the condition is true.
- `input()` waits for the user to type; `int()` turns the text `"14"` into the number `14`.
- `return True` ends the function immediately, even in the middle of the loop.

## 4. Saving to a file

```python
def collect_details_for_leaderboard():
    with open("leaderboard.txt", "a") as f:   # "a" = append (add to the end)
        name = input("Enter the name : ")
        f.write(name + "\n")                  # "\n" = new line
```

| Mode | What it does |
|---|---|
| `"a"` append | adds to the end and keeps old names ✅ |
| `"w"` write | **erases** the file first ⚠️ |
| `"r"` read | only reads |

`with open(...)` closes the file for you automatically when the block ends.

## 5. `main()` tells the story

```python
def main():
    show_greeting()
    show_options()
    user_selected_mode = get_user_option()
    start, end, attempts = get_start_end_attempts(user_selected_mode)
    secret_number = generate_secret_number(start, end)
    won = play(secret_number, attempts)
    if won:
        collect_details_for_leaderboard()
    play_again()
```

Read it out loud: *greet, show options, ask the mode, pick a secret, play, save if won, offer
another game*. You understand the whole program without reading a single function body. Aim for
this in everything you write, including agents.

## Common mistakes in the class version

:::{warning}
1. **It shows the answer!** `main()` has `print(secret_number)`, left over from testing. Delete it.
2. **Typing letters crashes it.** `int("abc")` raises a `ValueError`. Choosing option `4` also
   breaks it, because every setting becomes `None`.
3. **"Play again" calls `main()` from inside itself.** After very many games Python stops with
   `RecursionError`. A `while True:` loop is the safer way to repeat.
:::

## Try it yourself

1. Delete the debug `print`, and keep asking until the user types a real number.

   <details class="solution">
   <summary>Answer</summary>

   ```python
   def read_guess() -> int:
       while True:
           text = input("Enter your Guess : ")
           try:
               return int(text)          # works → leave the loop with the number
           except ValueError:
               print("Please type a whole number, like 7.")
   ```

   </details>

2. Replace `play_again()` with a loop inside `main()`:

   ```python
   def main():
       while True:
           # ... play one round ...
           if input("Play again? (Y/N) ").upper() != "Y":
               break      # leave the loop
   ```

3. Save how many attempts the winner needed, and show the top 5 at the start of each game.

## Full source

<details class="source">
<summary>game.py</summary>

```{literalinclude} ../code/03-number-guessing-game/game.py
:language: python
```

</details>

- {download}`Download game.py <../code/03-number-guessing-game/game.py>`
- {download}`Whiteboard: sets and the game design (open at excalidraw.com) <../code/03-number-guessing-game/whiteboard.excalidraw>`
