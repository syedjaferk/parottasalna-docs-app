"""Without Command: actions happen at once and leave no trace to undo."""


class Editor:
    def __init__(self):
        self.text = ""


editor = Editor()
editor.text += "Hello"
editor.text += " World"
print(editor.text)
# How do we undo " World"? We never recorded what we did.
