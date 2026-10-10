# Session 7 · RAG without code: n8n

## The big idea

**n8n** is a visual workflow tool: you connect boxes ("nodes") instead of writing Python. It has
ready-made nodes for document loading, text splitting, embeddings, vector stores, LLMs and AI
agents, so you can build the same RAG pipeline as Session 6 by dragging and dropping, and hook it
up to Telegram, Slack, email or a web form.

**Everyday example:** Session 6 was cooking from scratch. n8n is a meal kit: the pieces are
prepared, you just put them together in the right order.

## Run n8n with Docker

```bash
docker volume create n8n_data

docker run -it --rm \
 --name n8n \
 -p 5678:5678 \
 -e GENERIC_TIMEZONE="Asia/Kolkata" \
 -e TZ="Asia/Kolkata" \
 -e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true \
 -e N8N_RUNNERS_ENABLED=true \
 -v n8n_data:/home/node/.n8n \
 docker.n8n.io/n8nio/n8n
```

Open <http://localhost:5678> and create the owner account. The `n8n_data` volume keeps your
workflows and credentials when the container restarts. The download below also shows how to run
n8n with PostgreSQL instead of the built-in SQLite, for a team setup.

## The workflow from class

Two flows in one workflow, with **Pinecone** as the vector database, **Ollama** for embeddings and
**Groq** as the LLM:

```text
INGEST
  1. Upload File (form)  →  2. Pinecone Vector Store (insert, index "js-book")
                               ├─ 2A. Default Data Loader (reads the uploaded file)
                               │     └─ 2B. Recursive Character Text Splitter (overlap 300)
                               └─ 2C. Embeddings Ollama (nomic-embed-text)

ASK
  Edit Fields {"query": "..."}  →  2. AI Agent  →  4. Telegram: send the answer
                                      ├─ 3. LLM Model (Groq, openai/gpt-oss-120b)
                                      └─ 2B. Pinecone Vector Store (retrieve-as-tool, topK 5)
                                            └─ 2A. Embeddings Ollama
```

The **AI Agent** node's prompt:

```text
Use the pinecone vector store tool to get the necessary context and answer should be from the
context only.

User Query: {{ $json.query }}
```

Notice that retrieval is a **tool** here (`retrieve-as-tool`): the agent decides when to search the
knowledge base. That's agentic RAG, which we build in code in [Session 16](16-tools-and-mcp.md).

## Importing it

1. In n8n: **Workflows → Import from file**, and pick `rag-pinecone-workflow.json` from the
   downloads.
2. Every node with a red warning needs **your own credentials**: a Pinecone API key, a Groq API key,
   Ollama's URL (from Docker on Mac or Windows that's `http://host.docker.internal:11434`) and a
   Telegram bot token if you want the Telegram output.
3. Create a Pinecone index called `js-book` with **dimension 768** (the size of `nomic-embed-text`
   vectors), or pick your own index in both Pinecone nodes.

:::{note}
The exported file no longer contains the class's credential references or webhook ids; you add your
own when you import it. The Telegram node reads the chat id from a "Telegram Trigger" node that
wasn't part of the export. Add a Telegram Trigger as the start of the ask flow, or replace the last
node with any output you like.
:::

## Code or no-code?

| n8n | Python (Sessions 6, 8–12) |
|---|---|
| fast to build and change; non-developers can follow it | full control over chunking, retrieval and prompts |
| 400+ integrations (Telegram, Gmail, Sheets…) | easy to test, version and deploy like any app |
| advanced tricks (reranking, caching) are harder | every technique in this course is a few lines |

Many teams prototype in n8n, then move the core to code.

## Common mistakes

- **Index dimension doesn't match the embedding model.** Pinecone rejects 768-number vectors in a
  384-dimension index.
- **`localhost` inside Docker.** From inside the n8n container, `localhost` is the container itself,
  not your computer. Use `host.docker.internal`, or run Ollama in the same Docker network.
- **Different embedding models for insert and search.** Both Ollama nodes must use the same model.
- **Running without the volume.** With `--rm` and no `-v n8n_data:…`, everything is lost when the
  container stops.

## Try it yourself

1. Import the workflow, connect your credentials and upload a small PDF. Check in Pinecone that
   vectors arrived.
2. Replace the "Edit Fields" node with a **Chat Trigger** so you can ask questions in n8n's chat
   window.
3. Change topK from 5 to 2. Do the answers get better or worse?
4. Swap Pinecone for the **Simple Vector Store** (in-memory) node. What do you lose when n8n
   restarts?

## Downloads

{download}`run-n8n.txt <../code/07-n8n/run-n8n.txt>` ·
{download}`rag-pinecone-workflow.json <../code/07-n8n/rag-pinecone-workflow.json>`
