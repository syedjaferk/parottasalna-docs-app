"""Proxy + AI: a caching proxy in front of an LLM. Same .invoke(), fewer paid calls."""


class FakeLLM:
    """Offline stand-in with the same .invoke(...).content shape as a LangChain chat model."""
    def __init__(self):
        self.calls = 0

    def invoke(self, prompt):
        self.calls += 1
        return type("Msg", (), {"content": f"(answer #{self.calls} to: {str(prompt)[:40]})"})()


class CachingLLM:
    def __init__(self, llm):
        self._llm = llm
        self._cache = {}
        self.hits = 0

    def invoke(self, prompt: str) -> str:
        if prompt in self._cache:
            self.hits += 1
            return self._cache[prompt]
        answer = self._llm.invoke(prompt).content
        self._cache[prompt] = answer
        return answer


real_llm = FakeLLM()
llm = CachingLLM(real_llm)       # same .invoke() as before
print(llm.invoke("What is a proxy?"))   # calls the "API"
print(llm.invoke("What is a proxy?"))   # served from the cache
print(f"API calls: {real_llm.calls}, cache hits: {llm.hits}")    # API calls: 1, cache hits: 1
