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

**Option 1: Use LangGraph Dev** (Recommended - Best UI):
```bash
# Make sure Qdrant is running first
docker run -d -p 6333:6333 qdrant/qdrant

# Then start LangGraph Dev
langgraph dev --graph rag_api.services.langchain.graph:graph
```
Open: **http://localhost:8123** - Beautiful built-in UI!

**Option 2: Use Docker Compose** (For full stack):
```bash
docker compose up --build
```
This starts:
- Qdrant on port 6333
- LangChain API on port 8009
- LlamaIndex API on port 8080

#### Step 4: Open Browser
- **LangGraph Dev UI**: http://localhost:8123 (if using langgraph dev)
- **LangChain API**: http://localhost:8009/ (if using docker/compose)
- **LlamaIndex**: http://localhost:8080/

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
You need Qdrant running. Install it or use Docker:
```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

#### Step 6: Start with LangGraph Dev (Recommended - Better UI)
```bash
langgraph dev --graph rag_api.services.langchain.graph:graph
```

This gives you:
- Beautiful UI for debugging at http://localhost:8123
- Real-time logs and traces
- Step-by-step execution view
- Much better than terminal!

**Alternative**: If you want the API server instead:
```bash
uv run rag_api/services/langchain/app.py
```
Then access: http://localhost:8009/

---

## 🎨 LangGraph Dev (Built-in Debugging UI)

**LangGraph Dev** is the official tool from LangGraph - gives you a beautiful UI for debugging without building anything yourself!

### Using LangGraph Dev:

**Start it:**
```bash
langgraph dev --graph rag_api.services.langchain.graph:graph
```

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
- Start everything: `docker compose up`
- Stop everything: `docker compose down`
- View logs: `docker compose logs -f langchain`

**LangGraph Dev** (recommended for debugging):
- Start: `langgraph dev --graph rag_api.services.langchain.graph:graph`
- UI: http://localhost:8123

**API Server** (for production/testing):
- Start: `uv run rag_api/services/langchain/app.py`
- API: http://localhost:8009/
- Docs: http://localhost:8009/docs

**Other commands:**
- Check models: `uv run python check_company_models.py`
- Check status: `curl http://localhost:8009/status`

---

## 🔧 Troubleshooting

**"Connection failed"**
- Run `check_company_models.py` to test your credentials
- Make sure username and password in `.env` are correct

**"Model not found"**
- Run `check_company_models.py` to see available models
- Update `OPENAI_MODEL` in `.env` with one from the list

**"Service won't start"**
- Make sure `.env` file exists
- Check that you ran `uv sync`
- Look at the error message in terminal

---

## 📂 What This Project Does

- **LangChain Service** (port 8009): Agent with RAG + web search
- **LlamaIndex Service** (port 8080): Direct RAG queries
- Both connect to your company's LLM API
- Both use Qdrant for document storage

---

## 🎯 That's It!

Follow the 6 steps above. If something breaks, check the Troubleshooting section.

**Need help?** Check the terminal output - error messages will tell you what's wrong.
