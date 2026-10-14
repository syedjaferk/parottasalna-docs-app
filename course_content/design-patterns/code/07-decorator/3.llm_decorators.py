"""Decorator + AI: retry and cache around an LLM call, without touching the call itself."""
import random
import time
from functools import lru_cache, wraps


def retry(times=3, delay=1):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == times:
                        raise
                    print(f"attempt {attempt} failed: {e}. retrying...")
                    time.sleep(delay)
        return wrapper
    return deco


class FlakyLLM:
    """Offline stand-in that fails half the time, like a busy API."""
    def invoke(self, prompt):
        if random.random() < 0.5:
            raise ConnectionError("503 service unavailable")
        return type("Msg", (), {"content": f"(answer to: {prompt})"})()


llm = FlakyLLM()


@lru_cache(maxsize=256)
@retry(times=5, delay=0.1)
def ask_llm(prompt: str) -> str:
    return llm.invoke(prompt).content


random.seed(3)
print(ask_llm("What is a decorator?"))
print(ask_llm("What is a decorator?"))      # from the cache: no call, no retries
print(ask_llm.cache_info())
