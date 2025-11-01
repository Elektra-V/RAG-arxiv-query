# RAG API - Quick Start Guide

**One README. Everything you need to run this project.**

---

## 🚀 Setup (Choose One: Docker or Local)

### Option A: Docker (Recommended - Everything in Containers)

#### Step 1: Copy Configuration File
```bash
cp env.example .env
```

#### Step 2: Edit `.env` File
Open `.env` and replace these lines with your actual credentials:

```env
OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
OPENAI_AUTH_USERNAME="your-actual-username"
OPENAI_AUTH_PASSWORD="your-actual-password"
OPENAI_API_KEY="xxxx"
OPENAI_MODEL="gpt-4"  # or "gpt-4o", "gpt-4o-mini", etc.
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="openai"
```

**Important**: Use your real username and password from your company.

#### Step 3: Start Services

**Option 1: Use Docker Compose** (Recommended - Handles everything):
```bash
# First time or if you see "orphan containers" warning, use:
docker compose up --build --remove-orphans

# Or for normal use:
docker compose up --build
```
This automatically:
- Installs all dependencies using UV inside containers
- Starts Qdrant on port 6334
- Starts LangChain API on port 9010
- Starts LlamaIndex API on port 9020
- Everything is self-contained!

**Option 2: Use LangGraph Dev Locally** (For debugging):

⚠️ **IMPORTANT**: 
- **Don't start Qdrant separately** if Docker Compose is already running!
- Docker Compose already started Qdrant on port 6334
- Just use the Qdrant that's already running

**Install dependencies:**
```bash
uv sync  # CRITICAL - must do this FIRST!
```

**Then start LangGraph Dev:**
```bash
uv run langgraph dev
```
This will use `langgraph.json` config file to find your graph.
Open: **http://localhost:8123** - Beautiful built-in UI!

**Note**: If Docker Compose is NOT running and you want to use LangGraph Dev:
```bash
# First start Qdrant
docker run -d -p 6334:6333 qdrant/qdrant

# Then start langgraph dev
uv run langgraph dev
```

#### Step 4: Ingest Documents (IMPORTANT - Do This First!)
**Before querying, you need to populate Qdrant with documents:**

**Option A: Using API (recommended):**
```bash
curl -X POST http://localhost:9030/ingest \
  -H "Content-Type: application/json" \
  -d '{"query": "quantum computing", "max_docs": 5}'
```

**Option B: Using CLI:**
```bash
# If running locally (not Docker)
uv run rag-api-ingest run --query "quantum computing" --max-docs 5

# Or use defaults from .env
uv run rag-api-ingest run
```

**This will:**
- Download arXiv papers matching your query
- Create embeddings using your configured embedding model
- Store them in Qdrant for RAG queries

**Check if it worked:**
```bash
curl http://localhost:9010/status | grep collections
# Should show collections: ["arxiv_papers"] instead of []
```

#### Step 5: Open Browser and Test
- **LangChain API**: http://localhost:9010/ (query endpoint)
- **LangChain Docs**: http://localhost:9010/docs
- **LlamaIndex UI**: http://localhost:9020/ (debug interface)
- **LangGraph Dev UI**: http://localhost:8123 (if using langgraph dev)

---

### Option B: Local (Without Docker)

#### Step 1: Copy Configuration File
```bash
cp env.example .env
```

#### Step 2: Edit `.env` File
Same as Docker option above.

#### Step 3: Check Available Models
```bash
uv run python check_company_models.py
```

This shows available models. Update `OPENAI_MODEL` in `.env` if needed.

#### Step 4: Install Dependencies
```bash
uv sync
```

#### Step 5: Start Qdrant (if not using Docker)
**Only if Docker Compose is NOT running!** If Docker Compose is running, skip this step.

```bash
# Using port 6334 to avoid conflicts with original project
docker run -d -p 6334:6333 qdrant/qdrant
```
**Important**: Update `QDRANT_URL="http://localhost:6334"` in your `.env` file.

#### Step 6: Ingest Documents (CRITICAL - Do This Before Querying!)
**Your Qdrant database is empty! You need to populate it first:**

```bash
# Option 1: Using CLI (recommended)
uv run rag-api-ingest run --query "quantum computing" --max-docs 5

# Option 2: Using defaults from .env
uv run rag-api-ingest run

# Option 3: Using API endpoint (if ingestion service is running)
curl -X POST http://localhost:9030/ingest \
  -H "Content-Type: application/json" \
  -d '{"query": "quantum computing", "max_docs": 5}'
```

**This downloads arXiv papers, creates embeddings, and stores them in Qdrant.**

**Verify it worked:**
```bash
curl http://localhost:9010/status | grep collections
# Should show: "collections":["arxiv_papers"] instead of []
```

#### Step 7: Start with LangGraph Dev (Optional - Better UI)
```bash
uv run langgraph dev
```
This uses `langgraph.json` config file (already created).

This gives you:
- Beautiful UI for debugging at http://localhost:8123
- Real-time logs and traces
- Step-by-step execution view
- Much better than terminal!

**Alternative**: If you want the API server instead:
```bash
uv run rag_api/services/langchain/app.py
```
Then access: http://localhost:9010/

---

## 🎨 LangGraph Dev (Built-in Debugging UI)

