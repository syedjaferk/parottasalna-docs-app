# Session 12 · Project: the number guessing game

📖 Based on the blog posts [Build a game where the user guesses a randomly generated number](https://learn.parottasalna.com/blog/build-a-game-where-the-user-guesses-a-randomly-generated-number/)
and [Python Mini Projects Ideas](https://learn.parottasalna.com/blog/python-mini-projects-ideas/).

## The big idea

Time to put everything together: variables, `input()`, conditions, loops, functions, lists and
files. You'll build the same game four times, each version adding one feature:

| Version | Adds | You practise |
|---|---|---|
| A · Simple | guess 1–100, too high / too low | `random`, `while`, `if/elif/else`, `try/except` |
| B · Levels | difficulty, limited attempts, a hint, play again | functions with several return values |
| C · Leaderboard | top-10 scores saved to a file | files, lists of tuples, `sorted` with a key |
| D · Window | a Tkinter GUI | classes and event handlers (a preview) |

```{raw} html
:file: ../diagrams/s12-game.html
```

## Plan before you code

1. **Welcome** the player and explain the rules.
2. **Pick** a secret number: `random.randint(1, 100)` (both ends included).
3. **Ask** for a guess, and keep asking until it's a valid whole number.
4. **Compare**: too low, too high, or correct.
5. **Repeat** until correct (or out of attempts).
6. **Finish**: congratulate and show the number of attempts.

## Version A · the simple game

The heart of the game is one `while True` loop that only ends with `break` when the guess is right:

```py
while True:
    attempts += 1
    guess = get_user_guess()
    if guess < secret_number:
        print("Too low! Try again.")
    elif guess > secret_number:
        print("Too high! Try again.")
    else:
        print(f"Congratulations! You guessed the number in {attempts} attempts.")
        break
```

### Validating input

`int(input())` crashes if the player types "abc". Catch the error and **ask again in a loop**:

```py
def get_user_guess():
    # Keep asking until the input is a whole number
    while True:
        try:
            return int(input("Enter your guess: "))
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
```

:::{note}
The blog's version called `get_user_guess()` again inside `except` but threw away the result, so a
bad input followed by a good one crashed with `UnboundLocalError`. A loop is simpler and can't run
out of stack.
:::

A real session (secret number 18):

```text
Welcome to the Number Guessing Game!
I'm thinking of a number between 1 and 100.
Enter your guess: 50
Too high! Try again.
Enter your guess: abc
Invalid input. Please enter a valid integer.
Enter your guess: 10
Too low! Try again.
Enter your guess: 18
Congratulations! You guessed the number in 3 attempts.
```

## Version B · levels, attempts, hints, play again

| Level | Range | Attempts |
|---|---|---|
| 1 · Easy | 1–50 | 10 |
| 2 · Medium | 1–100 | 7 |
| 3 · Hard | 1–1000 | 5 |

A function returns all three settings at once (as a tuple, [Session 8](08-tuples.md)):

```py
def get_min_max_total_attempts(difficulty):
    if difficulty == 1:
        min_value, max_value, max_attempts = 1, 50, 10
    elif difficulty == 2:
        min_value, max_value, max_attempts = 1, 100, 7
    else:
        min_value, max_value, max_attempts = 1, 1000, 5
    return min_value, max_value, max_attempts
```

One input helper checks both "is it a number?" and "is it in range?", and is reused for the menu
**and** the guesses:

```py
def get_valid_number(prompt, min_value, max_value):
    while True:
        try:
            num = int(input(prompt))
            if min_value <= num <= max_value:
                return num
            print(f"Please enter a number between {min_value} and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
```

After half the attempts, the player gets a hint, using `%` from [Session 4](04-operators-conditionals-input.md):

```py
if attempts == max_attempts // 2 and not hints_given:
    hint = "even" if secret_number % 2 == 0 else "odd"
    print(f"Hint: The number is {hint}.")
    hints_given = True
```

:::{tip}
**Why 7 attempts for 1–100?** With the "halve the range" strategy (always guess the middle), 7
guesses are always enough for 100 numbers, because 2⁷ = 128. Hard mode (1–1000 in 5) needs luck:
the strategy needs 10 guesses.
:::

## Version C · a leaderboard in a file

Scores are saved as lines of `name,attempts` in `leaderboard.txt`, so they survive between games:

```py
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as file:
            leaderboard = [line.strip().split(",") for line in file.readlines()]
            leaderboard = [(name, int(score)) for name, score in leaderboard]
            return sorted(leaderboard, key=lambda x: x[1])
    return []

def update_leaderboard(player_name, attempts):
    leaderboard = load_leaderboard()
    leaderboard.append((player_name, attempts))
    leaderboard = sorted(leaderboard, key=lambda x: x[1])[:10]    # keep the top 10
    save_leaderboard(leaderboard)
```

`sorted(..., key=lambda x: x[1])` sorts the `(name, attempts)` tuples by attempts: fewer is better.

## Version D · a window with Tkinter

The last version wraps the same logic in a window: radio buttons for the level, a text box for the
guess, and pop-up messages. The game state (secret number, attempts) lives on a class instance
instead of local variables, because button clicks call different methods. You don't need classes
yet; read it as a preview of where Python goes next. Run it with `python d_tkinter.py` (Tkinter
comes with Python on Windows and macOS; on Ubuntu install `python3-tk`).

## Ideas to extend the game

- **Scoring**: points = `max_attempts - attempts + 1`, multiplied by the level.
- **Warmer / colder**: compare the new guess's distance with the previous one.
- **Statistics**: games played, win rate, average attempts, saved in a file.
- **Reverse game**: *you* think of a number and the computer guesses it with binary search.

## More mini projects

From [Python Mini Projects Ideas](https://learn.parottasalna.com/blog/python-mini-projects-ideas/):

1. A calculator, then a calculator **game** (solve random sums against the clock)
2. A command-line to-do list (saved to a file)
3. Hangman
4. A Caesar cipher: encrypt and decrypt text by shifting letters
5. A Pomodoro timer
6. A simple key-value store (like a tiny Redis)
7. A grocery list
8. An alarm clock

Each one uses only what's in this course.

## Hands-on exercises

**Exercise 1 · Limit the attempts.** Change version A so the player has only 7 attempts, and reveal
the number when they run out.

<details class="solution"><summary>Solution</summary>

```py
MAX_ATTEMPTS = 7
for attempt in range(1, MAX_ATTEMPTS + 1):
    guess = get_user_guess()
    if guess < secret_number:
        print("Too low!")
    elif guess > secret_number:
        print("Too high!")
    else:
        print(f"Correct in {attempt} attempts!")
        break
else:                       # runs only if the loop didn't break
    print(f"Out of attempts. The number was {secret_number}.")
```

A `for … else` is perfect here: the `else` runs only when the loop finished without `break`.

</details>

**Exercise 2 · Warmer or colder.** After the second guess, also print "warmer" if the guess is closer
to the secret than the previous one, otherwise "colder".

<details class="solution"><summary>Solution</summary>

```python
def warmer_or_colder(secret, previous, current):
    if previous is None:
        return ""
    return "warmer" if abs(secret - current) < abs(secret - previous) else "colder"

print(warmer_or_colder(18, None, 50))   # (nothing on the first guess)
print(warmer_or_colder(18, 50, 30))     # warmer
print(warmer_or_colder(18, 30, 45))     # colder
```

Keep `previous = None` before the loop and set `previous = guess` at the end of each round.

</details>

**Exercise 3 · Binary search.** Write `computer_guesses(secret, low=1, high=100)` that guesses by
always picking the middle, and returns how many guesses it needed.

<details class="solution"><summary>Solution</summary>

```python
def computer_guesses(secret, low=1, high=100):
    guesses = 0
    while True:
        guesses += 1
        guess = (low + high) // 2
        if guess == secret:
            return guesses
        if guess < secret:
            low = guess + 1
        else:
            high = guess - 1

print(max(computer_guesses(n) for n in range(1, 101)))   # 7: never more than 7
```

This proves the 7-attempt claim from the tip above.

</details>

**Exercise 4 · A safer leaderboard.** In version C, a player named "Ravi, Kumar" breaks the file
(an extra comma). Fix it.

<details class="solution"><summary>Solution</summary>

Use the `csv` module, which quotes commas for you:

```python
import csv

def save_leaderboard(leaderboard, path="leaderboard.csv"):
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(leaderboard)

def load_leaderboard(path="leaderboard.csv"):
    try:
        with open(path, newline="") as f:
            return sorted(((name, int(score)) for name, score in csv.reader(f)), key=lambda x: x[1])
    except FileNotFoundError:
        return []

save_leaderboard([("Ravi, Kumar", 4), ("Priya", 3)])
print(load_leaderboard())     # [('Priya', 3), ('Ravi, Kumar', 4)]
```

</details>

**Exercise 5 · Pick a mini project.** Build the Caesar cipher: `encrypt(text, shift)` and
`decrypt(text, shift)`, keeping spaces and punctuation as they are.

<details class="solution"><summary>Solution</summary>

```python
def shift_char(ch, shift):
    if ch.isupper():
        return chr((ord(ch) - ord("A") + shift) % 26 + ord("A"))
    if ch.islower():
        return chr((ord(ch) - ord("a") + shift) % 26 + ord("a"))
    return ch

def encrypt(text, shift):
    return "".join(shift_char(c, shift) for c in text)

def decrypt(text, shift):
    return encrypt(text, -shift)

secret = encrypt("Parotta Salna!", 3)
print(secret)                 # Sdurwwd Vdoqd!
print(decrypt(secret, 3))     # Parotta Salna!
```

</details>

## Full source

<details class="source">
<summary>a_simple.py</summary>

```{literalinclude} ../code/12-guessing-game/a_simple.py
:language: python
```

</details>

<details class="source">
<summary>b_levels.py</summary>

```{literalinclude} ../code/12-guessing-game/b_levels.py
:language: python
```

</details>

<details class="source">
<summary>c_leaderboard.py</summary>

```{literalinclude} ../code/12-guessing-game/c_leaderboard.py
:language: python
```

</details>

<details class="source">
<summary>d_tkinter.py</summary>

```{literalinclude} ../code/12-guessing-game/d_tkinter.py
:language: python
```

</details>

**Downloads:**
{download}`a_simple.py <../code/12-guessing-game/a_simple.py>` ·
{download}`b_levels.py <../code/12-guessing-game/b_levels.py>` ·
{download}`c_leaderboard.py <../code/12-guessing-game/c_leaderboard.py>` ·
{download}`d_tkinter.py <../code/12-guessing-game/d_tkinter.py>`
