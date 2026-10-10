# Session 13 · Async Python for AI apps

## The big idea

Most time in an AI app is spent **waiting**: for the LLM, an API, the database. Normal Python waits
for each one before starting the next. **Async** Python starts the next job while the first is
still waiting, so three 2-second calls take about 2 seconds, not 6.

**Everyday example:** making breakfast. You don't stand watching the kettle and only then start the
toast. You switch the kettle on, put the bread in, and both finish at about the same time.

## Breakfast, both ways

Synchronous (`1.app.sync.py`): toast takes 3 s, tea takes 3 s.

```text
Toasting bread...
Toast is ready!
Boiling water...
Tea is ready!
real 0m6.0s
```

Async (`1.app.py`): toast 2 s, tea 3 s, started together.

```python
async def make_tea():
    print("Boiling water...")
    await asyncio.sleep(3)          # "I'm waiting, do something else meanwhile"
    print("Tea is ready!")

async def main():
    await asyncio.gather(make_toast(), make_tea())

asyncio.run(main())
```

```text
Toasting bread...
Boiling water...
Toast is ready!
Tea is ready!
real 0m3.0s
```

Total time = the **longest** job, not the sum.

## The three words you need

| Word | Meaning |
|---|---|
| `async def` | this function can pause; calling it gives a *coroutine* (a job not started yet) |
| `await` | run this job, and while it waits, let other jobs run |
| `asyncio.run(main())` | start the event loop (the "kitchen") and run `main` until done |

## `await` one by one is still slow

`3.sequential_async.py` uses async functions, but awaits them **one after another**:

```python
await task("Task 1", 2)
await task("Task 2", 2)
await task("Task 3", 2)
```

```text
Total time: 6.01 seconds
```

`4.gather.py` starts them **together**:

```python
await asyncio.gather(task("Task 1", 2), task("Task 2", 2), task("Task 3", 2))
```

```text
Task 1 started
Task 2 started
Task 3 started
Task 1 completed
Task 2 completed
Task 3 completed
Total time: 2.00 seconds
```

```{raw} html
:file: ../diagrams/s13-async.html
```

`gather` returns the results **in the order you passed them**, even if they finish in another order
(`5.gather_return_values.py`):

```python
user, orders, products = await asyncio.gather(get_user(), get_orders(), get_products())
```

## Real work: HTTP calls and LLMs

- **HTTP:** use an async client. `requests` is blocking; `httpx.AsyncClient` isn't
  (`6.api_call.py`):

  ```python
  async with httpx.AsyncClient() as client:
      results = await asyncio.gather(*(fetch(client, url) for url in urls))
  ```

- **LangChain:** every model and agent has async versions: `ainvoke`, `astream`, `abatch`
  (`7.lc_query.py`):

  ```python
  response = await llm.ainvoke("What is LangChain in one sentence?")
  ```

- **Agents in parallel** (`8.crm.py`): three weather questions answered at once:

  ```python
  results = await asyncio.gather(
      agent.ainvoke({"messages": [{"role": "user", "content": "Weather in Chennai?"}]}),
      agent.ainvoke({"messages": [{"role": "user", "content": "Weather in Bangalore?"}]}),
      agent.ainvoke({"messages": [{"role": "user", "content": "Weather in Mumbai?"}]}),
  )
  ```

## Async APIs with FastAPI

`api/app_sync.py` and `api/app.py` are the same agent behind a `/chat` endpoint. The only
difference:

```python
def chat(req: ChatRequest):                         # app_sync.py
    response = agent.invoke(...)

async def chat(req: ChatRequest):                   # app.py
    response = await agent.ainvoke(...)
```

Start one of them, then send three requests at once with the load scripts:

```bash
cd api
uvicorn app:app --port 8000          # or app_sync:app
python load.py                       # 3 requests at the same time
python load_sync.py                  # 3 requests one after another
```

With the async server, three requests at once finish in about the time of one. (FastAPI runs plain
`def` endpoints in a thread pool, so the sync version also handles a few requests at once. Async
scales much further, because waiting costs almost nothing.)

## Common mistakes

- **Calling a blocking function inside `async def`.** `time.sleep(3)`, `requests.get(...)` or a
  synchronous database call freezes **every** job, not just this one. Use `asyncio.sleep`, `httpx`,
  async drivers, or `await asyncio.to_thread(blocking_function, ...)`.
- **Forgetting `await`.** `llm.ainvoke("hi")` without `await` gives a coroutine object and a
  warning, never an answer.
- **`asyncio.run()` inside an already-running loop** (Jupyter, FastAPI). There, just `await`.
- **Gathering 1,000 LLM calls at once.** You'll hit the provider's rate limit. Limit the number in
  flight with `asyncio.Semaphore(5)`.

