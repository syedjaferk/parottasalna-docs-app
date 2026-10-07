# @task decorator

A key feature of Locust is the `@task` decorator, which allows you to define the specific actions (or tasks) your simulated users will perform.

n this chapter, we’ll dive into the `@task` decorator and illustrate its use with an example that prints the current date and time, along with a friendly greeting.

### What Is the `@task` Decorator?

The `@task` decorator in Locust is used to mark methods in a `User` class as tasks to be executed during a load test. Each method decorated with `@task` represents an action that the simulated user will perform.

Locust automatically identifies these tasks and executes them based on the configuration you define, such as the **wait time** between tasks or their relative weighting.

### Example: Printing DateTime and a Greeting

Here’s a simple example of a Locust `User` class with two tasks: printing the current date and time and printing a greeting message.

```python
from locust import User, task, between
from datetime import datetime

class MyUser(User):
    # Defines the wait time between tasks to be a random value between 1 and 5 seconds.
    wait_time = between(1, 5)

    @task
    def print_datetime(self):
        # This task prints the current date and time.
        print(datetime.now())
    
    @task
    def print_greeting(self):
        # This task prints a greeting message.
        print("Hello!")

```

#### Explanation of the Code

1. **`MyUser` Class**\
   This class represents the behavior of a simulated user. Every simulated user will execute the tasks defined in this class.
2. **`wait_time`**\
   The `wait_time` attribute determines how long a user will wait before executing the next task.
   * Here, `between(1, 5)` specifies a random delay between 1 and 5 seconds.
3. **Task Methods**
   * `print_datetime`: Prints the current date and time using Python's `datetime.now()`.
   * `print_greeting`: Prints the message `"Hello!"`.
4. **`@task` Decorator**\
   The `@task` decorator marks the methods `print_datetime` and `print_greeting` as tasks for the simulated users.

### Fine-Tuning Tasks with Weights

You can adjust the relative frequency of tasks using weights. For instance:
