# RAG Query - Academic Paper Search System

A Retrieval Augmented Generation system for querying academic papers using LangChain ReAct agent with vector database and arXiv search.

## Quick Start

```bash
# 1. Configure environment
cp env.example .env
# Edit .env with your OPENAI_API_KEY

# 2. Start services
docker compose up --build

# 3. Ingest papers (optional, in another terminal)
uv run rag-api-ingest --query "machine learning" --max-docs 5

# 4. Start LangGraph Studio (in another terminal)
uv run langgraph dev
```

Access Studio at `http://localhost:8123`

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

## Usage

### LangGraph Studio
1. Run `uv run langgraph dev`
2. Open the Studio URL in your browser
3. Enter your question

### API
```bash
curl -X POST http://localhost:9010/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is quantum computing?"}'
```

API docs: `http://localhost:9010/docs`

---

## Automatic Prompt Optimization (APO)

Optimize the agent's prompt automatically using Agent-lightning:

```bash
# Ensure Qdrant is running and has ingested papers
docker compose up -d

# Run optimization
uv run python -m rag_api.services.langchain.train_apo
```

The optimized prompt is saved to `optimized_prompt.txt` and automatically loaded by the agent.

**Configuration:** Edit `rag_api/services/langchain/apo_config.py` to adjust:
- `num_iterations`: Training iterations (default: 2)
- `samples_per_iteration`: Samples per iteration (default: 3)
- `num_runners`: Parallel workers (default: 1)

---

## Architecture

```
User Query
    ↓
ReAct Agent
    ├─→ rag_query (Vector DB) → Qdrant
    └─→ arxiv_search → arXiv API
    ↓
LLM Response
```

---

## Troubleshooting

**Port conflicts:**
```bash
docker compose down
lsof -ti :6334 | xargs kill -9  # Qdrant
```

**Empty results:**
- Run ingestion: `uv run rag-api-ingest --query "topic" --max-docs 5`

**Studio connection issues:**
- Ensure LangGraph server is running
- Use Chrome browser
- Check base URL in LangSmith Studio matches local URL

---

## Project Structure

```
rag-api/
├── .env                 # Your configuration
├── docker-compose.yml   # Qdrant service
├── rag_api/
│   ├── services/langchain/  # ReAct agent
│   ├── ingestion/           # Paper ingestion
│   └── clients/              # API clients
└── optimized_prompt.txt      # APO optimized prompt (after training)
```

---

## How It Works

1. **Ingestion**: Papers are downloaded from arXiv, embedded, and stored in Qdrant
2. **Query**: User asks a question
3. **RAG Search**: Agent searches ingested papers in vector database
4. **arXiv Search**: If needed, agent searches arXiv API directly
5. **Response**: Agent synthesizes answer with citations

The agent automatically uses the optimized prompt if available, otherwise uses the baseline prompt.

---

## Testing

See `STUDIO_TEST_PROMPTS.md` for edge case test queries.
