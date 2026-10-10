# Session 16 · Tools, function calling and MCP

## The big idea

Tools are what turn a chatbot into an **agent**: functions it can ask to use, such as a
calculator, a weather API or a database. The key fact: **the LLM never runs your function.** It
only replies with a structured request ("please call `multiply(a=12, b=7)`"). **Your code** runs
it and sends the result back. An *agent* is simply that loop, repeated until the model has its
answer.

**MCP** (Model Context Protocol) is a standard way to **share tools between programs**: write a tool
server once, and any MCP-aware app (your LangChain agent, Claude Desktop, an IDE) can use it.

**Everyday example:** a manager and an assistant. The manager (LLM) says "call the bank and check
the balance"; the assistant (your code) makes the call and reports back; the manager decides what
to do next.

## 1 · Function calling, step by step

`1_function_calling.py` shows what agents do under the hood:

```python
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b

llm_with_tools = model.bind_tools([add, multiply])    # sends name + description + JSON schema
ai_msg = llm_with_tools.invoke("What is 12 multiplied by 7 ?. Use the provided tools if present. ")
print(ai_msg.content)       # ''  (usually empty)
print(ai_msg.tool_calls)    # [{'name': 'multiply', 'args': {'a': 12, 'b': 7}, 'id': '...'}]
```

The manual loop: call the model, run whatever tools it asks for, feed the results back, and stop
when it asks for none:

```python
while True:
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)
    if not ai_msg.tool_calls:
        break                                            # final answer
    for call in ai_msg.tool_calls:
        tool_msg = tools_by_name[call["name"]].invoke(call)   # run it → ToolMessage
        messages.append(tool_msg)
```

A typical run:

```text
-> model wants multiply({'a': 12, 'b': 7})
<- result: 84
-> model wants add({'a': 84, 'b': 5})
<- result: 89
FINAL ANSWER: 89
```

```{raw} html
:file: ../diagrams/s16-tool-loop.html
```

Compare with ReAct in [Session 2](02-reasoning-prompts.md): the same idea, but the tool call is
structured data instead of text we had to parse.

## 2 · Three ways to define a tool

`2_custom_tools.py`:

| Way | Code | Use it when |
|---|---|---|
| `@tool` | docstring = description, type hints = arguments | most of the time |
| `@tool(args_schema=...)` | a Pydantic model with `Field(description=…, gt=0)` | you want validation and per-argument descriptions |
| `StructuredTool.from_function` | wrap an existing function | the function is from a library you can't decorate |

```python
class DiscountInput(BaseModel):
    price: float = Field(gt=0, description="Original price of the item")
    percent: float = Field(ge=0, le=100, description="Discount percentage, 0-100")

@tool("apply_discount", args_schema=DiscountInput)
def apply_discount(price: float, percent: float) -> str:
    """Calculate the final price after applying a percentage discount."""
    return f"Final price: {price * (1 - percent / 100):.2f}"

apply_discount.invoke({"price": 2000, "percent": 15})    # 'Final price: 1700.00', no LLM needed
```

Then `create_agent(model, tools=tools, system_prompt=...)` runs the loop for you.

:::{tip}
**The description is the prompt.** The model chooses tools by reading their names and docstrings.
"Calculate the final price after applying a percentage discount" works; "helper function" doesn't.
:::

## 3 · Tools that call real APIs

`3_external_api_tools.py` wraps the free Open-Meteo API (no key needed). The agent chains two tools
by itself: `get_coordinates("Gampole")`, then `get_current_weather(lat, lon)`.

The golden rules, all in the code:

```python
r = requests.get(GEO_URL, params={"name": city, "count": 1}, timeout=10)   # 1. always a timeout
...
except requests.RequestException as e:
    return f"Geocoding API error: {e}"                                      # 2. return errors, don't crash
...
return f"Temperature: {cur['temperature_2m']} C, …"                        # 3. small, clean output
```

## 4 · Database tools, safely

`4_database_tools.py` lets the agent answer questions from SQLite with two tools:
`list_tables()` (the schema) and `run_sql_query(query)`. Letting an LLM write SQL is risky, so
there are three safety layers:

