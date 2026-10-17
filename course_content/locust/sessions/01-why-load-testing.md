# Session 1 · Why load testing, and installing Locust

## The big idea

A website that works for you alone may fall over when a thousand people use it at once. **Load testing**
means sending realistic traffic at your service on purpose, *before* real users do, and measuring what
happens: how fast it answers, how many requests per second it handles, and when it starts to fail.
**Locust** is a free tool where you describe the users in plain Python.

**Everyday example:** a wedding hall booked for 500 guests. You would not wait for the wedding day to find out
that the kitchen can only serve 200 plates an hour. A caterer does a trial run with 500 imaginary guests first,
notes where the queue forms, and fixes it. Load testing is that trial run for your server.

```{raw} html
:file: ../diagrams/load-idea.html
```

## The questions a load test answers

- Can the service handle the **expected** traffic (say, 500 users at once)?
- How does performance **degrade** as traffic grows?
- Where is the **breaking point**, and what breaks first (the app, the database, the network)?

Real examples: a shop before a sale day, a streaming service before a launch, a trading app at market open.
In each case a slow checkout or a dropped video is lost money.

## The numbers to watch

| Metric | Meaning | Rule of thumb |
|---|---|---|
| Response time | How long one request takes | Many sites aim for under 2 s |
| Throughput (requests/s) | How many requests are served per second | Higher is better, until errors start |
| Error rate | Share of requests that fail | Should stay near 0% |
| Percentiles (p95, p99) | The time that 95% or 99% of requests beat | Shows the slow tail that averages hide |
| Concurrent users | How many users act at the same time | The load you chose |

An **average** of 200 ms can hide the fact that 1 request in 20 takes 5 seconds. Always look at p95 and p99 too.

## Install Locust

```{literalinclude} ../code/01_install.sh
:language: bash
```

```{literalinclude} ../code/01_install.out
:language: text
```

Use a virtual environment (`python -m venv .venv`) if you like. The version above is what every example in
this course was run with. Locust has two ways to run: with a **web page** (`locust -f file.py`, then open
`http://localhost:8089`) or **headless** from the command line, which this course uses because it prints results you can read.

## The practice shop

All sessions test one small web shop that runs on your own computer, so you can load test freely without
harming anyone. `code/shop_server.py` uses only Python's standard library:

```bash
python shop_server.py        # listens on http://127.0.0.1:8765
```

| URL | Does |
|---|---|
| `GET /products`, `GET /products/<id>` | Product list and detail |
| `POST /login` | Returns a token for user `demo` / password `secret` |
| `GET /profile` | Needs the token |
| `POST /orders` | Places an order |
| `GET /slow` | Takes 0.3 s on purpose |
| `GET /flaky` | Fails with a 500 every fourth time |

## Common mistakes

- **Load testing someone else's website.** That can look like an attack and may be illegal. Test your own
  systems, or ones you have written permission for.
- **Testing the laptop instead of the service.** If your computer is the bottleneck, the numbers mean nothing.
  Watch your own CPU (Session 8 shows how to add workers).
- **Reading only the average.** Check percentiles and the error rate.
- **Testing on production by surprise.** Use a staging copy, or warn the team and pick a quiet time.
- **One test, then done.** Performance changes with every release; repeat the test regularly.

## Hands-on exercises

**Exercise 1.** Install Locust in a virtual environment and print its version.

<details class="solution"><summary>Solution</summary>

```bash
python -m venv .venv
source .venv/bin/activate
pip install locust
locust --version
```

You see a line like `locust 2.28.0`. Your version may be newer.

</details>

**Exercise 2.** Start the practice shop and call one URL with `curl`.

<details class="solution"><summary>Solution</summary>

```bash
python shop_server.py &
curl -s http://127.0.0.1:8765/products/2
```

It prints `{"id": 2, "name": "Phone", "price": 500}`. Stop the server later with `kill %1`.

</details>

**Exercise 3.** A service averages 200 ms but its p99 is 6 seconds. Is it healthy? Why or why not?

<details class="solution"><summary>Solution</summary>

Not necessarily. 1 request in 100 takes about 6 seconds, which a busy user will meet often (a page may make
dozens of requests). The average hides this tail; the p95 and p99 reveal it.

</details>

## Practice

Take the **Session 1 quiz**. The original *Why Load Testing?* and *Locust Installation* pages are in the
reference section.
