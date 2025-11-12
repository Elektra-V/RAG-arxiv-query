# RAG API - arXiv Query System

Retrieval Augmented Generation system for academic paper queries using LangChain ReAct agent with RAG and arXiv search tools.

## Quick Start

### 1. Configure Environment

```bash
cp env.example .env
```

Edit `.env` with your API keys and settings.

### 2. Install Dependencies

```bash
uv sync
```

### 3. Activate Virtual Environment

```bash
source .venv/bin/activate  # or use uv run for commands
```

### 4. Start Docker Services

```bash
docker compose up --build
```

This starts Qdrant (vector database) on port 6334.

### 5. Run Ingestion

Ingest arXiv papers into the vector database:

```bash
uv run rag-api-ingest --query "machine learning" --max-docs 5
```

### 6. Start LangGraph Studio

```bash
uv run langgraph dev
```

Access Studio at `http://localhost:8123` or use the URL shown in the output.

**Note:** If Studio doesn't connect or crashes, set the base URL in LangSmith Studio website to match your local machine (e.g., `http://127.0.0.1:2024`).

---

## Architecture

```
┌─────────────┐
│  Studio UI │
└──────┬──────┘
       │
┌──────▼──────────┐
│ LangGraph Server│
└──────┬──────────┘
       │
┌──────▼──────────────┐
│  ReAct Agent        │
│  - rag_query        │──► Qdrant (Vector DB)
│  - arxiv_search     │──► arXiv API
└──────┬──────────────┘
       │
┌──────▼──────┐
│   LLM       │
└─────────────┘
```

---

## Configuration

### Required Settings

- `OPENAI_API_KEY`: Your OpenAI API key (or OpenRouter/other gateway)
- `OPENAI_MODEL`: Model name (e.g., `gpt-4o-mini`, `openai/gpt-oss-20b:free`)
- `OPENAI_BASE_URL`: Optional gateway URL (e.g., `https://openrouter.ai/api/v1`)

### Optional Settings

- `ARXIV_SEARCH_MAX_RESULTS`: Max results for arXiv search (default: 5)
- `LANGSMITH_API_KEY`: LangSmith API key for tracing
- `LANGSMITH_ENDPOINT`: LangSmith endpoint (US: `https://api.smith.langchain.com`, EU: `https://eu.api.smith.langchain.com`)
- `LANGSMITH_PROJECT`: Project name for LangSmith traces
- `LANGSMITH_TRACING`: Enable/disable tracing (default: `false`)

See `env.example` for all available settings.

---

## Usage

### Query via Studio UI

1. Start LangGraph Studio: `uv run langgraph dev`
2. Open the Studio URL in your browser
3. Enter your question in the chat interface
4. The agent will use `rag_query` first, then `arxiv_search` if needed

### Query via API

```bash
curl -X POST http://localhost:9010/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is quantum computing?", "debug": true}'
```

### API Documentation

Visit `http://localhost:9010/docs` for interactive API documentation.

---

## Troubleshooting

### Port Already in Use

```bash
docker compose down
lsof -ti :6334 | xargs kill -9  # Qdrant
lsof -ti :2024 | xargs kill -9  # LangGraph
```

### Empty Database

Run ingestion first: `uv run rag-api-ingest --query "topic" --max-docs 5`

### Studio Connection Issues

1. Ensure LangGraph server is running: `uv run langgraph dev`
2. Set base URL in LangSmith Studio website to match local URL
3. Use Chrome browser (Safari may have issues with localhost)

### Authentication Errors

- Verify `OPENAI_API_KEY` is set correctly in `.env`
- Check API key has credits/usage remaining
- For OpenRouter, ensure model name is correct (e.g., `openai/gpt-oss-20b:free`)

---

## Project Structure

```
rag-api/
├── .env                 # Your configuration (copy from env.example)
├── env.example          # Configuration template
├── rag_api/
│   ├── settings.py      # Configuration loader
│   ├── clients/         # API clients (OpenAI, Qdrant, embeddings)
│   ├── ingestion/       # Document ingestion pipeline
│   └── services/        # API services (LangChain, LlamaIndex)
├── docker-compose.yml    # Docker services (Qdrant)
└── start_studio.sh      # Helper script to start Studio
```

---

## How It Works

1. **Ingestion**: Downloads arXiv papers, creates embeddings, stores in Qdrant
2. **Query**: User asks a question
3. **RAG Query**: Agent searches ingested papers in Qdrant vector database
4. **arXiv Search**: If RAG returns empty, agent searches arXiv API directly
5. **Response**: Agent synthesizes answer from retrieved information

The agent is configured to always use tools (`rag_query` or `arxiv_search`) and never respond directly without tool usage.