1. **A read-only connection**: `sqlite3.connect("file:shop.db?mode=ro", uri=True)`. The database
   itself refuses writes.
2. **SELECT only**: anything else is rejected before it runs.
3. **A row limit**: at most 50 rows, so a huge table can't flood the prompt.

What the guard does with different queries:

```text
SELECT c.name, SUM(o.amount) … WHERE c.city = 'Chennai' …   →  Karthik | 70000.0
                                                                Arun    | 65800.0
DELETE FROM orders                                          →  Error: only a single SELECT statement is allowed.
SELECT 1; DROP TABLE orders                                 →  Error: only a single SELECT statement is allowed.
```

So for *"Which customer from Chennai has spent the most?"* the agent answers **Karthik, ₹70,000**.
SQL errors are returned as text, so the agent can read them and fix its own query.

## 5 · MCP: tools as a service

An MCP **server** offers tools (`mcp_server.py`):

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("utils")

@mcp.tool()
def reverse_text(text: str) -> str:
    """Reverse a string."""
    return text[::-1]

mcp.run(transport="stdio")
```

An MCP **client** discovers them and hands them to an agent (`mcp_client.py`):

```python
client = MultiServerMCPClient({
    "utils": {"transport": "stdio", "command": "python", "args": ["mcp_server.py"]},
})
tools = await client.get_tools()          # Discovered: ['add', 'reverse_text']
agent = create_agent(model, tools)
```

Run only the client: it starts the server itself (`stdio` means the two talk through the server's
standard input and output).

```bash
python mcp_client.py
```

Asked to *"Add 21 and 21, then reverse the word 'parottasalna'"*, the agent calls `add` → 42 and
`reverse_text` → `anlasattorap`.

```{raw} html
:file: ../diagrams/s16-mcp.html
```

**Why MCP?** Without it, every app writes its own wrapper for every tool. With it, one GitHub MCP
server, one Postgres MCP server, one Slack MCP server… work in any MCP-aware app.

## Common mistakes

- **Vague tool descriptions**, so the model calls the wrong tool or none.
- **Tools that raise exceptions.** The agent run crashes. Return an error message instead.
- **Returning huge outputs** (a full JSON response, 10,000 rows). It costs tokens and confuses the
  model.
- **Trusting the model with write access.** Give tools the **least** power they need: read-only
  database users, allow-lists, limits.
- **Forgetting `await`** with MCP tools: they're async (`await agent.ainvoke(...)`).

## Hands-on exercises

Try each one before opening the solution.

**Exercise 1 · Safe division.** Add `divide(a, b)` to `1_function_calling.py` and ask *"What is 10
divided by 0?"*

<details class="solution"><summary>Solution</summary>

```python
@tool
def divide(a: float, b: float) -> str:
    """Divide a by b."""
    if b == 0:
        return "Error: cannot divide by zero."
    return str(a / b)

tools = [add, multiply, divide]
```

The model receives the error as the tool result and explains it, instead of the program crashing.

</details>

**Exercise 2 · A forecast tool.** Add `get_forecast(latitude, longitude, days)` to
`3_external_api_tools.py`.

<details class="solution"><summary>Solution</summary>

```python
@tool
def get_forecast(latitude: float, longitude: float, days: int = 3) -> str:
    """Daily max/min temperature (C) for the next 1-7 days at the given coordinates."""
    try:
        r = requests.get(WEATHER_URL, params={
            "latitude": latitude, "longitude": longitude, "forecast_days": max(1, min(days, 7)),
            "daily": "temperature_2m_max,temperature_2m_min", "timezone": "auto",
        }, timeout=10)
        r.raise_for_status()
        daily = r.json()["daily"]
        return "\n".join(f"{d}: {lo}–{hi} C" for d, lo, hi in
                         zip(daily["time"], daily["temperature_2m_min"], daily["temperature_2m_max"]))
    except requests.RequestException as e:
        return f"Forecast API error: {e}"
