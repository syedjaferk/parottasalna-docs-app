"""Without Singleton: every call builds a new Config, and the copies disagree."""


class Config:
    def __init__(self):
        print("Loading config from disk...")
        self.settings = {"debug": False}


a = Config()
b = Config()

a.settings["debug"] = True
print(a is b)               # False
print(b.settings["debug"])  # False  <- b never heard about the change
