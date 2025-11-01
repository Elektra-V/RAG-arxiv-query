# RAG API

Dual-service Retrieval-Augmented Generation platform providing LangChain agent and LlamaIndex endpoints backed by Qdrant and Ollama.

## Quick Start

**For most users, follow these steps:**

1. **Copy environment template**: `cp env.example .env`
2. **Edit `.env`** with your configuration (see [Configuration](#configuration) below)
3. **Install dependencies**: `uv sync`
4. **Validate setup**: `uv run python check_setup.py`
5. **Start a service**: `uv run rag_api/services/langchain/app.py`
6. **Open in browser**: http://localhost:8009/

**📖 For detailed guides, see:**
- **New machine setup**: See [Setup on New Machine](#setup-on-new-machine) section
- **Company API with Basic auth**: See [Company API Configuration](#company-api-configuration) section

## Features

- Manual ingestion CLI to load arXiv content into Qdrant using HuggingFace embeddings.
- LangChain FastAPI service on port 8009 with LangGraph ReAct agent and DuckDuckGo search tool.
- LlamaIndex FastAPI service on port 8080 offering direct retrieval over the shared Qdrant collection.
- Support for local models (Ollama), cloud APIs (OpenAI, Anthropic), and company APIs with Basic auth.
- Built-in debugging UI, LangSmith tracing, and enhanced observability.

## Configuration

**Step 1**: Copy the template: `cp env.example .env`

**Step 2**: Edit `.env` based on your setup:

### Option A: Local Models (Ollama + HuggingFace)

```env
# Model providers
LLM_PROVIDER="ollama"
EMBEDDING_PROVIDER="huggingface"

# Required
QDRANT_URL="http://localhost:6333"
QDRANT_COLLECTION="arxiv_papers"

# Ollama config
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="llama3.1:8b-instruct-q4_0"

# HuggingFace config
HUGGINGFACE_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# Optional - disable LangSmith if no key
LANGSMITH_TRACING=false
```

### Option B: Cloud APIs (OpenAI or Anthropic)

```env
# Model providers
LLM_PROVIDER="openai"  # or "anthropic"
EMBEDDING_PROVIDER="openai"

# OpenAI config
OPENAI_API_KEY="sk-your-key-here"
OPENAI_MODEL="gpt-4o-mini"

# OR Anthropic config
ANTHROPIC_API_KEY="sk-ant-your-key-here"
ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
```

### Option C: Company API (Basic Auth)

```env
# Model providers
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="openai"

# Company API - secrets go in .env file
OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
OPENAI_AUTH_USERNAME="your-username"
OPENAI_AUTH_PASSWORD="your-password"
OPENAI_API_KEY="xxxx"  # Placeholder is fine with Basic auth
OPENAI_MODEL="Llama-3-SauerkrautLM"
```

**Step 3**: Install dependencies

```bash
uv sync
```

**Step 4**: Validate setup

```bash
uv run python check_setup.py
```

This checks project structure, dependencies, and configuration.

> **Note**: See `env.example` for all available configuration options.

## Setup on New Machine

When setting up on a **work machine** or new environment:

1. **Copy project** to the new machine
2. **Run validation**: `uv run python check_setup.py`
3. **Copy `.env` template**: `cp env.example .env`
4. **Edit `.env`** with your credentials
5. **Install**: `uv sync`

**The code handles missing API keys gracefully:**
- LangSmith tracing disables automatically (with warning)
- Works with whatever provider you configure
- Only fails if you try to use a provider without required credentials

## Company API Configuration

For **company APIs with Basic authentication** (like Fraunhofer GenAI):

**Configuration** (in `.env`):
```env
OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
OPENAI_AUTH_USERNAME="your-username"
OPENAI_AUTH_PASSWORD="your-password"
OPENAI_API_KEY="xxxx"
OPENAI_MODEL="Llama-3-SauerkrautLM"
```

**How it works**:
1. Secrets read from `.env` file
2. `rag_api/clients/openai.py` encodes `username:password` as Base64
3. Creates OpenAI client with `Authorization: Basic <token>` header
4. All services (LangChain, LlamaIndex, embeddings) use the same client

**To debug**: Check `rag_api/clients/openai.py` - all auth logic is in one place.

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

---

## Additional Resources

- **Full environment template**: See `env.example` for all configuration options
- **Setup validation**: Run `uv run python check_setup.py` to verify your configuration
- **Company API details**: Authentication logic in `rag_api/clients/openai.py`
- **API documentation**: Visit `/docs` on any service (e.g., http://localhost:8009/docs)

## Troubleshooting

**Service won't start?**
1. Check `.env` file exists: `cp env.example .env`
2. Run validation: `uv run python check_setup.py`
3. Check logs for specific error messages

**Authentication errors?**
1. Verify credentials in `.env`
2. For company API: Check `rag_api/clients/openai.py` encoding logic
3. Test client directly: See `COMPANY_API_GUIDE.md` for examples

**Missing dependencies?**
```bash
uv sync  # Installs all dependencies
```

**Need help?**
- Check service status: `curl http://localhost:8009/status`
- Use debug UI: http://localhost:8009/
- Check logs for detailed error messages