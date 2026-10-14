"""A lighter State: a transition table for simple machines."""

transitions = {
    ("placed", "pay"): "paid",
    ("placed", "cancel"): "cancelled",
    ("paid", "ship"): "shipped",
    ("paid", "cancel"): "cancelled",
}


def move(state, action):
    try:
        return transitions[(state, action)]
    except KeyError:
        raise ValueError(f"cannot {action} when {state}") from None


def allowed(state):
    return [a for (s, a) in transitions if s == state]


s = "placed"
s = move(s, "pay")      # paid
print(s, "-> allowed:", allowed(s))      # ['ship', 'cancel']
s = move(s, "ship")     # shipped
print(s)
try:
    move(s, "cancel")
except ValueError as e:
    print("ValueError:", e)              # cannot cancel when shipped
