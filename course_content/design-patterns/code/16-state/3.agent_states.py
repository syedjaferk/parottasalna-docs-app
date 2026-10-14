"""State + AI: an agent's lifecycle as a state machine (the idea behind LangGraph)."""

agent_transitions = {
    ("planning", "tool_needed"): "calling_tool",
    ("planning", "answer_ready"): "answering",
    ("calling_tool", "tool_done"): "planning",
    ("calling_tool", "tool_failed"): "failed",
    ("answering", "done"): "finished",
}


def step(state, event):
    nxt = agent_transitions.get((state, event))
    if nxt is None:
        raise ValueError(f"event {event!r} is not allowed in state {state!r}")
    print(f"{state:13} --{event}--> {nxt}")
    return nxt


state = "planning"
for event in ["tool_needed", "tool_done", "answer_ready", "done"]:
    state = step(state, event)

try:
    step("calling_tool", "answer_ready")     # answering before the tool result arrived
except ValueError as e:
    print("blocked:", e)
