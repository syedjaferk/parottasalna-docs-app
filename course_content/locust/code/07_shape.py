from locust import HttpUser, LoadTestShape, between, task


class ShopUser(HttpUser):
    wait_time = between(0.1, 0.2)

    @task
    def products(self):
        self.client.get("/products")


class StepLoad(LoadTestShape):
    """Add 2 users every 3 seconds, for 9 seconds in total."""
    step_time = 3
    step_users = 2
    total_time = 9
    last_step = 0

    def tick(self):
        run_time = self.get_run_time()
        if run_time > self.total_time:
            return None                               # None ends the test
        step = int(run_time // self.step_time) + 1
        if step != self.last_step:
            self.last_step = step
            print(f"step {step}: going to {step * self.step_users} users (at {run_time:.0f}s)")
        return step * self.step_users, self.step_users
