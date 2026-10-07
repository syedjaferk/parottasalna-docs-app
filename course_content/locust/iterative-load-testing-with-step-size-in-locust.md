# Iterative Load Testing with Step Size in Locust

In this blog, we will explore **step size iteration** in Locust, which allows you to define user growth patterns and observe how your system handles the incremental load. We’ll dive into an example that uses a custom `LoadTestShape` for step-load behavior.

### Why Use Step-Load Testing?

Step-load testing gradually increases the number of simulated users at predefined intervals, providing insights into

* How the system scales with additional load.
* The exact user count where bottlenecks or failures occur.
* Server behavior under sustained stress.

### Example Code: Step-Load with Locust

Here’s a practical implementation of step-load testing in Locust. We’ll use a custom `LoadTestShape` class to define step-wise load increments.

```python
from locust import HttpUser, task, LoadTestShape, constant


class StepLoadShape(LoadTestShape):
    step_time = 60       # Each step lasts 60 seconds
    step_users = 10      # Add 10 users per step
    spawn_rate = 5       # Spawn 5 users per second
    max_users = 100      # Maximum of 100 users

    def tick(self):
        run_time = self.get_run_time()

        # Calculate the current step based on elapsed time
        current_step = run_time // self.step_time + 1
        if current_step * self.step_users > self.max_users:
            return None  # Stop the test if the maximum user count is reached

        user_count = current_step * self.step_users
        return user_count, self.spawn_rate


class MyReqRes(HttpUser):
    wait_time = constant(1)  # 1 second wait time between tasks
    host = "http://localhost:8001"

    @task
    def get_todos(self):
        # Request a specific resource and validate the response
        with self.client.get("/todos/104", name="test todo", catch_response=True) as resp1:
            if resp1.status_code == 200 and "Christian Adams" in resp1.json().get("name", ""):
                resp1.success()
            else:
                resp1.failure("Validation failed for 'Christian Adams'")

```

### How the Step-Load Works

1. **Step Timing**:
   * Each step lasts for 60 seconds (`step_time`).
   * Users are added incrementally every step, with 10 new users per step (`step_users`).
2. **Spawn Rate**:
   * Users are spawned at a rate of 5 users per second (`spawn_rate`), ensuring a steady ramp-up.
3. **Maximum Users**:
   * The test stops once the user count reaches 100 (`max_users`).
4. **Custom Load Test Shape**:
   * The `tick()` method calculates the current step based on runtime and determines the number of active users and spawn rate for that step.
   * If the number of users exceeds the maximum, the test gracefully stops.
