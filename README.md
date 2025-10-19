# RAG API

Dual-service Retrieval-Augmented Generation platform providing LangChain agent and LlamaIndex endpoints backed by Qdrant and Ollama.

## Features

- Manual ingestion CLI to load arXiv content into Qdrant using HuggingFace embeddings.
- LangChain FastAPI service on port 8009 with LangGraph ReAct agent and DuckDuckGo search tool.
- LlamaIndex FastAPI service on port 8080 offering direct retrieval over the shared Qdrant collection.

## Setup

Create a `.env` file with service URLs and optional overrides. Default values are shown below.

```env
ARXIV_QUERY="quantum computing"
ARXIV_MAX_DOCS=5
QDRANT_URL="http://qdrant:6333"
QDRANT_COLLECTION="arxiv_papers"
HUGGINGFACE_MODEL="sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL="llama3.1:8b-instruct-q4_0"
OLLAMA_BASE_URL="http://ollama:11434"
DUCKDUCKGO_RESULTS=3
LANGCHAIN_HOST="0.0.0.0"
LANGCHAIN_PORT=8009
LLAMAINDEX_HOST="0.0.0.0"
LLAMAINDEX_PORT=8080
INGESTION_HOST="0.0.0.0"
INGESTION_PORT=8090

OLLAMA_SOCKET=/var/run/ollama.sock
OLLAMA_MODEL_VOLUME=ollama-models
```

Install dependencies via `uv`:

```bash
uv sync
```

## Ingestion

### CLI

```bash
uv run rag-api-ingest run --query "quantum computing" --max-docs 5
```

### HTTP Service

```bash
uv run rag_api/services/ingestion/app.py
curl -X POST http://localhost:8090/ingest -H "Content-Type: application/json" -d '{"query": "quantum computing", "max_docs": 5}'
```

## Services

### LangChain FastAPI (port 8009)

```
uv run rag_api/services/langchain/app.py
```

### LlamaIndex FastAPI (port 8080)

```
uv run rag_api/services/llamaindex/app.py
```

Both expose `/query` accepting `{ "question": "..." }` and returning `{ "answer": "..." }`.

## Containerized

For a containerized usage, follow the following advice:

```bash
# Build all services and pull model to Ollama
docker compose up --build --detach
docker compose exec ollama ollama pull llama3.1:8b-instruct-q4_0
```

then you can use the service like so:

```bash
curl -X POST http://localhost:8010/ingest -H 'Content-Type: application/json' -d '{"query":"quantum computing","max_docs":2}'

curl -X POST http://localhost:8009/query -H 'Content-Type: application/json' -d '{"question":"Summarize quantum entanglement"}'

curl -X POST http://localhost:8080/query -H 'Content-Type: application/json' -d '{"question":"Summarize quantum entanglement"}'
```