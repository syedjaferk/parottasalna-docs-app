"""Composite: files (leaves) and folders (composites) share one interface."""
from abc import ABC, abstractmethod


class Node(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def size(self) -> int: ...

    @abstractmethod
    def show(self, indent: int = 0): ...


class File(Node):                              # leaf
    def __init__(self, name, size):
        super().__init__(name)
        self._size = size

    def size(self):
        return self._size

    def show(self, indent=0):
        print(" " * indent + f"📄 {self.name} ({self._size} KB)")


class Folder(Node):                            # composite
    def __init__(self, name):
        super().__init__(name)
        self.children: list[Node] = []

    def add(self, node: Node):
        self.children.append(node)
        return self

    def size(self):
        return sum(c.size() for c in self.children)

    def show(self, indent=0):
        print(" " * indent + f"📁 {self.name} ({self.size()} KB)")
        for c in self.children:
            c.show(indent + 2)


root = Folder("project")
src = Folder("src").add(File("main.py", 4)).add(File("utils.py", 2))
docs = Folder("docs").add(File("readme.md", 1))
root.add(src).add(docs).add(File("LICENSE", 1))

root.show()
print(root.size())
