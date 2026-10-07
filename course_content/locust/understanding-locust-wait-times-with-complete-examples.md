# Understanding Locust Wait Times with Complete Examples

In this chapter, we’ll cover,

1. What wait times are in Locust.
2. Built-in wait time options.
3. Creating custom wait times.
4. A full example with instructions to run the test.

### What Are Wait Times in Locust?

In real-world scenarios, users don’t interact with applications continuously. After performing an action (e.g., submitting a form), they often pause before the next action. This pause is called a **wait time** in Locust, and it plays a crucial role in mimicking real-life user behavior.

Locust provides several ways to define these wait times within your test scenarios.

### FastAPI App Overview

Here’s the FastAPI app that we’ll test,

```python
from fastapi import FastAPI

# Create a FastAPI app instance
app = FastAPI()

# Define a route with a GET method
@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

```



### **1. Constant Wait Time Example**

Here, we’ll simulate constant pauses between user requests

```python
from locust import HttpUser, task, constant

class FastAPIUser(HttpUser):
    wait_time = constant(2)  # Wait for 2 seconds between requests

    @task
    def get_root(self):
        self.client.get("/")  # Simulates a GET request to the root endpoint

    @task
    def get_item(self):
        self.client.get("/items/42?q=test")  # Simulates a GET request with path and query parameters

```

### **2. Between wait time Example**

Simulating random pauses between requests.

```python
from locust import HttpUser, task, between

class FastAPIUser(HttpUser):
    wait_time = between(1, 5)  # Random wait time between 1 and 5 seconds

    @task(3)  # Weighted task: this runs 3 times more often
    def get_root(self):
        self.client.get("/")

    @task(1)
    def get_item(self):
        self.client.get("/items/10?q=locust")

```

### **3. Custom Wait Time Example**

Using a custom wait time function to introduce more complex user behavior

```python
import random
from locust import HttpUser, task

def custom_wait():
    return max(1, random.normalvariate(3, 1))  # Normal distribution (mean: 3s, stddev: 1s)

class FastAPIUser(HttpUser):
    wait_time = custom_wait

    @task
    def get_root(self):
        self.client.get("/")

    @task
    def get_item(self):
        self.client.get("/items/99?q=custom")


```

### Full Test Example

Combining all the above elements, here’s a complete Locust test for your FastAPI app.

```python
from locust import HttpUser, task, between
import random

# Custom wait time function
def custom_wait():
    return max(1, random.uniform(1, 3))  # Random wait time between 1 and 3 seconds

class FastAPIUser(HttpUser):
    wait_time = custom_wait  # Use the custom wait time

    @task(3)
    def browse_homepage(self):
        """Simulates browsing the root endpoint."""
        self.client.get("/")

    @task(1)
    def browse_item(self):
        """Simulates fetching an item with ID and query parameter."""
        item_id = random.randint(1, 100)
        self.client.get(f"/items/{item_id}?q=test")

```

### Running Locust for FastAPI

1. **Run Your FastAPI App**\
   Save the FastAPI app code in a file (e.g., `main.py`) and start the server. By default, the app will run on `http://127.0.0.1:8000`.

```bash
uvicorn main:app --reload
```

2. **Run Locust**\
   Save the Locust file as `locustfile.py` and start Locust.

```bash
locust -f locustfile.py
```

3\. **Configure Locust**\
Open http://localhost:8089 in your browser and enter:

* **Host**: `http://127.0.0.1:8000`
* **Number of users** and **spawn rate** based on your testing requirements.

**4. Run in Headless Mode** (Optional)\
Use the following command to run Locust in headless mode

```bash
locust -f locustfile.py --headless -u 50 -r 10 --host http://127.0.0.1:8000
```

`-u 50`: Simulate 50 users.

`-r 10`: Spawn 10 users per second.
