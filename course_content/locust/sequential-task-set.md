# Sequential Task Set

In load testing, some scenarios require tasks to be executed in a specific sequence to mimic real-world workflows. Locust addresses this need with the `SequentialTaskSet`, allowing you to define tasks that follow a set order. This contrasts with the default `TaskSet`, where tasks are chosen randomly based on their weights.

In this chapter, we’ll explore how to use `SequentialTaskSet` with an example to create a realistic load-testing scenario.

### What Is `SequentialTaskSet`?

The `SequentialTaskSet` class in Locust is a specialized version of the `TaskSet`. It ensures that tasks are executed sequentially, one after the other, in the order they are defined. This is ideal for scenarios like:

* Simulating multi-step workflows (e.g., login, browse, add to cart, checkout).
* Testing APIs with a fixed sequence of calls.

### Example: Sequential Task Execution

Here’s an example that demonstrates the use of `SequentialTaskSet`

```python
from locust import User, SequentialTaskSet, task, constant

class RandomOrderTasks(SequentialTaskSet):
    @task(2)
    def task_one(self):
        print("Task one")

    @task(1)
    def task_two(self):
        print("Task two")

    @task(3)
    def task_three(self):
        print("Task three")

class MyUser(User):
    tasks = [RandomOrderTasks]
    wait_time = constant(1)

```

### Explanation of the Code

**1. `RandomOrderTasks` Class**

This class defines the sequence of tasks to be executed by a simulated user. The key points are:

* **`@task` Decorator:**\
  Each method in the class is marked with the `@task` decorator, making it part of the task sequence.
  * The argument (e.g., `@task(2)`) specifies the **weight** of the task. However, in a `SequentialTaskSet`, weights are ignored, and tasks are executed strictly in the order they appear.
* **Defined Tasks:**
  * `task_one`: Prints "Task one".
  * `task_two`: Prints "Task two".
  * `task_three`: Prints "Task three".

**2. `MyUser` Class**

This class represents the user behavior:

* **`tasks` Attribute:**\
  Assigns the `RandomOrderTasks` as the set of tasks for the user.
* **`wait_time` Attribute:**\
  Specifies a fixed wait time of 1 second between each task using `constant(1)`.

### Benefits of `SequentialTaskSet`

1. **Realistic Testing:**\
   Represents real-world user behavior more accurately compared to randomly ordered tasks.
2. **Control Over Task Flow:**\
   Ensures tasks are executed in the desired order, which is critical for workflows with dependencies.
3. **Simplicity:**\
   Easy to define and understand, even for complex workflows.

#### Enhancing Sequential Task Sets with Custom Logic

You can extend the functionality of `SequentialTaskSet` by overriding its `on_start` and `on_stop` methods

```python
from locust import SequentialTaskSet, User, task, constant

class Workflow(SequentialTaskSet):
    def on_start(self):
        print("Starting the workflow")
    
    @task
    def step_one(self):
        print("Step one completed")
    
    @task
    def step_two(self):
        print("Step two completed")
    
    def on_stop(self):
        print("Workflow completed")

class MyUser(User):
    tasks = [Workflow]
    wait_time = constant(1)

```

In this example:

* `on_start` runs once before the first task.
* `on_stop` runs after the last task, signaling the end of the workflow.
