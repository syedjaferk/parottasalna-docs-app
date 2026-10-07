# Load Testing with HTTP POST Requests in Locust

### Understanding HTTP POST in Load Testing

POST requests are used to send data to a server to create or update a resource. They are typically employed in scenarios like:

* Submitting forms
* Uploading files
* Sending data to APIs for storage or processing

For load testing, simulating POST requests helps evaluate how well an application handles concurrent writes and ensures data integrity under high loads.

### Example: Performing POST Requests with Locust

Below is an example of a Locust `HttpUser` class that performs both GET and POST requests

```python
from locust import HttpUser, constant, task
import uuid


class MyReqRes(HttpUser):

    wait_time = constant(1)  # Wait 1 second between tasks
    host = "http://localhost:8001"  # Base URL for the API

    @task
    def get_todos(self):
        # GET request to retrieve a specific todo item
        res = self.client.get("/todos/104")
        print(res.text)

    @task
    def create_todos(self):
        # Generate a unique ID and create a todo item
        request = {
            "id": str(uuid.uuid4()),
            "name": "Meet at 9 AM",
            "description": "Need to meet client at 9 AM tomorrow"
        }
        # POST request to create a new todo
        res = self.client.post("/todos", json=request)
        print(res.text)

```

#### Explanation of the Code

**1. `MyReqRes` Class**

This class defines the user behavior, combining both GET and POST requests.

* **`HttpUser` Base Class:**\
  Provides built-in methods like `get` and `post` for HTTP requests.
* **`wait_time`:**\
  The `constant(1)` function ensures the user waits 1 second between tasks.
* **`host`:**\
  Sets the base URL for the API.

**2. `create_todos` Task**

This task simulates creating a new "todo" item:

* **Dynamic Data with `uuid`:**\
  A unique ID is generated for each request using Python’s `uuid` module.
* **Payload (`request`):**\
  Contains data to be sent to the server, including an ID, name, and description.
* **POST Request:**\
  The `self.client.post` method sends the payload as JSON to the `/todos` endpoint.

**3. `get_todos` Task**

This task retrieves an existing "todo" item to validate the GET functionality.
