# Session 6 · Indexing and slicing

📖 Based on the blog post [Python: Indexing & Slicing](https://learn.parottasalna.com/blog/python-indexing-amp-slicing/).

## The big idea

A string is a **row of characters**, and each one has a position number: its **index**. Indexing
picks **one** item; slicing cuts out a **piece**. The same rules work on lists and tuples, so
you'll use this in every session from here on.

**Everyday example:** seats in a cinema row. "Seat 3" is indexing. "Seats 3 to 6" is slicing.

```{raw} html
:file: ../diagrams/s06-index.html
```

## Indexing: one character

Python counts from **0**:

```python
word = "Python"
print(word[0], word[1], word[5])
```

```text
P y n
```

**Negative** indexes count from the end: `-1` is the last item.

```python
word = "Python"
print(word[-1], word[-2], word[-6])
```

```text
n o P
```

Going past the end raises an error: `word[6]` → `IndexError: string index out of range`.

Example: the initials of a name.

```python
full_name = "Parotta Salna"
print(full_name[0] + full_name[8])
```

```text
PS
```

## Slicing: a piece

`text[start:stop]` takes from `start` **up to but not including** `stop`:

```python
text = "Hello, World!"
print(text[0:5])
print(text[7:12])
```

```text
Hello
World
```

:::{tip}
**Why is stop excluded?** So that `stop - start` is the length of the slice, and `text[:5] +
text[5:]` gives back the whole string with no overlap.
:::

### Leaving out start or stop

```python
text = "Python Programming"
print(text[:6])      # from the beginning
print(text[7:])      # to the end
print(text[-3:])     # the last three characters
print(text[:-1])     # everything except the last
```

```text
Python
Programming
ing
Python Programmin
```

### Adding a step

`text[start:stop:step]` takes every `step`-th character. A negative step goes backwards:

```python
text = "abcdefghij"
print(text[::2])      # every second character
print(text[0:10:3])   # every third
print(text[::-1])     # reversed
print(text[::-2])     # reversed, every second
```

```text
acegi
adgj
jihgfedcba
jhfdb
```

## Real-world slicing

```python
filename = "report.pdf"
print(filename[-3:])                 # file extension

date = "20230722"                    # YYYYMMDD
print(f"Year: {date[:4]}, Month: {date[4:6]}, Day: {date[6:]}")

quote = "To be or not to be, that is the question."
print(quote[9:18])

print("Malayalam".lower() == "Malayalam".lower()[::-1])   # palindrome check
```

```text
pdf
Year: 2023, Month: 07, Day: 22
not to be
True
```

:::{note}
The blog post used `quote[9:17]`, which gives `'not to b'`: the stop index is excluded, so it has
to be one past the last `e`, which is 18.
:::

## Strings can't be changed

```python
word = "Python"
# word[0] = "J"           → TypeError: 'str' object does not support item assignment
new_word = "J" + word[1:]  # build a new string instead
print(new_word)
```

```text
Jython
```

## Common mistakes

- **Starting from 1.** The first character is `[0]`.
- **Expecting stop to be included.** `"Hello"[0:4]` is `"Hell"`.
- **Out-of-range index vs slice.** `"abc"[10]` raises `IndexError`, but `"abc"[1:10]` is just
  `"bc"`. Slices never complain.
- **`filename[-3:]` for extensions.** It breaks for `.jpeg` or `.py`. Use
  `filename.rsplit(".", 1)[-1]` for any length.

## Hands-on exercises

**Exercise 1 · First and last.** For `city = "Coimbatore"`, print the first letter, the last
letter and the length.

<details class="solution"><summary>Solution</summary>

```python
city = "Coimbatore"
print(city[0], city[-1], len(city))     # C e 10
```

</details>

**Exercise 2 · Middle character.** Print the middle character of `"Python"` and of `"Chennai"`
(for even lengths, the right-hand one of the middle two).

<details class="solution"><summary>Solution</summary>

```python
for word in ["Python", "Chennai"]:
    print(word[len(word) // 2])     # h, n
```

</details>

**Exercise 3 · Palindrome.** Write `is_palindrome(word)`, ignoring case. Test "Madam", "Level" and
"Python".

<details class="solution"><summary>Solution</summary>

```python
def is_palindrome(word):
    w = word.lower()
    return w == w[::-1]

for w in ["Madam", "Level", "Python"]:
    print(w, is_palindrome(w))     # True True False
```

</details>

**Exercise 4 · Hide the card.** Print a card number `"1234567812345678"` as `************5678`.

<details class="solution"><summary>Solution</summary>

```python
card = "1234567812345678"
print("*" * (len(card) - 4) + card[-4:])
```

</details>

**Exercise 5 · Dates.** Turn `"2024-07-15"` into `"15/07/2024"` using only slicing.

<details class="solution"><summary>Solution</summary>

```python
d = "2024-07-15"
print(d[8:] + "/" + d[5:7] + "/" + d[:4])     # 15/07/2024
```

</details>

**Exercise 6 · Every other word.** For `"one two three four five six"`, print every other word
(`one three five`), using `split()` and a slice.

<details class="solution"><summary>Solution</summary>

```python
words = "one two three four five six".split()
print(" ".join(words[::2]))
```

The same slicing rules work on lists.

</details>
