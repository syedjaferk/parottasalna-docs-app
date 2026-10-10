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

## Try it yourself

1. Change `make_toast` in `1.app.py` to use `time.sleep(2)` instead of `await asyncio.sleep(2)`
   (and `import time`). The total jumps from 3 to 5 seconds. Why?
2. In `5.gather_return_values.py`, make `get_orders` raise an error. What does `gather` do? Then try
   `gather(..., return_exceptions=True)`.
3. Fetch 10 URLs with `6.api_call.py`, at most 3 at a time, using `asyncio.Semaphore(3)`.
4. Time `load.py` against `app.py` and against `app_sync.py`.
5. Add a timeout: `await asyncio.wait_for(llm.ainvoke(q), timeout=10)`.

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
