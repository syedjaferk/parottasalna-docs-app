import time

from locust import User, between, constant, constant_pacing, events, task

runs = {"ConstantUser": 0, "RandomUser": 0, "PacedUser": 0}


class Base(User):
    abstract = True

    @task
    def work(self):
        time.sleep(0.3)               # the task itself takes 0.3 seconds
        runs[type(self).__name__] += 1


class ConstantUser(Base):
    wait_time = constant(1)           # 1 s of waiting AFTER each task


class RandomUser(Base):
    wait_time = between(0.5, 1.5)     # random 0.5 to 1.5 s after each task


class PacedUser(Base):
    wait_time = constant_pacing(1)    # one task START every 1 s, whatever the task time


@events.test_stop.add_listener
def show(environment, **kwargs):
    name = environment.user_classes[0].__name__
    print(f"{name}: ran its task {runs[name]} times in 6 seconds")
