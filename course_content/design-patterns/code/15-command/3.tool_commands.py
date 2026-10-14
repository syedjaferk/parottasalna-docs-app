"""Command + AI: an LLM tool call is a command: a name plus arguments, as data."""


class ToolCall:
    def __init__(self, name, args):
        self.name, self.args = name, args


tools = {
    "add": lambda a, b: a + b,
    "upper": lambda text: text.upper(),
}


def run_tool(call: ToolCall):
    if call.name not in tools:
        raise ValueError(f"unknown tool {call.name}")
    return tools[call.name](**call.args)


log = []
for call in [ToolCall("add", {"a": 2, "b": 3}), ToolCall("upper", {"text": "hi"})]:
    log.append((call.name, call.args))          # audit trail
    print(run_tool(call))                        # 5, then HI

print(log)
