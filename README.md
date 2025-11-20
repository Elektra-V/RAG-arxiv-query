# RAG Query - Academic Paper Search System

A Retrieval Augmented Generation system for querying academic papers using LangChain ReAct agent with vector database and arXiv search.

## Prerequisites

- Docker and Docker Compose
- Python 3.12+
- `uv` package manager (`pip install uv` or `brew install uv`)

## Quick Start

### 1. Clone repository
```bash
git clone <repo-url>
cd rag-api
```

### 2. Configure environment
```bash
cp env.example .env
```

Edit `.env`:
```bash
OPENAI_API_KEY="sk-your-key-here"
```

### 3. Install dependencies
```bash
uv sync
```

### 4. Start services
```bash
docker compose up --build -d
```

Services:
- Qdrant: `http://localhost:6334`
- LangChain API: `http://localhost:9010`
- LlamaIndex API: `http://localhost:9020`
- Ingestion API: `http://localhost:9030`

### 5. Verify Qdrant
```bash
curl http://localhost:6334/collections
```

Expected: `{"collections":[]}` or list of collections

### 6. Ingest papers
```bash
uv run rag-api-ingest --query "machine learning" --max-docs 10
```

### 7. Start LangGraph Studio
```bash
uv run langgraph dev
```

Open `http://localhost:8123` in browser.

---

## Usage

### LangGraph Studio
1. Open `http://localhost:8123`
2. Enter query (e.g., "What is quantum computing?")
3. Agent uses tools and returns answer

### API Endpoints

**LangChain API:**
```bash
curl -X POST http://localhost:9010/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is quantum computing?"}'
```

**API Documentation:**
- LangChain: `http://localhost:9010/docs`
- LlamaIndex: `http://localhost:9020/docs`
- Ingestion: `http://localhost:9030/docs`

**Health Checks:**
- LangChain: `http://localhost:9010/status`
- LlamaIndex: `http://localhost:9020/status`
- Ingestion: `http://localhost:9030/health`

---

## Docker Services

### Start all services
```bash
docker compose up -d
```

### Start specific service
```bash
docker compose up -d qdrant
docker compose up -d langchain
```

### View logs
```bash
docker compose logs -f langchain
docker compose logs -f qdrant
```

### Stop services
```bash
docker compose down
```

### Remove volumes (reset data)
```bash
docker compose down -v
```

---

## Configuration

**Required:**
- `OPENAI_API_KEY`: OpenAI API key

**Optional:**
- `OPENAI_MODEL`: Model name (default: `gpt-4o-mini`)
- `OPENAI_BASE_URL`: Gateway URL (e.g., OpenRouter)
- `ARXIV_SEARCH_MAX_RESULTS`: Max results (default: 5)
- `QDRANT_URL`: Qdrant URL (default: `http://localhost:6334`)

See `env.example` for all settings.

---

## Automatic Prompt Optimization (APO)

```bash
docker compose up -d qdrant
uv run python -m rag_api.services.langchain.train_apo
```

Optimized prompt saved to `optimized_prompt.txt` (auto-loaded).

**Configuration:** `rag_api/services/langchain/apo_config.py`

---

## Troubleshooting

**Port conflicts:**
```bash
docker compose down
lsof -ti :6334 | xargs kill -9
lsof -ti :9010 | xargs kill -9
```

**Check service status:**
```bash
docker compose ps
curl http://localhost:9010/status
curl http://localhost:6334/collections
```

**Empty results:**
```bash
uv run rag-api-ingest --query "topic" --max-docs 10
```

**Rebuild containers:**
```bash
docker compose build --no-cache
docker compose up -d
```

**View service logs:**
```bash
docker compose logs langchain
docker compose logs qdrant
```

---

## Architecture

```
User Query
    ↓
ReAct Agent
    ├─→ rag_query → Qdrant (6334)
    └─→ arxiv_search → arXiv API
    ↓
LLM Response
```

**Services:**
- Qdrant: Vector database (port 6334)
- LangChain API: ReAct agent (port 9010)
- LlamaIndex API: Alternative RAG (port 9020)
- Ingestion API: Paper ingestion (port 9030)

---

## Project Structure

```
rag-api/
├── .env                 # Configuration
├── docker-compose.yml   # Docker services
├── docker/              # Dockerfiles
├── rag_api/
│   ├── services/langchain/  # ReAct agent
│   ├── ingestion/           # Paper ingestion
│   └── clients/            # API clients
└── optimized_prompt.txt     # APO optimized prompt
```

---

## Development

**Local development (without Docker):**
```bash
# Start Qdrant only
docker compose up -d qdrant

# Run services locally
uv run python -m rag_api.services.langchain.app
uv run python -m rag_api.services.ingestion.app
```

**Testing:**
See `STUDIO_TEST_PROMPTS.md` for test queries.
