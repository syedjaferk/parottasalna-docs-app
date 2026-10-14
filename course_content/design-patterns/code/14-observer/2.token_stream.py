"""Observer + AI: many listeners react to each streamed token."""


class TokenStream:
    def __init__(self):
        self.listeners = []

    def subscribe(self, fn):
        self.listeners.append(fn)

    def emit(self, token: str):
        for fn in self.listeners:
            fn(token)


stream = TokenStream()
buffer, count = [], [0]

stream.subscribe(lambda t: print(t, end="", flush=True))         # show on screen
stream.subscribe(lambda t: buffer.append(t))                     # keep full text
stream.subscribe(lambda t: count.__setitem__(0, count[0] + 1))   # count tokens

for token in ["Design ", "patterns ", "are ", "fun."]:
    stream.emit(token)

print(f"\n{count[0]} tokens, text={''.join(buffer)!r}")