**LangGraph Dev** is the official tool from LangGraph - gives you a beautiful UI for debugging without building anything yourself!

### Using LangGraph Dev:

⚠️ **IMPORTANT**: Install dependencies first!
```bash
uv sync  # Must do this FIRST!
```

**Then start it:**
```bash
uv run langgraph dev
```
This uses the `langgraph.json` configuration file.

**Access the UI:**
- Open: http://localhost:8123 (or the port shown in terminal)
- Interactive UI to test your agent
- See logs, traces, and execution flow
- Step-by-step debugging
- All built-in - no custom code needed!

**Optional: LangSmith Integration** (for cloud tracing):
1. Get API key from https://smith.langchain.com/
2. Add to `.env`:
   ```env
   LANGSMITH_API_KEY="your-key"
   LANGSMITH_TRACING=true
   ```
3. Traces will also appear in LangSmith cloud dashboard

**Note**: `langgraph dev` is included when you run `uv sync`. No extra installation needed!

---

## 📝 Quick Reference

**Docker commands:**
- Start everything: `docker compose up --build`
- Start and clean orphans: `docker compose up --build --remove-orphans`
- Stop everything: `docker compose down`
- Stop and remove volumes: `docker compose down -v`
- View logs: `docker compose logs -f langchain`

**LangGraph Dev** (recommended for debugging):
- **First**: `uv sync` (install dependencies)
- **Then**: `uv run langgraph dev` (uses langgraph.json config)
- UI: http://localhost:8123
- **Note**: If Docker Compose is running, Qdrant is already available - don't start it again!

**API Server** (for production/testing):
- Start: `uv run rag_api/services/langchain/app.py`
- API: http://localhost:9010/ (changed from 8009)
- Docs: http://localhost:9010/docs

**Ingestion commands:**
- **Ingest documents** (must do this first!): `uv run rag-api-ingest run`
- **Ingest via API**: `curl -X POST http://localhost:9030/ingest -H "Content-Type: application/json" -d '{"query": "quantum computing", "max_docs": 5}'`
- **Check status**: `curl http://localhost:9010/status` (look for collections in response)

**Other commands:**
- Check models: `uv run python check_company_models.py`
- Check Qdrant: `curl http://localhost:6334/collections` (should show arxiv_papers)

**Note**: Ports changed to 9000+ range to avoid conflicts with original project:
- LangChain: 9010 (was 8009)
- LlamaIndex: 9020 (was 8080)
- Ingestion: 9030 (was 8090)
- Qdrant: 6334 (was 6333)

---

## 🔧 Troubleshooting

**"Connection failed"**
- Run `check_company_models.py` to test your credentials
- Make sure username and password in `.env` are correct

**"Model not found"**
- Run `check_company_models.py` to see available models
- Update `OPENAI_MODEL` in `.env` with one from the list

**"Service won't start" / "Module not found" / "Command not found"**
- **CRITICAL**: Did you run `uv sync` first? This installs all dependencies!
- For Docker: `docker compose up --build` installs dependencies automatically
- For local: Must run `uv sync` before `langgraph dev` or any service
- Make sure `.env` file exists
- Look at the error message in terminal

**"langgraph: command not found"**
- Run `uv sync` first to install dependencies
- Then use `uv run langgraph dev ...` instead of just `langgraph dev`

**"port is already allocated" / "Bind failed"**
- **If Docker Compose is running**: Don't start Qdrant separately! It's already running.
- **If you want to stop everything first**: `docker compose down`
- **If you need Qdrant separately**: Stop Docker Compose first, or use a different port
- Find what's using the port:
  ```bash
  docker ps | grep 6334  # Find container using port 6334
  docker stop <container-id>  # Stop it
  ```

**"No such option: --graph"**
- Use `uv run langgraph dev` (without `--graph` flag)
- The project includes `langgraph.json` which configures the graph automatically

**"Required package 'langgraph-api' is not installed"**
- Run: `uv add "langgraph-cli[inmem]"` (this explicitly adds the inmem extra)
- Or: `uv sync` should install it, but if not, use the add command above
- The `[inmem]` extra is required for `langgraph dev` to work

**"collections": [] - Qdrant is empty**
- **You need to ingest documents first!**
- Run: `uv run rag-api-ingest run`
- Or use API: `curl -X POST http://localhost:9030/ingest -H "Content-Type: application/json" -d '{"query": "quantum computing", "max_docs": 5}'`
- Without documents, queries will return no results

**Ingestion endpoint returns 404**
- Ingestion service endpoint is `/ingest` not `/`
- Use: `curl -X POST http://localhost:9030/ingest`
- Check if service is running: `docker compose ps` or `curl http://localhost:9030/ingest` (should return method not allowed, not 404)

**"Found orphan containers" warning**
- Use `--remove-orphans` flag:
  ```bash
  docker compose up --build --remove-orphans
  ```
- This cleans up old containers from previous configurations

---

## 📂 What This Project Does

- **LangChain Service** (port 9010): Agent with RAG + web search
- **LlamaIndex Service** (port 9020): Direct RAG queries
- Both connect to your company's LLM API
- Both use Qdrant for document storage (port 6334)

---

## 🎯 That's It!

Follow the 6 steps above. If something breaks, check the Troubleshooting section.

**Need help?** Check the terminal output - error messages will tell you what's wrong.
