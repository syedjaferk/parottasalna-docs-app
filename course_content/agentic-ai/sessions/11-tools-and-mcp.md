# Session 11 · Custom Tools, API & Database Tools, and MCP

## The big idea

Tools turn a chatbot into an **agent that does things**. In [Session 6](06-tool-calling.md) you saw
the basic idea. Now we go further:

1. the **agent loop**, where the model can use tools several times in a row
2. three ways to **build tools**
3. tools that call a **real website** (an API)
4. tools that query a **database safely**
5. **MCP**, a standard way to share tools between apps

**Everyday example:** a new employee with a toolbox. Session 6 gave them one tool for one job.
Today they learn to use several tools in a row, to handle a broken tool without panicking, and to
work with the company's shared tool cupboard (MCP).

## 1. The agent loop

*"What is 12 × 7, then add 5?"* needs **two** tool calls in a row: the model can't ask for `add`
until it knows that 12 × 7 = 84. So we keep looping until the model stops asking for tools.

```{raw} html
:file: ../diagrams/s11-agent-loop.html
```

```python
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from model import model

@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b

tools_by_name = {"add": add, "multiply": multiply}
llm_with_tools = model.bind_tools([add, multiply])

messages = [HumanMessage("What is 12 multiplied by 7, then add 5 to the result?")]

while True:
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)
    if not ai_msg.tool_calls:                 # no more tools needed → we're done
        break
    for call in ai_msg.tool_calls:
        tool_msg = tools_by_name[call["name"]].invoke(call)   # run it; returns a ToolMessage
        messages.append(tool_msg)                             # report the result back

print(ai_msg.content)
```

**What happens:**

```text
-> model wants multiply({'a': 12, 'b': 7})
<- result: 84
-> model wants add({'a': 84, 'b': 5})
<- result: 89
FINAL ANSWER: 12 × 7 = 84, and 84 + 5 = 89.
```

:::{note}
**This loop IS an agent.** That's all an agent is: a model in a loop with tools. From now on we
let `create_agent()` run this loop for us. It adds extras like memory ([Session 10](10-memory.md)).
:::

## 2. Three ways to build a tool

```python
# WAY 1 — @tool: the quickest. Docstring = description, type hints = inputs.
@tool
def word_count(text: str) -> int:
    """Count the number of words in the given text."""
    return len(text.split())


# WAY 2 — with a Pydantic schema: add rules and a description for every input.
class DiscountInput(BaseModel):
    price: float = Field(gt=0, description="Original price of the item")
    percent: float = Field(ge=0, le=100, description="Discount percentage, 0-100")

@tool("apply_discount", args_schema=DiscountInput)
def apply_discount(price: float, percent: float) -> str:
    """Calculate the final price after applying a percentage discount."""
    return f"Final price: {price * (1 - percent / 100):.2f}"


# WAY 3 — wrap a function you already have (or can't change).
def _celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32

c_to_f = StructuredTool.from_function(
    func=_celsius_to_fahrenheit,
    name="celsius_to_fahrenheit",
    description="Convert a temperature from Celsius to Fahrenheit.",
)
```

| Way | Use it when |
|---|---|
| `@tool` | writing a new, simple function |
| `args_schema` | inputs need rules (ranges, formats) |
| `StructuredTool.from_function` | wrapping an existing function |

**Test a tool without any AI.** It's just a function:

```python
apply_discount.invoke({"price": 2000, "percent": 15})    # 'Final price: 1700.00'
```

**Then give all the tools to an agent:**

```python
agent = create_agent(model, tools=[word_count, apply_discount, c_to_f],
                     system_prompt="You are a helpful assistant. Use tools for calculations.")

result = agent.invoke({"messages": [{"role": "user", "content":
    "A jacket costs 2000 with 15% off. Final price? Also convert 36.6 C to F."}]})
```

**Answer:** *"The jacket costs 1700.00 after the discount, and 36.6 °C is 97.88 °F."* The agent
called two different tools on its own.

## 3. Tools that call a real website (API)

Most useful agents talk to real services. This example uses **Open-Meteo**, a free weather website
that needs no key. It takes two tools: city → coordinates, then coordinates → weather.

```python
@tool
def get_coordinates(city: str) -> str:
    """Find the latitude and longitude of a city by name."""
    try:
        r = requests.get(GEO_URL, params={"name": city, "count": 1}, timeout=10)
        r.raise_for_status()                      # turn HTTP errors into exceptions
        results = r.json().get("results")
        if not results:
            return f"City '{city}' not found."
        top = results[0]
        return f"{top['name']}: latitude={top['latitude']}, longitude={top['longitude']}"
    except requests.RequestException as e:
        return f"Geocoding API error: {e}"        # tell the AI, don't crash
```

**What happens for** *"How is the weather in Gampola right now?"*:

```text
-> get_coordinates("Gampola")            <- Gampola: latitude=7.16, longitude=80.57
-> get_current_weather(7.16, 80.57)      <- Temperature: 24.1 C, Humidity: 88%, Wind: 6.5 km/h
Final: "It's about 24 °C in Gampola right now: humid, with a light breeze."
```

:::{important}
**3 golden rules for API tools**

1. **Always set a `timeout`.** Otherwise a stuck website freezes your agent forever.
2. **Return errors as text, don't crash.** "City not found" lets the AI try another spelling. A
   crash just ends everything.
