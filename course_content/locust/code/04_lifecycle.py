import itertools

from locust import User, between, events, task

ids = itertools.count(1)


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("TEST START: the whole test begins (runs once)")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("TEST STOP: the whole test is over (runs once)")


class Customer(User):
    wait_time = between(0.5, 0.8)

    def on_start(self):
        self.name = f"user-{next(ids)}"
        print(f"  on_start  {self.name}: runs once when this user is created")

    @task
    def shop(self):
        print(f"  task      {self.name}: shopping")

    def on_stop(self):
        print(f"  on_stop   {self.name}: runs once when this user is stopped")
