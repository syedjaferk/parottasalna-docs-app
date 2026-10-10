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

## Try it yourself

1. In `1_function_calling.py`, add a `divide(a, b)` tool that returns an error message for
   `b == 0`. Ask *"What is 10 divided by 0?"*
2. Add a `get_forecast(latitude, longitude, days)` tool to `3_external_api_tools.py` (Open-Meteo's
   `daily=temperature_2m_max` parameter).
3. The SQL guard rejects `WITH … SELECT` queries (CTEs), which are read-only too. Change the check
   to allow them, but still block `INSERT`, `UPDATE`, `DELETE` and `DROP`.
4. Add a third tool to `mcp_server.py`, `word_count(text)`, and check the client discovers it.
5. Turn `4_database_tools.py`'s two tools into an MCP server, so any MCP app can query the shop
   database.

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
