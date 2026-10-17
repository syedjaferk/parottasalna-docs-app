# Session 8 · Running Locust in distributed mode

## The big idea

One Locust process can only generate so much load before **your own computer** becomes the bottleneck. Python runs one
CPU core per process. For bigger tests you start one **master** (the coordinator) and several **workers** (the
load generators). The master splits the users between workers and adds up the results. The same locustfile runs everywhere.

**Everyday example:** a call centre. One supervisor (master) does not make all the calls. She hands out the call list
to several agents (workers), then collects everybody's results into one report. For ten times the calls, hire more agents.

```{raw} html
:file: ../diagrams/locust-distributed.html
```

## One master, two workers on this computer

The worker processes are started first (any number, anywhere that can reach the master); the master waits for them.

```bash
locust -f 05_http.py --worker                      # run twice, in two terminals
locust -f 05_http.py --master --expect-workers 2 --headless -u 6 -r 6 -t 8s --only-summary
```

Locust looks for the master on the same computer by default. From another computer, add `--master-host=<master-ip>`.
The master's output:

```{literalinclude} ../code/08_distributed.out
:language: text
```

Reading it from the top:

1. **Waiting for workers**: the master will not start until `--expect-workers 2` workers have connected.
2. Both workers say they are ready, then the master **sends the spawn jobs** of 6 users to the 2 ready workers, who share them.
3. **All users spawned: ShopUser: 6** confirms the total.
4. When the time limit is reached the workers quit, and the master prints one **combined table**, as if a single
   process had made all the requests.

## When do you need it?

| Situation | Do |
|---|---|
| Learning, small API, a few hundred users | One process is fine |
| Your CPU is at 100% while testing | Add workers (one per CPU core is a good start) |
| Need load from different regions | Run workers on machines in those regions |
| CI pipelines | Headless master with workers started by the pipeline |

The master itself should not be the busiest machine: keep it free to coordinate and gather stats.

## Common mistakes

- **Starting the master before the workers without `--expect-workers`.** The test begins with no load generators.
- **Workers with a different locustfile** than the master. Every process must use the same file.
- **Firewalls blocking the master's port (5557).** Workers cannot join. Open the port or use the same network.
- **Expecting more load from more workers when the server is already the bottleneck.** If the service is slow, adding
  workers just adds queueing.
- **Forgetting to count the generators.** When the load machine's CPU is above about 80%, results are unreliable.
- **Leaving workers running afterwards.** Stop them when the master finishes.

## Hands-on exercises

**Exercise 1.** How would you start 4 workers on a 4-core machine with a script?

<details class="solution"><summary>Solution</summary>

```bash
for i in 1 2 3 4; do locust -f 05_http.py --worker & done
locust -f 05_http.py --master --expect-workers 4 --headless -u 400 -r 40 -t 60s
```

Locust also offers `--processes 4`, which starts the workers for you on one machine.

</details>

**Exercise 2.** The master says "Waiting for workers to be ready, 1 of 2 connected" and never starts. What do you check?

<details class="solution"><summary>Solution</summary>

One worker has not connected: check that it was started, uses `--worker` with the correct `--master-host`, can reach
the master's port 5557 (firewall), and runs the same Locust version.

</details>

**Exercise 3.** You doubled the workers but the total requests per second did not change. Name two likely reasons.

<details class="solution"><summary>Solution</summary>

(1) The service under test is the bottleneck, so it cannot go faster however much load you send. (2) The users
spend most of their time waiting (`wait_time`) rather than sending, so adding workers without adding users
changes nothing. Check the server's CPU and the number of users.

</details>

## Practice

Take the **Session 8 quiz**. The original page *Running Locust in Distributed Mode* is in the reference section.
