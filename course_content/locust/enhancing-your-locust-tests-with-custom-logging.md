# Enhancing Your Locust Tests with Custom Logging

### Why Use Logging in Locust?

While Locust's web UI and metrics provide an overview of test performance, logging allows you to:

* **Track Key Events**: Record specific milestones or observations during a test.
* **Debug Failures**: Investigate why certain requests fail.
* **Maintain Historical Records**: Keep a log of test runs for later analysis.
* **Monitor Tests in Real Time**: Watch logs to understand system behavior as the test runs.

### Setting Up Logging in Locust

The `logging` module is built into Python, making it easy to configure and use in Locust scripts. Here’s how to set up a logger:

1. **Initialize a Logger**: Use `logging.getLogger("locust")` to create or retrieve a logger.
2. **Set the Log Level**: Control the verbosity of your logs with levels like `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`.
3. **Add Log Messages**: Use methods like `logger.info()`, `logger.warning()`, and `logger.error()` to log events during your test.

### Example: Logging in a Locust Test

Here’s an example of a Locust test that uses logging to track a specific scenario: validating a response from a `/todos` endpoint.

```python
from locust import HttpUser, constant, task
import logging

# Initialize a logger
logger = logging.getLogger("locust")
logger.setLevel(logging.INFO)  # Set log level to INFO

class MyReqRes(HttpUser):
    wait_time = constant(1)  # Wait 1 second between tasks
    host = "http://localhost:8001"  # Set the target host

    @task
    def get_todos(self):
        # Send a GET request to the "/todos/104" endpoint
        with self.client.get("/todos/104", name="test todo", catch_response=True) as resp1:
            if resp1.status_code == 200 and "Christian Adams" in resp1.json().get("name", ""):
                # Log a success message if the condition is met
                logger.info("Successfully found user 'Christian Adams'.")
                resp1.success()
            else:
                # Log a warning message if the condition is not met
                logger.warning(f"Failed to validate user. Response: {resp1.text}")
                resp1.failure("User validation failed.")

```

### Breakdown of the Code

1. **Logger Initialization**:
   * A logger named `"locust"` is created using `logging.getLogger("locust")`.
   * The log level is set to `INFO` to filter out unnecessary details while still capturing significant events.
2. **Adding Log Messages**:
   * When the response contains `"Christian Adams"`, an informational log is recorded.
   * If validation fails, a warning message is logged, including the response text for debugging.
3. **Catch Response Validation**:
   * The `catch_response=True` parameter enables manual validation of responses, making it easier to integrate logging into the decision-making process.

### Running the Test

To run this script, execute

```bash
locust -f logger_locust.py --headless -u 10 -r 1
```

This command simulates 10 users, spawning at a rate of 1 user per second. Logs will appear in the console as the test runs.
