"""A registry of ready-made prototypes: clone by name, change a few fields."""
import copy


class AgentConfig:
    def __init__(self, model="gpt-oss-120b", temperature=0.2, tools=None):
        self.model, self.temperature = model, temperature
        self.tools = tools if tools is not None else ["search", "calculator"]

    def __repr__(self):
        return f"AgentConfig(model={self.model!r}, temperature={self.temperature}, tools={self.tools})"


class PrototypeRegistry:
    def __init__(self):
        self._items = {}

    def register(self, name, obj):
        self._items[name] = obj

    def clone(self, name, **changes):
        obj = copy.deepcopy(self._items[name])
        for k, v in changes.items():
            setattr(obj, k, v)
        return obj


registry = PrototypeRegistry()
registry.register("default", AgentConfig())
registry.register("coder", AgentConfig(tools=["python", "search"]))

bot = registry.clone("default", temperature=0.9)
coder = registry.clone("coder")
coder.tools.append("git")

print(bot)
print(coder)
print(registry.clone("coder"))    # the template is unchanged
