# Load Testing with Locust

Load test web applications with Locust: users and tasks, wait times, events, HTTP requests, response validation, step load and distributed mode.

## How each session works

1. **The big idea**: the topic in plain words, with an everyday example.
2. **A picture**: a diagram of the idea.
3. **Real runs**: every test was run with Locust 2.28 against a small practice shop on your own computer, and the output you see is what it printed.
4. **Common mistakes**: what trips beginners up.
5. **Hands-on exercises**: try first, then open the solution.
6. **Practice**: a quiz for the session.

:::{important}
Only load test systems you own or have written permission to test. The practice shop in `code/shop_server.py` is
yours to hammer. Numbers such as requests per second differ on every computer and every run; look at the shape of the results.
:::

```{toctree}
:maxdepth: 1
:caption: Sessions

sessions/01-why-load-testing
sessions/02-tasks-weights-and-wait-times
sessions/03-user-types-and-task-order
sessions/04-lifecycle-hooks
sessions/05-http-requests
sessions/06-validating-responses
sessions/07-shaping-the-load
sessions/08-distributed-mode
```

```{toctree}
:maxdepth: 2
:caption: Original notes (reference)

Why Load Testing ? <introduction>
Locust Installation <locust-installation>
Understanding Locust Wait Times with Complete Examples <understanding-locust-wait-times-with-complete-examples>
Simulating Multiple User Types in Locust <simulating-multiple-user-types-in-locust>
Why on_start and on_stop are Essential for Locust Users <why-on_start-and-on_stop-are-essential-for-locust-users>
How to use test_start and test_stop Events in Locust <how-to-use-test_start-and-test_stop-events-in-locust>
@task decorator <task-decorator>
task attribute <task-attribute>
Sequential Task Set <sequential-task-set>
HTTP Load Testing with Locust's HttpUser <http-load-testing-with-locusts-httpuser>
Load Testing with HTTP POST Requests in Locust <load-testing-with-http-post-requests-in-locust>
Using catch_response in Locust for Custom Response Validation <using-catch_response-in-locust-for-custom-response-validation>
Iterative Load Testing with Step Size in Locust <iterative-load-testing-with-step-size-in-locust>
Enhancing Your Locust Tests with Custom Logging <enhancing-your-locust-tests-with-custom-logging>
Running Locust in Distributed Mode with Master and Workers <running-locust-in-distributed-mode-with-master-and-workers>
```
