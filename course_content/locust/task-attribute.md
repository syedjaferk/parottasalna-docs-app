# task attribute

In this blog, we’ll explore what `task_attribute` is, why it’s useful, and how to use it effectively in your Locust tests.

#### What Is `task_attribute`?

The `task_attribute` is a property of tasks in Locust. It is used to store metadata or additional information about a task, making it easier to manage, analyze, or document tasks. You can attach custom attributes to tasks for purposes like:

* Tracking execution details
* Adding task descriptions
* Tagging tasks for categorization

Unlike static annotations, `task_attribute` enables dynamic configuration, which is particularly helpful when tasks are generated programmatically.

### Use Cases for `task_attribute`

Here are some scenarios where `task_attribute` can enhance your load testing:

1. **Dynamic Task Configuration:**\
   Attach metadata to tasks, such as API endpoints or expected response times.
2. **Task Documentation:**\
   Provide descriptions or tags for better understanding and reporting.
3. **Custom Logging and Analysis:**\
   Log task attributes during execution for advanced analysis.
4. **Scenario Management:**\
   Categorize tasks for specific user scenarios in complex applications.

### Example: Using `task_attribute`

Below is a simple example that demonstrates how to set and use `task_attribute`

```python
from locust import User, TaskSet, task

class MyTaskSet(TaskSet):
    # Define tasks with dynamic attributes
    @task
    def task_one(self):
        print("Executing Task One")
    task_one.task_attribute = {"description": "This is Task One", "priority": 1}

    @task
    def task_two(self):
        print("Executing Task Two")
    task_two.task_attribute = {"description": "This is Task Two", "priority": 2}

class MyUser(User):
    tasks = [MyTaskSet]

```

### Explanation of the Code

1. **Defining Tasks**\
   The `task_one` and `task_two` methods are standard Locust tasks marked with the `@task` decorator.
2. **Adding Attributes**\
   Custom attributes are attached to tasks using `task_attribute`. For instance:
   * `task_one` is labeled with a description and a priority level.
3. **Dynamic Metadata**\
   The metadata can be referenced or logged during test execution, providing additional insights.

### Accessing `task_attribute` at Runtime

You can access a task’s `task_attribute` dynamically within the test run, for example

```python
for task in MyTaskSet.tasks:
    if hasattr(task, "task_attribute"):
        print(f"Task: {task.__name__}, Metadata: {task.task_attribute}")
```

This outputs the task name and its attributes, making it easy to analyze your test configuration.