## Hands-on exercises

Try each one before opening the solution.

**Exercise 1 · One blocking call.** Change `make_toast` in `1.app.py` to use `time.sleep(2)` instead
of `await asyncio.sleep(2)` (and `import time`). The total jumps from 3 to 5 seconds. Why?

<details class="solution"><summary>Answer</summary>

`time.sleep` blocks the whole event loop: nothing else can run during those 2 seconds, so the tea
can't even start boiling. Toast (2 s) and then tea (3 s) gives 5 s. One blocking call ruins the
concurrency of everything.

</details>

**Exercise 2 · Errors in gather.** Make `get_orders` raise an exception. What does `gather` do? Then
add `return_exceptions=True`.

<details class="solution"><summary>Answer</summary>

By default the exception propagates out of `await asyncio.gather(...)` and you lose the other results.
With `return_exceptions=True`, `gather` returns the exception object in that slot:

```python
user, orders, products = await asyncio.gather(get_user(), get_orders(), get_products(),
                                              return_exceptions=True)
if isinstance(orders, Exception):
    print("orders failed:", orders)
```

</details>

**Exercise 3 · Limit concurrency.** Fetch 10 URLs, at most 3 at a time.

<details class="solution"><summary>Solution</summary>

```python
limit = asyncio.Semaphore(3)

async def fetch(client, url):
    async with limit:                       # only 3 coroutines get past this at once
        response = await client.get(url)
        return response.status_code
```

Use the same pattern for LLM calls, so you stay under the provider's rate limit.

</details>

**Exercise 4 · Sync vs async server.** Time `load.py` against `api/app.py` and against
`api/app_sync.py`.

<details class="solution"><summary>What to notice</summary>

Against `app.py`, three requests take about as long as the slowest one. `app_sync.py` also handles
them at the same time (FastAPI runs plain `def` endpoints in a thread pool), so the gap is small with
3 requests. It grows with many requests: threads are limited (40 by default), coroutines are cheap.
`load_sync.py` is slow against both, because the **client** sends one at a time.

</details>

**Exercise 5 · Timeouts.** Give every LLM call 10 seconds at most.

<details class="solution"><summary>Solution</summary>

```python
try:
    response = await asyncio.wait_for(llm.ainvoke(question), timeout=10)
except asyncio.TimeoutError:
    response = None
    print("The model took too long, try again")
```

</details>

**Exercise 6 · as_completed.** Print each agent's answer in `8.crm.py` as soon as it's ready, not all
at the end.

<details class="solution"><summary>Solution</summary>

```python
tasks = [agent.ainvoke({"messages": [{"role": "user", "content": f"Weather in {city}?"}]})
         for city in ["Chennai", "Bangalore", "Mumbai"]]
for next_done in asyncio.as_completed(tasks):
    result = await next_done
    print(result["messages"][-1].content)
```

</details>

## Full source

<details class="source">
<summary>1.app.py and 1.app.sync.py</summary>

```{literalinclude} ../code/13-async/1.app.py
:language: python
```

```{literalinclude} ../code/13-async/1.app.sync.py
:language: python
```

</details>

<details class="source">
<summary>8.crm.py · three agents in parallel</summary>

```{literalinclude} ../code/13-async/8.crm.py
:language: python
```

</details>

<details class="source">
<summary>api/app.py</summary>

```{literalinclude} ../code/13-async/api/app.py
:language: python
```

</details>

<details class="source">
<summary>api/load.py</summary>

```{literalinclude} ../code/13-async/api/load.py
:language: python
```

</details>

**Downloads:**
{download}`1.app.sync.py <../code/13-async/1.app.sync.py>` ·
{download}`1.app.py <../code/13-async/1.app.py>` ·
{download}`2.py <../code/13-async/2.py>` ·
{download}`3.sequential_async.py <../code/13-async/3.sequential_async.py>` ·
{download}`4.gather.py <../code/13-async/4.gather.py>` ·
{download}`5.gather_return_values.py <../code/13-async/5.gather_return_values.py>` ·
{download}`6.api_call.py <../code/13-async/6.api_call.py>` ·
{download}`7.lc_query.py <../code/13-async/7.lc_query.py>` ·
{download}`8.crm.py <../code/13-async/8.crm.py>` ·
{download}`api/app.py <../code/13-async/api/app.py>` ·
{download}`api/app_sync.py <../code/13-async/api/app_sync.py>` ·
{download}`api/load.py <../code/13-async/api/load.py>` ·
{download}`api/load_sync.py <../code/13-async/api/load_sync.py>` ·
{download}`env.example <../code/13-async/env.example>`
