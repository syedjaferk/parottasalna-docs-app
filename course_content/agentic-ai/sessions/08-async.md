# Session 8 · Async Python for AI Apps

## The big idea

Asking an AI model a question takes a few seconds, and almost all of that time your program is
just **waiting** for the reply to travel over the internet. Ask three questions one after another and
you wait three times. **Async** lets your program start all three and wait **once**.

**Everyday example:** making breakfast. You don't stand staring at the toaster for 3 minutes and
*then* put the kettle on. You start the toast, start the kettle, and wait for both together.

```{raw} html
:file: ../diagrams/s08-kitchen.html
```

## The normal (synchronous) way

```python
import time

def make_toast():
    print("Toasting bread...")
    time.sleep(3)              # stand and wait 3 seconds. Nothing else can happen.
    print("Toast is ready!")

def make_tea():
    print("Boiling water...")
    time.sleep(3)
    print("Tea is ready!")

make_toast()
make_tea()
```

**Output (6 seconds in total):**

```text
Toasting bread...
Toast is ready!        ← after 3s
Boiling water...
Tea is ready!          ← after 6s
```

## The async way

```python
import asyncio

async def make_toast():
    print("Toasting bread...")
    await asyncio.sleep(2)     # "I'm waiting, so do something else meanwhile"
    print("Toast is ready!")

async def make_tea():
    print("Boiling water...")
    await asyncio.sleep(3)
    print("Tea is ready!")

async def main():
    await asyncio.gather(make_toast(), make_tea())    # start both together

asyncio.run(main())
```

**Output (3 seconds in total):**

```text
Toasting bread...
Boiling water...       ← started straight away, didn't wait for the toast
Toast is ready!        ← after 2s
Tea is ready!          ← after 3s
```

## Four new words

