# RAG API - Complete Guide

**Everything you need in one place. Simple and clear.**

---

## 🚀 Quick Start (3 Steps)

### 1. Setup Configuration
```bash
cp env.example .env
# Edit .env with your API credentials (see below)
```

### 2. Start Services
```bash
# Option A: Docker (easiest - handles everything)
docker compose up --build

# Option B: Local (for debugging)
uv sync
docker run -d -p 6334:6333 qdrant/qdrant
uv run langgraph dev --tunnel  # Opens Studio UI via tunnel (Safari-compatible)
# Note: Use --tunnel flag for Safari or if localhost is blocked
```

### 3. Ingest Documents (Required Before Querying!)
```bash
uv run rag-api-ingest --query "quantum computing" --max-docs 5
```

**Done!** Now you can query: http://localhost:9010/docs

---

## 📝 Configuration (.env file)

Open `.env` and configure one of these options:

### Option 1: Company API (Production)
```env
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="openai"
OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
OPENAI_AUTH_USERNAME="your-username"
OPENAI_AUTH_PASSWORD="your-password"
OPENAI_API_KEY="xxxx"
OPENAI_MODEL="gpt-4"
OPENAI_EMBEDDING_MODEL="text-embedding-3-small"
```

**Check available models:**
```bash
uv run python check_company_models.py
```

### Option 2: Local Testing (Free APIs)

**⚠️ IMPORTANT NOTES:**
- **402 Error**: OpenRouter requires credits for paid models
- **429 Error**: Free models are rate-limited (wait 2-3 minutes or switch to Together AI)

**Option 2A: Together AI (Free Tier - Recommended)**
1. Go to: https://together.ai/
2. Sign up (no credit card for free tier)
3. Get API key from dashboard
4. Add to `.env`:

```env
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="huggingface"  # FREE - no key needed!
OPENAI_BASE_URL="https://api.together.xyz/v1"
OPENAI_API_KEY="your-together-key"
OPENAI_MODEL="meta-llama/Llama-3-8b-chat-hf"
HUGGINGFACE_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

**Option 2B: Ollama (100% Free, Local)**
1. Install: `brew install ollama` (or see https://ollama.ai/)
2. Start: `ollama serve`
3. Pull model: `ollama pull llama3.1:8b`
4. Add to `.env`:

```env
LLM_PROVIDER="ollama"
EMBEDDING_PROVIDER="huggingface"  # FREE!
OLLAMA_MODEL="llama3.1:8b-instruct-q4_0"
OLLAMA_BASE_URL="http://localhost:11434"
HUGGINGFACE_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

**Option 2C: OpenRouter (Free Model Available!)**
- **FREE model**: `qwen/qwen3-coder:free` (no credits needed!)
- Sign up at: https://openrouter.ai/ (free account)
- Get API key from dashboard
- Add to `.env`:

```env
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="huggingface"
OPENAI_BASE_URL="https://openrouter.ai/api/v1"
OPENAI_API_KEY="your-openrouter-key"
OPENAI_MODEL="qwen/qwen3-coder:free"  # FREE!
HUGGINGFACE_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

**Note**: Some OpenRouter models require credits, but `qwen/qwen3-coder:free` is completely free!

### Option 3: Test Ingestion Only (No LLM API Key)
```env
LLM_PROVIDER="openai"  # Not used for ingestion
EMBEDDING_PROVIDER="huggingface"  # FREE!
HUGGINGFACE_MODEL="sentence-transformers/all-MiniLM-L6-v2"
OPENAI_API_KEY=""  # Leave empty
```

This tests: Download papers → Create embeddings → Store in Qdrant  
(No LLM querying, but ingestion works!)

---

## 📖 Complete Workflow

### Step 1: Ingest Documents (MUST DO FIRST!)

**Your database is empty!** Populate it:

```bash
uv run rag-api-ingest --query "machine learning" --max-docs 5
```

**What happens:**
- Downloads arXiv papers
- Creates embeddings
- Stores in Qdrant

**Verify:**
```bash
curl http://localhost:9010/status | grep collections
# Should show: ["arxiv_papers"] instead of []
```

### Step 2: Query the System

**Option A: Via API**
```bash
curl -X POST http://localhost:9010/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is quantum computing?", "debug": true}'
```

**Option B: Via LangGraph Dev (Best for debugging)**
```bash
# With tunnel (for Safari or external access):
uv run langgraph dev --tunnel
# Opens Studio UI via Cloudflare tunnel - works in Safari!

# Without tunnel (localhost only):
uv run langgraph dev
# Opens UI at http://localhost:8123 - interactive debugging!
```

**Option C: Via Web UI**
- LangChain API: http://localhost:9010/docs
- LlamaIndex UI: http://localhost:9020/

### Step 3: Debug & Check Status

```bash
# Detailed system info
curl http://localhost:9010/debug | jq '.'

# Check service status
curl http://localhost:9010/status

# Check Qdrant
curl http://localhost:6334/collections
```

---

## 🔧 Troubleshooting

**"Connection failed"**
- Check credentials in `.env`
- Test with: `uv run python check_company_models.py`

**"Model not found"**
- List models: `uv run python check_company_models.py`
- Update `OPENAI_MODEL` in `.env`

**"port is already allocated"**
- Docker Compose already started Qdrant - don't start it again!
- Or stop everything: `docker compose down`

**"collections": [] - Empty database**
- **You must ingest documents first!**
- Run: `uv run rag-api-ingest --query "topic" --max-docs 5`

**"langgraph: command not found"**
- Run: `uv sync` first
- Then use: `uv run langgraph dev`

**"Module not found"**
- **CRITICAL**: Run `uv sync` before starting services!

---

## 📂 Project Structure

```
rag-api/
├── .env                      # Your configuration (copy from env.example)
├── README.md                 # This file - everything you need!
├── env.example               # Configuration template
├── pyproject.toml            # Dependencies
├── docker-compose.yml        # Docker setup
├── langgraph.json            # LangGraph config
├── check_company_models.py   # List available models
├── check_setup.py            # Verify your setup
└── rag_api/                  # Source code
    ├── settings.py           # Configuration
    ├── clients/              # API clients (OpenAI, Qdrant)
    ├── ingestion/           # Document ingestion
    └── services/            # API services (LangChain, LlamaIndex)
```

---

## 🎯 What This Project Does

- **Downloads** arXiv papers based on query
- **Creates embeddings** (vector representations)
- **Stores** in Qdrant (vector database)
- **Queries** using RAG (Retrieval Augmented Generation)
- **Answers** questions using LLM + retrieved context

**Services:**
- LangChain API (port 9010): RAG agent with web search
- LlamaIndex API (port 9020): Direct RAG queries
- Ingestion (port 9030): Document processing
- Qdrant (port 6334): Vector database

---

## 🚀 Docker Commands

```bash
# Start everything
docker compose up --build

# Stop everything
docker compose down

# View logs
docker compose logs -f langchain

# Clean start (remove old containers)
docker compose up --build --remove-orphans
```

---

## 💡 Tips

- **Start with ingestion-only testing** (no LLM key needed) to verify pipeline
- **Use LangGraph Dev** (`uv run langgraph dev`) for best debugging experience
- **Check status** with `/debug` endpoint for detailed system info
- **Ports changed** to 9000+ range to avoid conflicts

---

**Need help?** Check troubleshooting section above or use `/debug` endpoint!
