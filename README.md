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

### Setup Validation

When setting up on a new machine, run the validation script to check your configuration:

```bash
uv run python check_setup.py
```

This will verify:
- Project structure and files
- Required environment variables
- Python dependencies
- Service files

**Note for work machines**: If you can't set API keys on your current machine, that's okay! The code will:
- Gracefully disable LangSmith tracing if no API key is found (with a warning)
- Work with whatever provider is configured (Ollama, OpenAI, or Anthropic)
- Only fail if you try to use a provider that requires an API key but no key is provided

## Ingestion

### CLI

```bash
uv run rag-api-ingest --query "quantum computing" --max-docs 5
```

Note: If you are running this outside Docker Compose, point to your local Qdrant:

```bash
export QDRANT_URL="http://localhost:6333"
uv run rag-api-ingest --query "quantum computing" --max-docs 5
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

Both expose `/query` accepting `{ "question": "..." }` and returning `{ "answer": "...", "debug": {...}, "status": "success" }`.

## Debugging and Observability

### Web UI

Both services now include interactive HTML debugging interfaces:

- **LangChain Service**: http://localhost:8009/
- **LlamaIndex Service**: http://localhost:8080/

The UI provides:
- Real-time status monitoring
- Query interface with debug information
- Formatted response display
- Links to API documentation

### Enhanced API Responses

Query endpoints now return detailed debug information:

```json
{
  "answer": "The answer to your question...",
  "debug": {
    "tools_used": ["rag_query", "web_search"],
    "steps_taken": 5,
    "messages_count": 6,
    "model_provider": "openai",
    "execution_time_ms": 1234.56,
    "total_tokens": {
      "input_tokens": 150,
      "output_tokens": 200
    }
  },
  "status": "success"
}
```

### LangSmith Integration

The project includes built-in LangSmith tracing for comprehensive debugging:

1. **Get your LangSmith API key** from https://smith.langchain.com/
2. **Configure in `.env`**:
   ```env
   LANGSMITH_API_KEY="your-api-key-here"
   LANGSMITH_TRACING=true
   LANGSMITH_PROJECT="rag-api-langchain"
   ```

Once configured, all agent executions are automatically traced to LangSmith, allowing you to:
- View detailed execution traces
- Debug tool usage and reasoning
- Monitor token usage and costs
- Analyze performance bottlenecks
- Use LangChain Studio for interactive debugging

### Status Endpoints

Check service health and configuration:

```bash
curl http://localhost:8009/status
curl http://localhost:8080/status
```

Returns service status, configuration, and connection health.

### Streaming Endpoint (LangChain)

For real-time debugging, use the streaming endpoint:

```bash
curl -X POST http://localhost:8009/query/stream \
  -H 'Content-Type: application/json' \
  -d '{"question": "What is quantum computing?"}'
```

Returns Server-Sent Events (SSE) with real-time execution chunks.

### Enhanced Logging

All services now include structured logging with:
- Timestamps and log levels
- File names and line numbers
- Detailed execution traces
- Error stack traces

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

curl -X POST http://localhost:8009/query -H 'Content-Type: application/json' -d '{"question":"Summarize quantum entanglement", "debug": true}'

curl -X POST http://localhost:8080/query -H 'Content-Type: application/json' -d '{"question":"Summarize quantum entanglement", "debug": true}'
```

### Using the Debug UI

Instead of curl, you can use the interactive web interfaces:
- Visit http://localhost:8009/ for LangChain service
- Visit http://localhost:8080/ for LlamaIndex service

The UI shows real-time status, formatted responses, and detailed debug information.