| Word | In simple words |
|---|---|
| `async def` | "this function may pause while it waits" (it's called a **coroutine**) |
| `await` | "pause **here** until this is done, and let other work run meanwhile" |
| `asyncio.gather(...)` | "start all of these together and wait until they're all done" |
| `asyncio.run(main())` | "start the async engine and run `main()`" |

:::{warning}
**Never use `time.sleep()` inside `async def`.** It freezes everything, so nothing else can run.
Use `await asyncio.sleep()`. In general, inside async code use async libraries: `httpx` instead of
`requests`.
:::

## `await` one by one is still slow

This is the most common surprise. Writing `async` alone doesn't make things run together:

```python
async def task(name, seconds):
    print(f"{name} started")
    await asyncio.sleep(seconds)
    print(f"{name} completed")

async def main():
    await task("Task 1", 2)    # wait until finished...
    await task("Task 2", 2)    # ...then start this one
    await task("Task 3", 2)
```

```{raw} html
:file: ../diagrams/s08-gather.html
```

With `asyncio.gather(task("Task 1", 2), task("Task 2", 2), task("Task 3", 2))` all three start
together: **2 seconds** instead of 6.

## Getting results back

`gather()` returns the results **in the same order you listed the tasks**, no matter which finishes
first:

```python
async def get_user():     await asyncio.sleep(2); return "User"
async def get_orders():   await asyncio.sleep(3); return "Orders"
async def get_products(): await asyncio.sleep(1); return "Products"

user, orders, products = await asyncio.gather(get_user(), get_orders(), get_products())
print(user, orders, products)    # User Orders Products   ← after ~3 seconds, not 6
```

## Many web requests at once

`httpx.AsyncClient` is the async version of `requests`:

```python
import httpx

async def fetch(client, url):
    response = await client.get(url)
    return response.status_code

async def main():
    urls = ["https://example.com", "https://httpbin.org/get", "https://httpbin.org/uuid"]
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*(fetch(client, url) for url in urls))
    print(results)       # [200, 200, 200]
```

(`*( ... )` unpacks the list so each request becomes its own argument to `gather`.)

## Async AI calls

Every LangChain model and agent has an async version of its methods: just add an **a** in front.

| Normal | Async |
|---|---|
| `llm.invoke(...)` | `await llm.ainvoke(...)` |
| `llm.stream(...)` | `async for chunk in llm.astream(...)` |

```python
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

async def main():
    response = await llm.ainvoke("What is LangChain in one sentence?")
    print(response.content)
```

**Three agent questions at the same time:**

```python
agent = create_react_agent(model=llm, tools=[get_weather])

results = await asyncio.gather(
    agent.ainvoke({"messages": [{"role": "user", "content": "Weather in Chennai?"}]}),
    agent.ainvoke({"messages": [{"role": "user", "content": "Weather in Bangalore?"}]}),
    agent.ainvoke({"messages": [{"role": "user", "content": "Weather in Mumbai?"}]}),
)
for r in results:
    print(r["messages"][-1].content)     # the last message is the agent's final answer
```

**Streaming** (`astream`) sends the answer piece by piece, so users see words appearing instead of
a blank screen. It's the typing effect in ChatGPT.

## Putting an agent behind a web API

The `api/` folder turns the agent into a web service with **FastAPI**:

```python
app = FastAPI()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    response = await agent.ainvoke({"messages": [{"role": "user", "content": req.message}]})
    return ChatResponse(reply=response["messages"][-1].content)
```

Start the server in one terminal:

```bash
uvicorn app:app --reload
```

Then open <http://localhost:8000/docs> to try it in the browser, or send test traffic from another
terminal:

```bash
python load_sync.py     # sends 3 questions one after another
```

```bash
python load.py          # sends 3 questions at the same time
```

`load_sync.py` takes about the **sum** of the three replies; `load.py` takes about as long as the
**slowest** one.

:::{note}
**Where does the speed-up really come from?** Mostly from the **sender**: `load.py` sends all three
questions at once. On the **server** side, FastAPI already runs a plain `def` endpoint in a pool of
threads, so `app_sync.py` can also handle a few requests at once. The `async def` version
(`app.py`) handles waiting more efficiently, which matters when **hundreds** of users wait on slow
AI calls at the same time.

The real mistake to avoid: calling slow, non-async code (`agent.invoke`, `requests.get`,
`time.sleep`) **inside** an `async def` endpoint. That freezes the server for everyone.
:::

## Try it yourself

1. Write `fetch_all(urls)` that returns `{url: status_code}` for a list of URLs, all fetched at once.
2. Time 5 questions to `llm.ainvoke` with `gather`, then 5 with a normal `for` loop and
   `llm.invoke`. How much faster is `gather`?
3. In `gather`, make one task raise an error. What happens? Now add `return_exceptions=True`. What
   changes?

## Full source

<details class="source"><summary>1.app.sync.py: the synchronous kitchen</summary>

```{literalinclude} ../code/08-async/1.app.sync.py
:language: python
```

</details>

<details class="source"><summary>1.app.py: the async kitchen</summary>

```{literalinclude} ../code/08-async/1.app.py
:language: python
```

</details>

<details class="source"><summary>2.py: your first coroutine</summary>

```{literalinclude} ../code/08-async/2.py
:language: python
```

</details>

<details class="source"><summary>3.sequential_async.py</summary>

```{literalinclude} ../code/08-async/3.sequential_async.py
:language: python
```

</details>

<details class="source"><summary>4.gather.py</summary>

```{literalinclude} ../code/08-async/4.gather.py
:language: python
```

</details>

<details class="source"><summary>5.gather_return_values.py</summary>

```{literalinclude} ../code/08-async/5.gather_return_values.py
:language: python
```

</details>

<details class="source"><summary>6.api_call.py</summary>

```{literalinclude} ../code/08-async/6.api_call.py
:language: python
```

</details>

<details class="source"><summary>7.lc_query.py</summary>

```{literalinclude} ../code/08-async/7.lc_query.py
:language: python
```

</details>

<details class="source"><summary>8.crm.py: concurrent agent calls</summary>

```{literalinclude} ../code/08-async/8.crm.py
:language: python
```

</details>

<details class="source"><summary>api/app.py: async endpoint</summary>

```{literalinclude} ../code/08-async/api/app.py
:language: python
```

</details>

<details class="source"><summary>api/app_sync.py: sync endpoint</summary>

```{literalinclude} ../code/08-async/api/app_sync.py
:language: python
```

</details>

<details class="source"><summary>api/load.py: concurrent load test</summary>

```{literalinclude} ../code/08-async/api/load.py
:language: python
```

</details>

<details class="source"><summary>api/load_sync.py: sequential load test</summary>

```{literalinclude} ../code/08-async/api/load_sync.py
:language: python
```

</details>
