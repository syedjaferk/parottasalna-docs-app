"""Builder + AI: assemble a prompt from named parts, check it in build()."""


class PromptBuilder:
    def __init__(self):
        self._parts = {}
        self._examples = []

    def role(self, text):      self._parts["role"] = text;     return self
    def context(self, text):   self._parts["context"] = text;  return self
    def example(self, q, a):   self._examples.append((q, a));  return self
    def question(self, text):  self._parts["question"] = text; return self
    def format(self, text):    self._parts["format"] = text;   return self

    def build(self) -> str:
        if "question" not in self._parts:
            raise ValueError("a prompt needs a question")
        out = []
        if "role" in self._parts:
            out.append(f"You are {self._parts['role']}.")
        if "context" in self._parts:
            out.append(f"Context:\n{self._parts['context']}")
        for q, a in self._examples:
            out.append(f"Q: {q}\nA: {a}")
        out.append(f"Question: {self._parts['question']}")
        if "format" in self._parts:
            out.append(f"Answer format: {self._parts['format']}")
        return "\n\n".join(out)


prompt = (PromptBuilder()
          .role("a helpful Python tutor")
          .example("What is a list?", "An ordered collection.")
          .question("What is a tuple?")
          .format("one sentence")
          .build())
print(prompt)
