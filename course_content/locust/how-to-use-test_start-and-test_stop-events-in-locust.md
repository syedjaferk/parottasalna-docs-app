# How to use test\_start and test\_stop Events in Locust

In this chapter, we will

1. Understand what `test_start` and `test_stop` are.
2. Explore their use cases.
3. Provide examples of implementing these events.
4. Discuss how to run and validate the setup.

### What Are `test_start` and `test_stop`?

* **`test_start`**: Triggered when the test starts. Use this event to perform actions like initializing global resources, starting external systems, or logging test start information.
* **`test_stop`**: Triggered when the test ends. This event is ideal for cleanup operations, aggregating results, or stopping external systems.

These events are **global** and apply to the entire test environment rather than individual user instances.

### Why Use `test_start` and `test_stop`?

* **Global Setup**: Initialize shared resources, like database connections or external services.
* **Logging**: Record timestamps or test details for audit or reporting purposes.
* **External System Management**: Start/stop services that the test depends on, such as mock servers or third-party APIs.

### Example: Basic Usage of `test_start` and `test_stop`

Here’s a basic example demonstrating the usage of these events

```python
from locust import User, task, between, events
from datetime import datetime

# Global setup: Perform actions at test start
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Test started at:", datetime.now())

# Global teardown: Perform actions at test stop
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Test stopped at:", datetime.now())

# Simulated user behavior
class MyUser(User):
    wait_time = between(1, 5)

    @task
    def print_datetime(self):
        """Task that prints the current datetime."""
        print("Current datetime:", datetime.now())
```

Running the Example

* Save the code as `locustfile.py`.
* Start Locust -> \``locust -f locustfile.py`\`
* Configure the test parameters (number of users, spawn rate, etc.) in the web UI at http://localhost:8089.
* Observe the console output:
  * A message when the test starts (`on_test_start`).
  * Messages during the test as users execute tasks.
  * A message when the test stops (`on_test_stop`).

### Example: Logging Test Details

You can log detailed test information, like the number of users and host under test, using `environment` and `kwargs`

```python
from locust import User, task, between, events

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Test started!")
    print(f"Target host: {environment.host}")
    print(f"Total users: {environment.runner.target_user_count}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Test finished!")
    print("Summary:")
    print(f"Requests completed: {environment.stats.total.num_requests}")
    print(f"Failures: {environment.stats.total.num_failures}")

class MyUser(User):
    wait_time = between(1, 5)

    @task
    def dummy_task(self):
        pass

```

#### Observing the Results

When you run the above examples

* **At Test Start**: Look for messages indicating setup actions, like initializing external systems or printing start time.
* **During the Test**: Observe user tasks being executed.
* **At Test Stop**: Verify that cleanup actions were executed successfully.
