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

---

## Automatic Prompt Optimization (APO)

The project includes Automatic Prompt Optimization using Agent-lightning to improve the agent's system prompt through iterative training.

### Running APO Training

1. **Ensure dependencies are installed:**
   ```bash
   uv sync
   ```

2. **Prepare your environment:**
   - Ensure `OPENAI_API_KEY` is set in `.env`
   - Ensure Qdrant is running (for RAG queries during training)
   - Optionally ingest some papers for better training data:
     ```bash
     uv run rag-api-ingest --query "machine learning" --max-docs 10
     ```

3. **Run training:**
   ```bash
   uv run python -m rag_api.services.langchain.train_apo
   ```

   The training script will:
   - Load training and validation datasets
   - Evaluate baseline prompt performance
   - Run APO optimization for multiple iterations
   - Evaluate optimized prompt performance
   - Display comparison metrics
   - Save optimized prompt to `optimized_prompt.txt`

### Using Optimized Prompts

After training, you can use the optimized prompt in production:

**Option 1: Load from file**
```python
from pathlib import Path
from rag_api.services.langchain.agent import build_agent

# Load optimized prompt
optimized_prompt = Path("optimized_prompt.txt").read_text()

# Build agent with optimized prompt
agent = build_agent(prompt_template=optimized_prompt)
```

**Option 2: Update agent.py directly**
Replace the baseline prompt in `agent.py` with the optimized prompt from `optimized_prompt.txt`.

### APO Configuration

You can customize APO training by modifying `rag_api/services/langchain/apo_config.py`:

- `num_runners`: Number of parallel runners (default: 4)
- `num_iterations`: Training iterations (default: 10)
- `samples_per_iteration`: Samples per iteration (default: 8)
- `use_validation`: Use validation set (default: True)

### Training Datasets

Training datasets are defined in `rag_api/services/langchain/apo_dataset.py`:

- `load_training_dataset()`: Returns training queries with evaluation criteria
- `load_validation_dataset()`: Returns validation queries

You can customize these datasets by adding your own queries with:
- `query`: The research question
- `expected_tool_usage`: Which tools should be used (optional)
- `expected_output_contains`: Key phrases that should appear (optional)
- `quality_score`: Target quality score (optional)

### Evaluation Criteria

The grader (`rag_response_grader`) evaluates responses based on:

1. **Tool Usage (30%)**: Did the agent use `rag_query` or `arxiv_search`?
2. **Output Format (20%)**: Does the response follow the TOOL_LOG structure?
3. **Completeness (30%)**: Is the response complete and error-free?
4. **Response Quality (20%)**: Does it include citations and relevant content?

### Troubleshooting APO Training

**Training fails with API errors:**
- Verify `OPENAI_API_KEY` is set correctly
- Check API rate limits and quotas
- Reduce `num_runners` in config if hitting rate limits

**Low scores on all tasks:**
- Ensure Qdrant is running and has ingested papers
- Check that tools (`rag_query`, `arxiv_search`) are working correctly
- Review dataset queries to ensure they're appropriate

**No improvement after training:**
- The baseline prompt may already be optimal
- Try increasing `num_iterations` for more optimization
- Review evaluation criteria in `rag_response_grader`
