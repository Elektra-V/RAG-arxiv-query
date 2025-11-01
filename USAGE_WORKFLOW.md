# How to Use This RAG System - Complete Workflow

## 📋 Overview

This RAG system lets you query academic papers. Here's the complete workflow:

```
1. Setup → 2. Ingest Documents → 3. Query → 4. Debug
```

---

## 🎯 Complete Usage Workflow

### Step 1: Setup (One-time)

```bash
# 1. Configure your .env file with company API credentials
cp env.example .env
# Edit .env with your username/password

# 2. Start services
docker compose up --build

# 3. Verify services are running
curl http://localhost:9010/status  # LangChain API
curl http://localhost:9020/status  # LlamaIndex API  
curl http://localhost:6334/        # Qdrant
```

**Expected output:**
- All services return healthy status
- Qdrant shows version info
- Collections should be `[]` (empty, that's normal at first)

---

### Step 2: Ingest Documents (Required Before Querying)

**Your Qdrant database is empty!** You must populate it first.

**Option A: Using API** (if ingestion service is running):
```bash
curl -X POST http://localhost:9030/ingest \
  -H "Content-Type: application/json" \
  -d '{"query": "quantum computing", "max_docs": 5}'
```

**Option B: Using CLI** (recommended):
```bash
uv run rag-api-ingest run --query "quantum computing" --max-docs 5
```

**What happens:**
1. Downloads arXiv papers matching "quantum computing"
2. Creates embeddings using your configured embedding model (e.g., `text-embedding-3-small`)
3. Stores documents + embeddings in Qdrant collection `arxiv_papers`

**Verify it worked:**
```bash
curl http://localhost:9010/status | jq '.qdrant.collections'
# Should show: ["arxiv_papers"] instead of []
```

**Common issues:**
- **No documents found**: Try a different query (e.g., "machine learning", "neural networks")
- **Embedding errors**: Check your `OPENAI_EMBEDDING_MODEL` is valid
- **Qdrant connection failed**: Make sure Qdrant is running (`curl http://localhost:6334`)

---

### Step 3: Query the System

Now you can query! **You have 3 options:**

#### Option A: Query via LangChain API (Recommended)

```bash
curl -X POST http://localhost:9010/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the latest developments in quantum computing?", "debug": true}'
```

**Or use the web UI:**
- Open: http://localhost:9010/docs
- Find `/query` endpoint
- Click "Try it out"
- Enter your question
- Click "Execute"

**What happens:**
1. Agent receives your question
2. Searches Qdrant for relevant papers
3. Retrieves top matching documents
4. Sends question + context to LLM (your company API)
5. Returns answer with sources

---

#### Option B: Query via LangGraph Dev UI (Best for Debugging)

```bash
# Make sure dependencies are installed
uv sync

# Start LangGraph Dev
uv run langgraph dev
```

Then:
1. Open: http://localhost:8123
2. You'll see a beautiful UI
3. Type your question
4. Watch step-by-step execution
5. See logs, traces, and tool usage

**Why use this?**
- See exactly what the agent is doing
- View intermediate steps
- Debug why queries fail
- Better than terminal logs!

---

#### Option C: Query via LlamaIndex UI

1. Open: http://localhost:9020/
2. Enter your question in the form
3. Click "Submit Query"
4. See answer with debug info

---

## 🔍 Understanding the Query Flow

When you ask: *"What are the latest developments in quantum computing?"*

```
1. Question received → Agent decides: use RAG or web search?
2. If RAG: 
   - Query → Qdrant vector search
   - Find top 3-5 relevant paper chunks
   - Send to LLM: "Based on these papers: [chunks], answer: [question]"
3. If web search:
   - Use DuckDuckGo to find recent info
   - Combine with RAG results
4. LLM generates answer using both sources
5. Return answer to you
```

---

## 📊 Check System Health

**Quick health check:**
```bash
# Check all services
curl http://localhost:9010/status | jq '.'
curl http://localhost:9020/status | jq '.'
curl http://localhost:6334/collections | jq '.'
```

**What to look for:**
- ✅ `status: "healthy"`
- ✅ `qdrant.connected: true`
- ✅ `collections: ["arxiv_papers"]` (not empty!)
- ✅ `configuration.llm_provider: "openai"`
- ✅ `configuration.embedding_provider: "openai"`

---

## 🐛 Debugging Common Issues

### Issue: Query returns no results

**Check:**
```bash
# 1. Is Qdrant populated?
curl http://localhost:9010/status | jq '.qdrant.collections'
# Should NOT be []

# 2. Check ingestion worked
# Look at ingestion logs when you ran: uv run rag-api-ingest run
# Should see: "Ingested X documents into Qdrant"
```

**Fix:**
- Run ingestion again if collections is empty
- Try a different query topic if no papers found

---

### Issue: LLM API errors

**Check logs:**
```bash
# Docker logs
docker compose logs langchain | tail -50

# Or if running locally, check terminal output
```

**Common errors:**
- `401 Unauthorized` → Check username/password in `.env`
- `Model not found` → Run `check_company_models.py` and update `OPENAI_MODEL`
- `Connection timeout` → Check `OPENAI_BASE_URL` is correct

---

### Issue: Embedding errors

**Check:**
```bash
# Verify embedding model exists
curl http://localhost:9010/status | jq '.configuration.embedding_provider'
# Should be "openai" and model should exist
```

**Fix:**
- Run `check_company_models.py` to see available embedding models
- Update `OPENAI_EMBEDDING_MODEL` in `.env`

---

## 📝 Typical Workflow Summary

```bash
# 1. Start services (one-time)
docker compose up -d

# 2. Ingest documents (whenever you want new papers)
uv run rag-api-ingest run --query "your topic" --max-docs 5

# 3. Query the system
curl -X POST http://localhost:9010/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Your question here"}'

# 4. Or use LangGraph Dev for interactive debugging
uv run langgraph dev
# Then open http://localhost:8123
```

---

## 🎓 Key Points to Remember

1. **Ingestion must happen first** - Empty Qdrant = no query results
2. **Query via API** - Most straightforward for production/testing
3. **Query via LangGraph Dev** - Best for debugging and understanding flow
4. **Check status endpoints** - They tell you if everything is connected
5. **Logs are your friend** - Check Docker logs or terminal output when things fail

---

## 🚀 Next Steps After Setup

1. ✅ Ingest documents on your topic of interest
2. ✅ Try a query via API or LangGraph Dev
3. ✅ Check logs to see what's happening
4. ✅ Experiment with different questions
5. ✅ Debug issues using status endpoints and logs

That's it! You now know how to use the system end-to-end.

