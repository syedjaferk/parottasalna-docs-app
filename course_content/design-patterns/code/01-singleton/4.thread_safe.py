"""Thread-safe Singleton with double-checked locking.

The plain version can create two objects when two threads arrive at the same moment.
"""
import threading
import time


class Unsafe:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            time.sleep(0.05)                    # pretend loading takes time
            cls._instance = super().__new__(cls)
        return cls._instance


class Config:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:               # fast check, no lock
            with cls._lock:
                if cls._instance is None:       # check again inside the lock
                    time.sleep(0.05)
                    cls._instance = super().__new__(cls)
        return cls._instance


def count_instances(cls, n=10):
    ids = []
    threads = [threading.Thread(target=lambda: ids.append(id(cls()))) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return len(set(ids))


print("unsafe :", count_instances(Unsafe), "instance(s)")    # usually more than 1
print("locked :", count_instances(Config), "instance(s)")    # always 1
