from locust import SequentialTaskSet, User, between, events, task

steps = []
buyer_ids = iter(range(1, 100))
env = None


class BuyerJourney(SequentialTaskSet):
    """Tasks run in the order they are written, then the journey starts again."""

    @task
    def log_in(self):
        steps.append((self.user.buyer, "log in"))

    @task
    def pick_product(self):
        steps.append((self.user.buyer, "pick product"))

    @task
    def check_out(self):
        steps.append((self.user.buyer, "check out"))
        self.interrupt()      # end of the journey; the user starts it again from the top


class Browser(User):
    weight = 3                # three times as many Browsers as Buyers
    wait_time = between(0.1, 0.2)

    @task
    def look_around(self):
        pass


class Buyer(User):
    weight = 1
    wait_time = between(0.1, 0.2)
    tasks = [BuyerJourney]

    def on_start(self):
        self.buyer = next(buyer_ids)


@events.init.add_listener
def remember_environment(environment, **kwargs):
    global env
    env = environment


@events.spawning_complete.add_listener
def spawned(user_count, **kwargs):
    print("users spawned:", user_count, env.runner.user_classes_count)


@events.test_stop.add_listener
def report(environment, **kwargs):
    print("buyer 1 did, in order:", [step for who, step in steps if who == 1][:7])