3. **Return small, clean data.** Don't paste the whole website response; it wastes tokens and
   confuses the AI.
:::

## 4. Database tools, safely

Letting an AI write database queries is powerful, and risky. What if it writes `DROP TABLE orders`?
The demo protects a small shop database with **three layers**:

```{raw} html
:file: ../diagrams/s11-db-layers.html
```

```python
def _connect_readonly():
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)   # ② the database refuses writes

@tool
def run_sql_query(query: str) -> str:
    """Run a read-only SQL SELECT query and return the rows."""
    q = query.strip().rstrip(";")
    if not re.match(r"(?is)^\s*select\b", q) or ";" in q:          # ① SELECT only, one statement
        return "Error: only a single SELECT statement is allowed."
    conn = _connect_readonly()
    try:
        cur = conn.execute(q)
        rows = cur.fetchmany(50)                                    # ③ at most 50 rows
        ...
    except sqlite3.Error as e:
        return f"SQL error: {e}"      # the AI reads the error and fixes its own query
    finally:
        conn.close()
```

A second tool, `list_tables`, shows the AI the tables and columns first, so it doesn't have to
guess names.

**What happens for** *"Which customer from Chennai has spent the most?"*:

```text
-> list_tables()
<- customers(id, name, city)  orders(id, customer_id, product, amount, order_date)
-> run_sql_query("SELECT c.name, SUM(o.amount) AS total FROM customers c
                  JOIN orders o ON o.customer_id = c.id
                  WHERE c.city = 'Chennai' GROUP BY c.name ORDER BY total DESC LIMIT 1")
<- name | total
   Karthik | 70000.0
Final: "Karthik, from Chennai, has spent the most: ₹70,000 in total (a monitor and a laptop)."
```

:::{note}
The **read-only connection** is the layer that truly protects your data. Text checks like
"starts with SELECT" can be tricked. In a real company database, also give the agent a database
user that is **only allowed to read** the tables it needs. This is called **least privilege**.
:::

## 5. MCP: Model Context Protocol

So far, every tool lived inside our own program. **MCP** is a common standard (like USB for AI
tools): you put tools in a separate **MCP server**, and **any** MCP-aware app can find and use
them: your LangChain agent, Claude Desktop, a code editor…

**Everyday example:** a USB pen drive works in any laptop, whatever the brand. An MCP server works
with any MCP app.

```{raw} html
:file: ../diagrams/s11-mcp.html
```

**The server: tools anyone can use**

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("utils")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.tool()
def reverse_text(text: str) -> str:
    """Reverse a string."""
    return text[::-1]

if __name__ == "__main__":
    mcp.run(transport="stdio")       # talk through standard input/output
```

**The client: our agent discovers the tools at runtime**

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "utils": {"transport": "stdio", "command": "python", "args": ["mcp_server.py"]},
})
tools = await client.get_tools()        # → ['add', 'reverse_text'], discovered automatically
agent = create_agent(model, tools)
result = await agent.ainvoke({"messages": [{"role": "user",
          "content": "Add 21 and 21, then reverse the word 'parottasalna'."}]})
```

**Answer:** *"21 + 21 = 42, and 'parottasalna' reversed is 'anlasattorap'."*

- With **stdio**, the client starts the server program itself, so you just run `python mcp_client.py`.
- `MultiServerMCPClient` can connect to **many** servers at once.
- Notice `await`: MCP uses async code ([Session 8](08-async.md)).

## Try it yourself

1. Add a `get_forecast(latitude, longitude, days)` tool to the weather agent and ask about the weekend.
2. Ask the database agent to *"delete all orders from Madurai"*. Which layer stops it?
3. Add a `top_customers(limit: int)` tool with a Pydantic schema that allows at most 10.
4. Add a `word_count` tool to the MCP server. Does the client find it without any changes?

## Full source

<details class="source"><summary>model.py</summary>

```{literalinclude} ../code/11-tools-mcp/model.py
:language: python
```

</details>

<details class="source"><summary>1_function_calling.py</summary>

```{literalinclude} ../code/11-tools-mcp/1_function_calling.py
:language: python
```

</details>

<details class="source"><summary>2_custom_tools.py</summary>

```{literalinclude} ../code/11-tools-mcp/2_custom_tools.py
:language: python
```

</details>

<details class="source"><summary>3_external_api_tools.py</summary>

```{literalinclude} ../code/11-tools-mcp/3_external_api_tools.py
:language: python
```

</details>

<details class="source"><summary>4_database_tools.py</summary>

```{literalinclude} ../code/11-tools-mcp/4_database_tools.py
:language: python
```

</details>

<details class="source"><summary>mcp_server.py</summary>

```{literalinclude} ../code/11-tools-mcp/mcp_server.py
:language: python
```

</details>

<details class="source"><summary>mcp_client.py</summary>

```{literalinclude} ../code/11-tools-mcp/mcp_client.py
:language: python
```

</details>

<details class="source"><summary>requirements.txt</summary>

```{literalinclude} ../code/11-tools-mcp/requirements.txt
:language: text
```

</details>

{download}`Whiteboard: MCP explained (open at excalidraw.com) <../code/11-tools-mcp/mcp-explained.excalidraw>`
