from collections import Counter

from locust import User, between, events, task

counts = Counter()


class Visitor(User):
    wait_time = between(0.1, 0.3)

    @task(3)
    def browse(self):
        counts["browse"] += 1

    @task(1)
    def buy(self):
        counts["buy"] += 1


@events.test_stop.add_listener
def show_counts(environment, **kwargs):
    total = sum(counts.values())
    print(f"tasks run: {dict(counts)}  (browse is {counts['browse'] / total:.0%} of {total})")
