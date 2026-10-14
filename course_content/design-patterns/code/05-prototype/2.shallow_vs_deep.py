"""Shallow copy shares the inner list; deep copy copies everything inside too."""
import copy

a = {"name": "bot", "tools": ["search"]}

shallow = copy.copy(a)
shallow["tools"].append("calc")
print(a["tools"])         # ['search', 'calc']   <- a changed too!

deep = copy.deepcopy(a)
deep["tools"].append("crm")
print(a["tools"])         # ['search', 'calc']   <- a is safe
print(deep["tools"])      # ['search', 'calc', 'crm']
