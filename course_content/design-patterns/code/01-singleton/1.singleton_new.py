"""Singleton with __new__: build the object once, hand out the same one after that."""


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Loading config from disk...")
            cls._instance = super().__new__(cls)
            cls._instance.settings = {"debug": False}
        return cls._instance
    # No __init__ on purpose: Python runs __init__ on every Config() call, even when __new__
    # returns the old object, so it would reset the settings.


a = Config()
b = Config()

a.settings["debug"] = True
print(a is b)               # True
print(b.settings["debug"])  # True
