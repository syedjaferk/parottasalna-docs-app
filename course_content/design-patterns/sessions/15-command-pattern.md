# Session 15 · Command pattern

## The big idea

Normally you call a method and it runs *now*. The **Command** pattern turns an action into an
**object**. Now you can store it, queue it, log it, run it later, and **undo** it.

**Everyday example:** ordering at a restaurant. The waiter writes your order on a slip (the
command). The slip goes to the kitchen queue, and the chef cooks when ready. You and the chef never
talk directly, and the slip can be cancelled.

:::{admonition} In plain words
:class: tip
Turn "do this" into a **thing you can hold**: an object that knows how to do the action and how to undo it. Then you can save it, queue it, log it or reverse it.

**Reach for it when:**

- you need undo/redo
- actions should run later, in a queue or on another worker
- you want a log of what was done, or a human to approve it first
:::

## Without Command

`0.no_command.py`: actions happen immediately and leave no trace.

```python
class Editor:
    def __init__(self): self.text = ""

editor = Editor()
editor.text += "Hello"
editor.text += " World"
# How do we undo " World"? We forgot what we did.
```

## With Command: undo and redo

`1.command.py`:

```python
from abc import ABC, abstractmethod

class Editor:
    def __init__(self):
        self.text = ""

class Command(ABC):
    @abstractmethod
    def execute(self): ...
    @abstractmethod
    def undo(self): ...

class AppendText(Command):
    def __init__(self, editor: Editor, text: str):
        self.editor, self.text = editor, text

    def execute(self):
        self.editor.text += self.text

    def undo(self):
        self.editor.text = self.editor.text[: -len(self.text)]

class History:
    def __init__(self):
        self._done: list[Command] = []
        self._undone: list[Command] = []

    def run(self, cmd: Command):
        cmd.execute()
        self._done.append(cmd)
        self._undone.clear()

    def undo(self):
        if self._done:
            cmd = self._done.pop()
            cmd.undo()
            self._undone.append(cmd)

    def redo(self):
        if self._undone:
            cmd = self._undone.pop()
            cmd.execute()
            self._done.append(cmd)

editor, history = Editor(), History()
history.run(AppendText(editor, "Hello"))
history.run(AppendText(editor, " World"))
print(editor.text)      # Hello World
history.undo()
print(editor.text)      # Hello
history.redo()
print(editor.text)      # Hello World
```

Every action is now an object in a list, so undo is just "pop the last one and reverse it".

```{raw} html
:file: ../diagrams/s15-command.html
```

## Queue commands for later

`2.queue.py`: the same idea powers job queues (Celery, RabbitMQ consumers).

```python
from queue import Queue

class SendEmail:
    def __init__(self, to): self.to = to
    def execute(self): print(f"emailing {self.to}")

class ResizeImage:
    def __init__(self, path): self.path = path
    def execute(self): print(f"resizing {self.path}")

jobs = Queue()
jobs.put(SendEmail("kavya@example.com"))
jobs.put(ResizeImage("photo.jpg"))

while not jobs.empty():
    jobs.get().execute()          # a worker runs them one by one
```

## Command + AI: tool calls

When an LLM agent decides to use a tool, it produces a name and arguments. That is a command
(`3.tool_commands.py`):

```python
class ToolCall:
    def __init__(self, name, args):
        self.name, self.args = name, args

tools = {
    "add": lambda a, b: a + b,
    "upper": lambda text: text.upper(),
}

def run_tool(call: ToolCall):
    if call.name not in tools:
        raise ValueError(f"unknown tool {call.name}")
    return tools[call.name](**call.args)

log = []
for call in [ToolCall("add", {"a": 2, "b": 3}), ToolCall("upper", {"text": "hi"})]:
    log.append((call.name, call.args))          # audit trail
    print(run_tool(call))                        # 5, then HI
```

Because calls are data, you can log them, validate them (with Pydantic, from the data-validation session), ask a human to
approve, or replay them.

## Common mistakes

- **Undo that doesn't match execute.** Test `execute` then `undo` returns the original state.
- **Commands that hold too much state.** A command should store only what it needs to run and undo.
- **Forgetting to clear redo** after a new action. Otherwise redo applies stale commands.
- **Huge history.** Cap the undo stack.

## Hands-on exercises

**Exercise 1 · Delete command.** Add `DeleteLast(n)` that removes the last `n` characters and can undo.

<details class="solution"><summary>Solution</summary>

```python
class DeleteLast(Command):
    def __init__(self, editor, n):
        self.editor, self.n, self._removed = editor, n, ""

    def execute(self):
        self._removed = self.editor.text[-self.n:]
        self.editor.text = self.editor.text[: -self.n]

    def undo(self):
        self.editor.text += self._removed
```

Note how the command remembers what it removed.

</details>

**Exercise 2 · Smart-home remote.** `LightOn`, `LightOff` commands and a `Remote` with `press(cmd)`
and `undo_last()`.

<details class="solution"><summary>Solution</summary>

```python
class Light:
    def __init__(self): self.on = False

class LightOn:
    def __init__(self, light): self.light = light
    def execute(self): self.light.on = True
    def undo(self): self.light.on = False

class LightOff:
    def __init__(self, light): self.light = light
    def execute(self): self.light.on = False
    def undo(self): self.light.on = True

class Remote:
    def __init__(self): self.history = []
    def press(self, cmd): cmd.execute(); self.history.append(cmd)
    def undo_last(self):
        if self.history: self.history.pop().undo()

light, remote = Light(), Remote()
remote.press(LightOn(light)); print(light.on)    # True
remote.undo_last();          print(light.on)    # False
```

</details>

**Exercise 3 · Macro.** A `MacroCommand` that runs a list of commands together and undoes them in
reverse.

<details class="solution"><summary>Solution</summary>

```python
class Macro(Command):
    def __init__(self, commands): self.commands = commands
    def execute(self):
        for c in self.commands: c.execute()
    def undo(self):
        for c in reversed(self.commands): c.undo()

history.run(Macro([AppendText(editor, "A"), AppendText(editor, "B")]))
history.undo()     # removes both
```

</details>

## Full source

<details class="source">
<summary>1.command.py</summary>

```{literalinclude} ../code/15-command/1.command.py
:language: python
```

</details>

<details class="source">
<summary>3.tool_commands.py</summary>

```{literalinclude} ../code/15-command/3.tool_commands.py
:language: python
```

</details>

**Downloads:**
{download}`0.no_command.py <../code/15-command/0.no_command.py>` ·
{download}`1.command.py <../code/15-command/1.command.py>` ·
{download}`2.queue.py <../code/15-command/2.queue.py>` ·
{download}`3.tool_commands.py <../code/15-command/3.tool_commands.py>`
