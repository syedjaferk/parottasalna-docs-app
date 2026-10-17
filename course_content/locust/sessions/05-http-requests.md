# Session 5 · Testing a web service with HttpUser

## The big idea

`HttpUser` is a user that comes with an HTTP **client** (`self.client`). Every request you send through it is
timed and recorded in the results, so a load test is just a script of the requests a real person would make:
log in once, then browse, look at a profile, place an order.

**Everyday example:** a mystery shopper. A company sends someone into its own stores to walk in, ask for help,
buy something and time every step. `HttpUser` is a mystery shopper for your website, and Locust sends hundreds of
them at once.

```{raw} html
:file: ../diagrams/locust-http.html
```

## A shopper script

```{literalinclude} ../code/05_http.py
:language: python
```

- **`on_start`** logs in once and keeps the token in the client's headers, so every later request is authenticated.
- **Weights** 5, 3, 2, 1 make browsing the common action and ordering the rare one.
- **`name="/products/[id]"`** groups `/products/1`, `/products/2` and `/products/3` into one row. Without it you
  would get a separate row per URL, which is unreadable for ids.
- **`json=`** sends a JSON body with the right header.

Run it: 5 users for 8 seconds against the practice shop.

```bash
python shop_server.py &
locust -f 05_http.py --headless -u 5 -r 5 -t 8s --host http://127.0.0.1:8765 --only-summary --loglevel WARNING
```

```{literalinclude} ../code/05_http.out
:language: text
```

## Reading the results table

| Column | Meaning |
|---|---|
| `# reqs` | How many requests were made |
| `# fails` | How many failed (error status or exception) |
| `Avg Min Max Med` | Response times in milliseconds |
| `req/s` | Throughput |

Notice the shape of the numbers. `/login` ran 5 times, once per user, because it is in `on_start`. `/products` has the
most requests because it has the highest weight. Every request here took a few milliseconds because the shop
runs on the same machine. Over a real network, times are far larger.

**Failures.** Locust counts a request as failed when the status code is 400 or above, or the connection breaks.
All 161 requests succeeded here. The next session shows how to define "failed" yourself.

## Web UI or headless?

Leave out `--headless` and open `http://localhost:8089`: a web page lets you type the users, spawn rate and host
and shows live charts. Headless suits scripts and CI because it prints the same table to the terminal.

## Common mistakes

- **Forgetting `--host`.** Without it, requests have no base URL and fail. Set `host = "..."` in the class or pass `--host`.
- **Not grouping dynamic URLs.** `/products/17`, `/products/18`... create thousands of rows. Use `name=`.
- **Logging in inside every task.** Use `on_start`.
- **Sending real credentials or real purchases to production.** Use test accounts and a safe environment.
- **Testing from the same machine as the server and trusting the numbers.** Local tests are good for learning
  and for checking scripts, not for capacity planning.

## Hands-on exercises

**Exercise 1.** Add a task that requests `/slow` with weight 1. What happens to the average response time?

<details class="solution"><summary>Solution</summary>

```python
@task(1)
def slow(self):
    self.client.get("/slow")
```

A new row `/slow` appears with an average near 300 ms, and the **aggregated** average rises because 300 ms
requests are mixed with 2 ms ones. Look at the per-row figures, not just the total.

</details>

**Exercise 2.** The `/profile` request is missing its token. What status code would you see, and how would Locust report it?

<details class="solution"><summary>Solution</summary>

The shop returns 401, which Locust counts as a failure, so `/profile` would show 100% in the `# fails` column. (Remove
the `Authorization` header from `on_start` and run it to see.)

</details>

**Exercise 3.** Why do `/orders` requests number far fewer than `/products` requests?

<details class="solution"><summary>Solution</summary>

Their task weights are 1 and 5, so a user picks `/products` five times for each `/orders`. In the run above the
counts were 15 and 79.

</details>

## Practice

Take the **Session 5 quiz**. The original pages on `HttpUser` and HTTP POST requests are in the reference section.
