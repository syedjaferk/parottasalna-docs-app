# Simulating Multiple User Types in Locust

In this chapter, we will

1. Discuss the concept of multiple user types in Locust.
2. Explore how to implement multiple user classes with weights.
3. Run and analyze the test results.

### Why Use Multiple User Types?

In real-world applications, different user groups interact with your system differently. For example,

* **Web Users** might spend more time browsing through the UI.
* **Mobile Users** could make faster but more frequent requests.

By simulating distinct user types with varying behaviors, you can identify performance bottlenecks across all client groups.

### Understanding User Classes and Weights

Locust provides the ability to define user classes by extending the `User` or `HttpUser` base class. Each user class can,

* Have a unique set of tasks.
* Define its own wait times.
* Be assigned a **weight**, which determines the proportion of that user type in the simulation.

For example, if `WebUser` has a weight of 1 and `MobileUser` has a weight of 2, the simulation will spawn 1 web user for every 2 mobile users.

### Example: Simulating Web and Mobile Users

Below is an example Locust test with two user types

```python
from locust import User, task, between

# Define a user class for web users
class MyWebUser(User):
    wait_time = between(1, 3)  # Web users wait between 1 and 3 seconds between tasks
    weight = 1  # Web users are less frequent

    @task
    def login_url(self):
        print("I am logging in as a Web User")


# Define a user class for mobile users
class MyMobileUser(User):
    wait_time = between(1, 3)  # Mobile users wait between 1 and 3 seconds
    weight = 2  # Mobile users are more frequent

    @task
    def login_url(self):
        print("I am logging in as a Mobile User")
```

### How Locust Uses Weights

With the above configuration

* For every 3 users spawned, **1 will be a Web User**, and **2 will be Mobile Users** (based on their weights: 1 and 2).

Locust automatically handles spawning these users in the specified ratio.

### Running the Locust Test

1. **Save the Code**\
   Save the above code in a file named `locustfile.py`.
2. **Start Locust**\
   Open your terminal and run \``locust -f locustfile.py`\`
3. **Access the Web UI**
   * Open your browser and go to http://localhost:8089.
4. **Enter Test Parameters**
   * Number of users (e.g., 30).
   * Spawn rate (e.g., 5 users per second).
   * **Host**: If you are testing an actual API or website, specify its URL (e.g., `http://localhost:8000`).
5. **Analyze Results**
   * Observe how Locust spawns the users according to their weights and tracks metrics like request counts and response times.

After running the test:

* Check the **distribution of requests** to ensure it matches the weight ratio (e.g., for every 1 web user request, there should be \~3 mobile user requests).
* Use the metrics (response time, failure rate) to evaluate performance for each user type.
