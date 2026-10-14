"""A reusable singleton decorator: one instance per decorated class."""


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class Logger:
    def __init__(self):
        self.lines = []

    def log(self, msg):
        self.lines.append(msg)


@singleton
class Cache:
    def __init__(self):
        self.data = {}


Logger().log("server started")
Logger().log("user logged in")
print(Logger().lines)            # ['server started', 'user logged in']
print(Logger() is Logger())      # True
print(Cache() is Cache())        # True
print(Logger() is Cache())       # False: each class has its own instance
