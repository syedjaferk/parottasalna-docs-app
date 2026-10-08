# Session 6 · Tool Calling

## The big idea

An AI model can only **write text**. It can't check the weather, open a database or calculate
precisely. **Tool calling** gives it "hands": you describe some Python functions to the model, and
when it needs one, it **asks** you to run it.

**Everyday example:** a manager and an assistant. The manager (the AI model) says *"Please call the
weather office for Paris."* The assistant (**your code**) makes the call and reports back *"Sunny,
25°C."* The manager then writes the final reply. The manager never touches the phone.

:::{important}
**The AI never runs your code.** It only sends back a request like
`get_weather(city="Paris")`. **Your program** decides whether to run it. That's also where you put
safety checks.
:::

```{raw} html
:file: ../diagrams/s06-sequence.html
```

## Step 1 · Turn a function into a tool

Add `@tool` on top of a normal Python function:

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    return f"The weather in {city} is sunny and 25°C."    # a pretend answer for now

@tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```

`@tool` reads three things from your function and shows them to the model:

| From your code | The model sees it as | Why it matters |
|---|---|---|
| function name `get_weather` | the tool's name | how it asks for the tool |
| the docstring `"""..."""` | the tool's description | **when** to use it |
| type hints `city: str` | the inputs it needs | **what** to send |

:::{tip}
The docstring is not decoration. It's how the model decides whether to use the tool. A vague
docstring means the model picks the wrong tool, or none at all.
:::

## Step 2 · Give the tools to the model

```python
from langchain_groq import ChatGroq

tools = [get_weather, add_numbers]
tool_map = {t.name: t for t in tools}     # {"get_weather": get_weather, ...} to find them by name

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
llm_with_tools = llm.bind_tools(tools)    # attach the tool descriptions to every request
```

## Step 3 · The two-call dance

```python
from langchain_core.messages import HumanMessage

def run_query(question: str) -> str:
    messages = [HumanMessage(question)]

    # Call 1: the model decides — answer directly, or ask for tools?
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)

    if ai_msg.tool_calls:                                  # it asked for tools
        for call in ai_msg.tool_calls:
            result = tool_map[call["name"]].invoke(call["args"])   # YOUR code runs it
            messages.append({"role": "tool", "content": str(result),
                             "tool_call_id": call["id"]})          # report back
        # Call 2: the model writes the final answer using the results
        return llm_with_tools.invoke(messages).content

    return ai_msg.content                                  # no tool needed
```

**Let's trace** `run_query("What's the weather in Paris and London?")`:

**Call 1:** the model replies with *no text*, just two tool requests:

```python
ai_msg.tool_calls
# [{'name': 'get_weather', 'args': {'city': 'Paris'},  'id': 'call_1'},
#  {'name': 'get_weather', 'args': {'city': 'London'}, 'id': 'call_2'}]
```

**Your loop** runs `get_weather` twice and adds two `tool` messages, one per request.

**Call 2:** the model reads everything and answers:

```text
Paris is sunny and 25°C, and London is sunny and 25°C too.
```

:::{note}
**What is `tool_call_id`?** When the model asks for several tools at once, each request has an ID.
Your result must carry the same ID so the model knows which answer belongs to which question. It's
like a token number at a bank counter.
:::

## When the model doesn't use a tool

Try `run_query("convert 100rs to usd")`. There's no currency tool, so the model answers from memory
(maybe with an old exchange rate) or says it can't. Tools make the model **able** to act; they don't
force it to.

**Fix it with a clear system rule:** *"Use the tools for any calculation or live data. If no tool
fits, say so instead of guessing."*

## Why this is better than the ReAct loop

| Hand-made ReAct (Session 5) | Native tool calling (this session) |
|---|---|
| the model writes "Action: ..." as plain text | the service returns clean `tool_calls` |
| you cut strings to find the inputs | inputs arrive as a ready dictionary |
| breaks if the format changes slightly | the format is guaranteed |
| the model can invent fake results | results only come from your code |

The pattern, **ask → run tools → ask again**, is exactly what agents automate. In
[Session 11](11-tools-and-mcp.md) you'll let `create_agent()` run it for you.

## Try it yourself

1. Add a `multiply(a, b)` tool and ask *"What is 12 × 7, plus 5?"*. The model needs the
   multiplication result before it can add, so it needs **two rounds** of tools. This code only
   allows one round. Can you change it to keep going until there are no more `tool_calls`?
   (Session 11 shows the answer.)
2. Write `convert_currency(amount: float, from_code: str, to_code: str)` using a fixed dictionary
   of rates, and try `"convert 100rs to usd"` again.
3. Print `llm_with_tools.invoke("What's the weather in Chennai?").tool_calls` and find the name,
   args and id.

## Full source

<details class="source">
<summary>tool_calling.py</summary>

```{literalinclude} ../code/06-tool-calling/tool_calling.py
:language: python
```

</details>

{download}`Download tool_calling.py <../code/06-tool-calling/tool_calling.py>` ·
{download}`.env example <../code/06-tool-calling/env.example>`

The file in class pauses with `input("Wait Final....")` before the second call so you can read the
message list. Remove it to run straight through.
