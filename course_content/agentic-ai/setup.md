# Setup

Before the first session, let's get your computer ready. You'll do this **once**, and then every
session's code will run. It takes about 15 minutes.

You need three things:

| What | Why | Where |
|---|---|---|
| **Python 3.10+** | the language we write everything in | [python.org](https://www.python.org/downloads/) |
| **A Groq API key** | a free "password" that lets your code talk to an AI model | [console.groq.com](https://console.groq.com/keys) |
| **Ollama** (Session 7 only) | runs a small AI model on your own computer | [ollama.com](https://ollama.com) |

## Step 1 · Check Python

Open a terminal (Command Prompt or PowerShell on Windows) and type:

```bash
python3 --version
```

You should see something like `Python 3.12.3`. If you see an error, install Python from
[python.org](https://www.python.org/downloads/) first. On Windows, tick **"Add Python to PATH"**
during installation.

## Step 2 · Make a project folder with a virtual environment

A **virtual environment** is a private box for this course's packages, so they don't mix with
anything else on your computer. Think of it as a separate bag for each course's books.

```bash
mkdir agentic-ai
cd agentic-ai
python3 -m venv .venv
```

Now "open the bag" (activate it). Do this **every time** you open a new terminal for the course:

```bash
source .venv/bin/activate
```

On Windows, use `.venv\Scripts\activate` instead. When it works, your prompt starts with `(.venv)`.

## Step 3 · Install the packages

Packages are ready-made code other people wrote, which we reuse. This one command installs
everything the sessions use:

```bash
pip install "langchain>=1.0" langchain-core langchain-community langchain-groq langgraph langchain-text-splitters langchain-chroma langchain-ollama pypdf fastapi uvicorn httpx requests python-dotenv "pydantic[email]" langgraph-checkpoint-sqlite langchain-huggingface sentence-transformers mcp langchain-mcp-adapters
```

It downloads quite a lot, so give it a few minutes.

## Step 4 · Get your free Groq API key

Most sessions call an AI model through **Groq**, a service that runs models very fast and has a
free tier.

1. Go to [console.groq.com/keys](https://console.groq.com/keys) and sign in.
2. Click **Create API Key** and copy it. It starts with `gsk_`.
3. In the folder where you put a session's code, create a file named exactly `.env` containing:

   ```bash
   GROQ_API_KEY="gsk_paste_your_key_here"
   ```

The code reads the key from this file with `load_dotenv()`, so the key never has to be written
inside your code.

:::{warning}
**Your API key is like a password.** Anyone who has it can use your account.

- Never share it in chats or screenshots.
- Never upload `.env` to GitHub. Create a file named `.gitignore` containing the line `.env`.
- If it leaks, delete it in the Groq console and create a new one.
:::

## Step 5 · Ollama (only for Session 7)

Session 7 turns text into numbers ("embeddings") on your own computer. Install Ollama from
[ollama.com](https://ollama.com), then download the small model it needs:

```bash
ollama pull nomic-embed-text
```

## Step 6 · Run your first file

Make a file called `hello_ai.py`:

```python
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()                                   # reads GROQ_API_KEY from .env
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

answer = llm.invoke("Say hello to a new AI student in one sentence.")
print(answer.content)
```

Run it:

```bash
python hello_ai.py
```

**Output (it will vary a little):**

```text
Hello and welcome. You're about to learn how to build things that think!
```

If you see a friendly sentence, you're all set. 🎉

:::{note}
**Common problems**

- `ModuleNotFoundError`: the virtual environment isn't active. Run the `activate` command again.
- `401 Unauthorized` or "API key not set": the `.env` file is missing, misspelled, or in a
  different folder from your code.
:::
