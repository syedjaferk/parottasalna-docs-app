# HTTP Load Testing with Locust's HttpUser

Locust makes load testing web applications intuitive and efficient, thanks to its specialized `HttpUser` class. The `HttpUser` class provides built-in methods for HTTP interactions like `GET`, `POST`, `PUT`, and `DELETE`, making it an excellent choice for API and web application performance testing.

In this chapter, we’ll explore how to use the `HttpUser` class to perform HTTP GET requests with a simple example that tests a `/todos` endpoint.

### What Is `HttpUser`?

The `HttpUser` class in Locust is a specialized user class designed for HTTP-based load testing. It includes the following features:

* A built-in HTTP client for making requests.
* Easy-to-use methods like `get`, `post`, and `put` for testing API endpoints.
* Support for handling headers, query parameters, and payloads.

By extending `HttpUser`, you can create users that simulate HTTP-based workflows for your application.

### Example: HTTP GET Request with `HttpUser`

Here’s a simple example of an `HttpUser` that performs a `GET` request to retrieve a specific "todo" item from an API

```python
from locust import HttpUser, constant, task

class MyReqRes(HttpUser):
    wait_time = constant(1)  # Wait 1 second between tasks
    host = "http://localhost:8001"  # Base URL for the API

    @task
    def get_todos(self):
        # Send a GET request to the "/todos/104" endpoint
        res = self.client.get("/todos/104")
        # Print the response text to the console
        print(res.text)

```

#### Explanation of the Code

**1. `MyReqRes` Class**

This class defines the behavior of a simulated user interacting with an API.

* **`HttpUser` Base Class:**\
  Provides an HTTP client (`self.client`) for making requests.
* **`wait_time`:**\
  The `constant(1)` function ensures the user waits 1 second between tasks.
* **`host`:**\
  Sets the base URL for the API. All requests made by this user will use this host.

**2. `get_todos` Task**

This task sends a `GET` request to the `/todos/104` endpoint. The response is printed to the console using `print(res.text)`.

### Enhancing the Example: Error Handling

To make the test more robust, you can include error handling to capture non-200 responses

```python
from locust import HttpUser, constant, task

class MyReqRes(HttpUser):
    wait_time = constant(1)
    host = "http://localhost:8001"

    @task
    def get_todos(self):
        res = self.client.get("/todos/104")
        if res.status_code == 200:
            print(f"Success: {res.text}")
        else:
            print(f"Error {res.status_code}: {res.text}")
```

This ensures you’re informed about any issues during the test.

### Adding Headers and Query Parameters

Locust’s HTTP client supports headers and query parameters, allowing you to test endpoints that require authentication or additional parameters. For example,

```python
@task
def get_todos_with_params(self):
    headers = {"Authorization": "Bearer YOUR_TOKEN"}
    params = {"completed": "false"}
    res = self.client.get("/todos", headers=headers, params=params)
    print(res.text)

```

The `HttpUser` class in Locust is a powerful tool for load testing HTTP APIs. By using simple methods like `get` and `post`, you can simulate realistic user interactions with your application. Whether you’re testing a REST API or a web application backend, `HttpUser` provides the flexibility and ease of use to design and execute effective load tests.
