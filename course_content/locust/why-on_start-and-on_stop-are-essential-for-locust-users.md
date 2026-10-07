# Why on\_start and on\_stop are Essential for Locust Users

In this chapter, we’ll cover,

1. What `on_start` and `on_stop` do.
2. Why they are important.
3. Practical examples of using these methods.
4. Running and testing Locust scripts.

### What Are `on_start` and `on_stop`?

* **`on_start`**: This method is executed once when a new simulated user starts. It's commonly used for tasks like logging in or setting up the environment.
* **`on_stop`**: This method is executed once when a simulated user stops. It’s often used for cleanup tasks like logging out.

These methods are executed _only once per user_ during the lifecycle of a test, as opposed to tasks that are run repeatedly.

### Why Use `on_start` and `on_stop`?

1. **Simulating Real User Behavior**: Real users often start a session with an action (e.g., login) and end it with another (e.g., logout).
2. **Initial Setup**: Some tasks require initializing data or setting up user state before performing other actions.
3. **Cleanup**: Ensure that actions like logout are performed to leave the system in a clean state.

### Examples

**Basic Usage of `on_start` and `on_stop`**

In this example, we just print `on start and` \`on stop\` for each user while running a task.

```python
from datetime import datetime
from locust import User, task, between, constant, constant_pacing

class MyUser(User):

    wait_time = between(1, 5)

    def on_start(self):
        print("on start")

    def on_stop(self):
        print("on stop")

    @task
    def print_datetime(self):
        print(datetime.now())

```
