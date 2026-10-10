# Setup

Do this **once** before the first session. It takes about 20 minutes, most of it waiting for
downloads.

| What | Why | Where |
|---|---|---|
| **Python 3.10+** | everything in the course is Python | [python.org](https://www.python.org/downloads/) |
| **A Groq API key** | lets your code talk to a fast AI model, free tier available | [console.groq.com](https://console.groq.com/keys) |
| **Docker** | runs Redis, OpenSearch and n8n for some sessions | [docker.com](https://docs.docker.com/get-docker/) |
| **Ollama** (sessions 3, 7, 8) | makes embeddings on your own computer | [ollama.com](https://ollama.com) |

## 1 · A project folder with a virtual environment

```bash
mkdir agentic-ai && cd agentic-ai
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

Your prompt now starts with `(.venv)`. Activate it again every time you open a new terminal.

## 2 · Install the packages

```bash
pip install "langchain>=1.0" langchain-classic langchain-core langchain-community \
  langchain-text-splitters langchain-groq langchain-chroma langchain-huggingface langchain-ollama \
  langgraph langchain-mcp-adapters mcp groq chromadb faiss-cpu sentence-transformers \
  rank-bm25 opensearch-py tiktoken nltk pypdf pandas scikit-learn matplotlib \
  redis fastapi uvicorn sse-starlette httpx requests python-dotenv "pydantic[email]"
```

`sentence-transformers` pulls in PyTorch, so this download is large (1–2 GB). The first time a
script uses an embedding model such as `all-MiniLM-L6-v2`, it downloads that model too (about 90 MB).

## 3 · Your Groq API key

1. Sign in at [console.groq.com](https://console.groq.com/keys) and create a key.
2. Put it in a file called `.env` in your project folder:

   ```text
   GROQ_API_KEY=gsk_your_key_here
   ```

3. Load it in the terminal before running scripts. On macOS or Linux:

   ```bash
   export $(cat .env | xargs)
   ```

   On Windows PowerShell, use `$env:GROQ_API_KEY="gsk_your_key_here"`. Scripts that call
   `load_dotenv()` read `.env` by themselves.

:::{warning}
**Your API key is a password.** Never paste it into code you share, push to GitHub, or post in a
chat. Every script in this course reads it from the `GROQ_API_KEY` environment variable instead.
If a key ever leaks, delete it in the Groq console and create a new one. Anyone who has it can use
your account.
:::

## 4 · Ollama embeddings (sessions 3, 7, 8)

Install Ollama, then download the embedding model once:

```bash
ollama pull nomic-embed-text
```

## 5 · Services in Docker

Start these only when a session needs them:

```bash
# Redis (sessions 9 and 12)
docker run -d --name redis -p 6379:6379 redis:7

# OpenSearch (session 4, hybrid search). Pick your own strong password.
docker run -d --name opensearch -p 9200:9200 \
  -e "discovery.type=single-node" -e "plugins.security.disabled=true" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=<choose-a-strong-password>" \
  opensearchproject/opensearch:latest
```

n8n has its own steps in [Session 7](sessions/07-rag-with-n8n.md).

## 6 · A PDF to search

Many RAG sessions read a file called `python.pdf`. Use **any PDF you're allowed to use**: your
own notes, a free e-book, a product manual. Save it next to the script as `python.pdf`, or change
the file name in the code.

## Check everything works

```bash
python -c "import langchain, chromadb, sentence_transformers; print('ready')"
```

If you see `ready`, you're set.
