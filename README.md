# RAG Query - Academic Paper Search System

A Retrieval Augmented Generation system for querying academic papers using LangChain ReAct agent with vector database and arXiv search.

## Prerequisites

- Docker and Docker Compose
- Python 3.10+
- `uv` package manager (`pip install uv` or `brew install uv`)

## Setup

### 1. Clone and navigate
```bash
cd rag-api
```

### 2. Configure environment
```bash
cp env.example .env
```

Edit `.env` and set:
```bash
OPENAI_API_KEY="sk-your-key-here"
```

### 3. Install dependencies
```bash
uv sync
```

### 4. Start Qdrant (vector database)
```bash
docker compose up --build -d
```

Verify Qdrant is running:
```bash
curl http://localhost:6334/collections
```

### 5. Ingest papers (required before querying)
```bash
uv run rag-api-ingest --query "machine learning" --max-docs 10
```

### 6. Start LangGraph Studio
```bash
uv run langgraph dev
```

Open `http://localhost:8123` in your browser.

---

## Usage

### Query via Studio
1. Open `http://localhost:8123`
2. Enter a question (e.g., "What is quantum computing?")
3. Agent will use tools and return answer

### Query via API
```bash
curl -X POST http://localhost:9010/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is quantum computing?"}'
```

API docs: `http://localhost:9010/docs`

---

## Configuration

**Required:**
- `OPENAI_API_KEY`: Your OpenAI API key

**Optional:**
- `OPENAI_MODEL`: Model name (default: `gpt-4o-mini`)
- `OPENAI_BASE_URL`: Gateway URL (e.g., OpenRouter)
- `ARXIV_SEARCH_MAX_RESULTS`: Max results (default: 5)

See `env.example` for all settings.

---

## Automatic Prompt Optimization (APO)

```bash
docker compose up -d
uv run python -m rag_api.services.langchain.train_apo
```

Optimized prompt saved to `optimized_prompt.txt` and auto-loaded.

**Config:** Edit `rag_api/services/langchain/apo_config.py`

---

## Troubleshooting

**Port conflicts:**
```bash
docker compose down
lsof -ti :6334 | xargs kill -9
```

**Empty results:**
```bash
uv run rag-api-ingest --query "topic" --max-docs 10
```

**Studio connection:**
- Ensure `uv run langgraph dev` is running
- Use Chrome browser
- Check URL matches console output

---

## Project Structure

```
rag-api/
├── .env                 # Configuration
├── docker-compose.yml   # Qdrant service
├── rag_api/
│   ├── services/langchain/  # ReAct agent
│   ├── ingestion/           # Paper ingestion
│   └── clients/              # API clients
└── optimized_prompt.txt      # APO optimized prompt
```

---

## How It Works

1. Papers ingested → embedded → stored in Qdrant
2. User query → agent searches vector DB
3. If needed → agent searches arXiv API
4. Agent synthesizes answer with citations

Agent auto-loads optimized prompt if available.

---

## Testing

See `STUDIO_TEST_PROMPTS.md` for test queries.
