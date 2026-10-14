"""Composite + AI: an agent's plan is a tree of tasks."""


class Task:
    def __init__(self, name, minutes=0):
        self.name, self.minutes, self.subtasks = name, minutes, []

    def add(self, t):
        self.subtasks.append(t)
        return self

    def total_minutes(self):
        return self.minutes + sum(t.total_minutes() for t in self.subtasks)

    def run(self, depth=0):
        print("  " * depth + f"▶ {self.name}")
        for t in self.subtasks:
            t.run(depth + 1)


plan = Task("Write blog post").add(
    Task("Research").add(Task("Search papers", 20)).add(Task("Read docs", 15))
).add(Task("Outline", 10)).add(Task("Draft", 40))

plan.run()
print(plan.total_minutes())     # 85
