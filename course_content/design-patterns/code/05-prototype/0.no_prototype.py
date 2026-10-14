"""Without Prototype: every new object repeats the slow setup."""


class AgentConfig:
    def __init__(self):
        print("Loading defaults... (slow)")
        self.model = "gpt-oss-120b"
        self.temperature = 0.2
        self.tools = ["search", "calculator"]


support_bot = AgentConfig()
sales_bot = AgentConfig()     # slow setup again
sales_bot.temperature = 0.7
