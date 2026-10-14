"""Prototype: do the slow setup once, then clone with copy.deepcopy."""
import copy


class AgentConfig:
    def __init__(self):
        print("Loading defaults... (slow)")
        self.model = "gpt-oss-120b"
        self.temperature = 0.2
        self.tools = ["search", "calculator"]


base = AgentConfig()                 # slow setup once

support_bot = copy.deepcopy(base)
sales_bot = copy.deepcopy(base)
sales_bot.temperature = 0.7
sales_bot.tools.append("crm")

print(base.tools)         # ['search', 'calculator']   <- base untouched
print(sales_bot.tools)    # ['search', 'calculator', 'crm']