```

Ask *"Will it be hot in Chennai this weekend?"*.

</details>

**Exercise 3 · Allow CTEs, still block writes.** The SQL guard rejects `WITH … SELECT`. Allow it
safely.

<details class="solution"><summary>Solution</summary>

```python
FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|replace|attach|pragma)\b", re.I)

q = query.strip().rstrip(";")
if ";" in q or not re.match(r"(?is)^\s*(select|with)\b", q) or FORBIDDEN.search(q):
    return "Error: only a single read-only SELECT query is allowed."
```

The read-only connection is still the real protection; the check just gives the agent a clear
message.

</details>

**Exercise 4 · A third MCP tool.** Add `word_count(text)` to `mcp_server.py`.

<details class="solution"><summary>Solution</summary>

```python
@mcp.tool()
def word_count(text: str) -> int:
    """Count the words in a text."""
    return len(text.split())
```

Run `python mcp_client.py`: `Discovered:` now lists three tools, without any change to the client.

</details>

**Exercise 5 · The shop database over MCP.** Turn `list_tables` and `run_sql_query` into an MCP server.

<details class="solution"><summary>Solution outline</summary>

```python
# shop_mcp.py
from mcp.server.fastmcp import FastMCP
from importlib import import_module

db_tools = import_module("4_database_tools")   # reuse the guarded functions
mcp = FastMCP("shop")

@mcp.tool()
def list_tables() -> str:
    """List all tables with their columns. Call this first."""
    return db_tools.list_tables.invoke({})

@mcp.tool()
def run_sql_query(query: str) -> str:
    """Run one read-only SELECT query and return up to 50 rows."""
    return db_tools.run_sql_query.invoke({"query": query})

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Point `mcp_client.py` at `shop_mcp.py` and ask *"Which city has the most customers?"*. Note: importing
`4_database_tools` also builds its agent, so it needs `GROQ_API_KEY`; moving the tools into their own
module is cleaner.

</details>

**Exercise 6 · Let the agent pick.** Give one agent all the tools from this session (maths, discount,
weather, database) and ask a question that needs three of them.

<details class="solution"><summary>What to notice</summary>

With clear names and docstrings the agent picks the right tools in a sensible order. Watch the trace
(`m.pretty_print()`): if it picks wrongly, improve the **descriptions** before changing anything
else. With many tools, group them into separate agents or MCP servers.

</details>

## Full source

<details class="source">
<summary>1_function_calling.py</summary>

```{literalinclude} ../code/16-tools-mcp/1_function_calling.py
:language: python
```

</details>

<details class="source">
<summary>2_custom_tools.py</summary>

```{literalinclude} ../code/16-tools-mcp/2_custom_tools.py
:language: python
```

</details>

<details class="source">
<summary>3_external_api_tools.py</summary>

```{literalinclude} ../code/16-tools-mcp/3_external_api_tools.py
:language: python
```

</details>

<details class="source">
<summary>4_database_tools.py</summary>

```{literalinclude} ../code/16-tools-mcp/4_database_tools.py
:language: python
```

</details>

<details class="source">
<summary>mcp_server.py and mcp_client.py</summary>

```{literalinclude} ../code/16-tools-mcp/mcp_server.py
:language: python
```

```{literalinclude} ../code/16-tools-mcp/mcp_client.py
:language: python
```

</details>

**Downloads:**
{download}`model.py <../code/16-tools-mcp/model.py>` ·
{download}`1_function_calling.py <../code/16-tools-mcp/1_function_calling.py>` ·
{download}`2_custom_tools.py <../code/16-tools-mcp/2_custom_tools.py>` ·
{download}`3_external_api_tools.py <../code/16-tools-mcp/3_external_api_tools.py>` ·
{download}`4_database_tools.py <../code/16-tools-mcp/4_database_tools.py>` ·
{download}`mcp_server.py <../code/16-tools-mcp/mcp_server.py>` ·
{download}`mcp_client.py <../code/16-tools-mcp/mcp_client.py>` ·
{download}`requirements.txt <../code/16-tools-mcp/requirements.txt>`
