# Session 8 · Facade pattern

## The big idea

A real system is made of many small parts: each with its own setup and methods. Using them directly
means the caller must know the right steps and the right order. The **Facade** pattern puts one
simple class in front that does the whole job with one or two methods.

**Everyday example:** a hotel receptionist. You say "I need a room with dinner and a cab at 6". The
receptionist talks to housekeeping, the kitchen and the taxi desk. You never visit those yourself.

:::{admonition} In plain words
:class: tip
Give a complicated system **one simple front door**. Callers make one call; the facade runs all the steps in the right order behind the scenes.

**Reach for it when:**

- callers repeat the same multi-step sequence across several classes
- you want one place where the order of steps lives
- beginners (or other teams) should use the system without learning every part
:::

## Without Facade

`0.no_facade.py`: the caller runs every step in the right order.

```python
class Inventory:
    def check(self, item): print(f"{item} in stock"); return True
class Payment:
    def charge(self, amount): print(f"charged ₹{amount}"); return True
class Shipping:
    def book(self, item): print(f"shipping booked for {item}")
class Notifier:
    def send(self, msg): print(f"sent: {msg}")

# every page that places an order repeats this:
inv, pay, ship, note = Inventory(), Payment(), Shipping(), Notifier()
if inv.check("laptop") and pay.charge(55000):
    ship.book("laptop")
    note.send("Order placed")
```

Five lines, four classes, one fixed order. The checkout page, the mobile API and the admin tool all
copy it, and one change means editing all three.

## With Facade

`1.facade.py`:

```python
class OrderFacade:
    def __init__(self):
        self._inventory = Inventory()
        self._payment = Payment()
        self._shipping = Shipping()
        self._notifier = Notifier()

    def place_order(self, item: str, amount: int) -> bool:
        if not self._inventory.check(item):
            return False
        if not self._payment.charge(amount):
            return False
        self._shipping.book(item)
        self._notifier.send(f"Order placed for {item}")
        return True

OrderFacade().place_order("laptop", 55000)
```

One line for the caller. The order of steps lives in one place.

```{raw} html
:file: ../diagrams/s08-facade.html
```

The facade does **not** hide the subsystem classes. Advanced users can still use `Payment` directly.
It just offers an easy front door.

## Facade + AI: a RAG facade

A RAG pipeline has loader, splitter, embedder, vector store, retriever, prompt and LLM
(`2.rag_facade.py`):

```python
class RagFacade:
    def __init__(self, llm, embeddings, vector_store):
        self._llm = llm
        self._embeddings = embeddings
        self._store = vector_store

    def ingest(self, text: str):
        chunks = [text[i:i + 500] for i in range(0, len(text), 500)]
        self._store.add_texts(chunks)

    def ask(self, question: str) -> str:
        docs = self._store.similarity_search(question, k=3)
        context = "\n\n".join(d.page_content for d in docs)
        prompt = f"Answer using only this context:\n{context}\n\nQuestion: {question}"
        return self._llm.invoke(prompt).content

rag = RagFacade(llm, embeddings, store)
rag.ingest(open("notes.txt").read())
print(rag.ask("What is a Singleton?"))
```

Your web app only needs `ingest()` and `ask()`.

## Facade vs Adapter

- **Adapter**: one thing, wrong shape → make it fit. It *changes* an interface.
- **Facade**: many things, too complex → give one simple entry. It *simplifies* an interface.

## Common mistakes

- **A "god" facade** with 40 methods. Make several small facades: `OrderFacade`, `ReportFacade`.
- **Business logic inside the facade.** It should coordinate, not decide.
- **Blocking access to the subsystems.** Keep them usable for special cases.

## Hands-on exercises

**Exercise 1 · Home theatre.** Make `HomeTheatre.watch(movie)` do: lights dim, projector on, sound on,
play movie.

<details class="solution"><summary>Solution</summary>

```python
class Lights:
    def dim(self): print("lights dimmed")
class Projector:
    def on(self): print("projector on")
class Sound:
    def on(self): print("sound on")
class Player:
    def play(self, m): print(f"playing {m}")

class HomeTheatre:
    def __init__(self):
        self.lights, self.projector, self.sound, self.player = Lights(), Projector(), Sound(), Player()

    def watch(self, movie):
        self.lights.dim()
        self.projector.on()
        self.sound.on()
        self.player.play(movie)

HomeTheatre().watch("Interstellar")
```

</details>

**Exercise 2 · Add `cancel_order`.** Use the same subsystems in reverse.

<details class="solution"><summary>Solution</summary>

```python
class Payment:
    def charge(self, amount): ...
    def refund(self, amount): print(f"refunded ₹{amount}")

class OrderFacade:
    ...
    def cancel_order(self, item, amount):
        self._payment.refund(amount)
        self._notifier.send(f"Order cancelled for {item}")
```

</details>

**Exercise 3 · Video converter.** `convert(path, fmt)` should load the file, extract audio, encode
and save. Hide the steps behind a facade.

<details class="solution"><summary>Solution</summary>

```python
class Loader:
    def load(self, p): print(f"loaded {p}"); return p
class Encoder:
    def encode(self, data, fmt): print(f"encoded to {fmt}"); return data
class Saver:
    def save(self, data, name): print(f"saved {name}")

class VideoConverter:
    def convert(self, path, fmt):
        data = Loader().load(path)
        data = Encoder().encode(data, fmt)
        Saver().save(data, path.rsplit(".", 1)[0] + "." + fmt)

VideoConverter().convert("movie.avi", "mp4")
```

</details>

## Full source

<details class="source">
<summary>1.facade.py</summary>

```{literalinclude} ../code/08-facade/1.facade.py
:language: python
```

</details>

<details class="source">
<summary>2.rag_facade.py</summary>

```{literalinclude} ../code/08-facade/2.rag_facade.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_facade.py <../code/08-facade/0.no_facade.py>` ·
{download}`1.facade.py <../code/08-facade/1.facade.py>` ·
{download}`2.rag_facade.py <../code/08-facade/2.rag_facade.py>`
