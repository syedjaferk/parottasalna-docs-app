"""Command: each action is an object, so it can be stored, undone and redone."""
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
        self._undone.clear()          # a new action makes old redos invalid

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
