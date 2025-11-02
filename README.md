# RAG API - OpenAI Platform

**Retrieval Augmented Generation system using OpenAI Platform for academic paper queries.**

## ✨ Features

- OpenAI Platform integration with API key authentication
- Fast embeddings via OpenAI Platform
- Ready-to-use RAG pipeline with academic paper queries
- Simple, clean codebase

---

## 🚀 Quick Start

### 1. Setup Configuration

```bash
cp env.example .env
```

### 2. Configure OpenAI Platform

Edit `.env` with your OpenAI API key:

```env
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="openai"
OPENAI_API_KEY="sk-..."  # Your OpenAI Platform API key
OPENAI_MODEL="gpt-4o-mini"  # OpenAI model
# OPENAI_EMBEDDING_MODEL=""  # Leave empty for auto-detection (defaults to text-embedding-3-small)
```

### 3. Install Dependencies & Start Services

```bash
# Install dependencies
uv sync

# Start Qdrant (vector database)
docker compose up -d qdrant

# Ingest documents (REQUIRED before querying!)
uv run rag-api-ingest --query "machine learning" --max-docs 5

# Start server
uv run langgraph dev
# Access Studio at: http://localhost:8123
# (For cluster access, see CLUSTER_ACCESS.md)
```

**Done!** The Studio UI URL will be displayed - use it to query your RAG system.

---

## 📋 Configuration Reference

### Required Settings

| Setting | Description | Example |
|---------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI Platform API key | `"sk-..."` |
| `OPENAI_MODEL` | OpenAI model to use | `"gpt-4o-mini"` (default)<br/>`"gpt-4o"`, `"gpt-3.5-turbo"` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model (optional) | Leave empty for auto-detection<br/>Defaults to `"text-embedding-3-small"` |

### Optional Settings

- `EMBEDDING_PROVIDER`: `"openai"` (default, recommended) or `"huggingface"` (free local, CPU only, slower)
- `ARXIV_QUERY`: Default query for ingestion
- `ARXIV_MAX_DOCS`: Maximum documents to ingest

---

## 📖 Complete Workflow

### Step 1: Ingest Documents (MUST DO FIRST!)

Your database starts empty. Populate it:

```bash
uv run rag-api-ingest --query "quantum computing" --max-docs 5
```

**What happens:**
- Downloads arXiv papers matching your query
- Creates embeddings (vector representations)
- Stores in Qdrant vector database

**Verify ingestion:**
```bash
curl http://localhost:6334/collections/arxiv_papers
# Should show your documents with points_count > 0
```

### Step 2: Query the System

**Option A: LangGraph Studio**

**On Linux Cluster or Local Machine:**
```bash
# Run without tunnel (tunnel may not work on cluster networks)
uv run langgraph dev

# Access Studio at: http://localhost:8123
# Access API docs at: http://localhost:9010/docs
```

**For Remote Cluster Access:**
Use SSH port forwarding (see `CLUSTER_ACCESS.md` for details):
```bash
# On local machine: Forward ports
ssh -L 8123:localhost:8123 -L 9010:localhost:9010 user@cluster

# On cluster: Start server (without tunnel)
uv run langgraph dev

# On local browser: http://localhost:8123
```

**Option B: Direct API**
```bash
curl -X POST http://localhost:9010/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is quantum computing?", "debug": true}'
```

**Option C: API Documentation**
- Open: http://localhost:9010/docs
- Interactive API testing

### Step 3: Debug & Status

```bash
# Detailed system info
curl http://localhost:9010/debug | jq '.'

# Service status
curl http://localhost:9010/status

# Qdrant collections
curl http://localhost:6334/collections
```

---

## 🔧 Troubleshooting

### "Connection failed" or "Unauthorized"
- Verify `OPENAI_API_KEY` in `.env` is correct
- Check if your API key has sufficient credits
- Verify network connectivity

### "Model not found"
- Check available models: https://platform.openai.com/docs/models
- Update `OPENAI_MODEL` in `.env` with correct model name

### "collections": [] - Empty database
- **You must ingest documents first!**
- Run: `uv run rag-api-ingest --query "topic" --max-docs 5`

### "Port already in use"
- **Check what's using the port**: `lsof -i :6334` or `docker ps | grep qdrant`
- **Stop containers**: `docker compose down`
- **Remove stuck containers**: `docker compose down --remove-orphans`

### "langgraph: command not found"
- Run: `uv sync` first
- Then: `uv run langgraph dev`

### Cloudflare tunnel fails on cluster
- Use `uv run langgraph dev` without `--tunnel` flag
- For remote access, use SSH port forwarding (see `CLUSTER_ACCESS.md`)
- Access Studio at `http://localhost:8123` or via port forwarding

---

## 📂 Project Structure

```
rag-api/
├── .env                      # Your configuration (copy from env.example)
├── env.example               # Configuration template
├── rag_api/
│   ├── settings.py           # Configuration loader
│   ├── clients/              # API clients (OpenAI, Qdrant, embeddings)
│   ├── ingestion/            # Document ingestion pipeline
│   └── services/             # API services (LangChain, LlamaIndex)
└── docker-compose.yml         # Docker services (Qdrant)
```

---

## 🎯 What This System Does

1. **Downloads** arXiv papers based on search query
2. **Creates embeddings** (vector representations using OpenAI)
3. **Stores** in Qdrant (vector database for similarity search)
4. **Retrieves** relevant documents for user questions
5. **Generates** answers using LLM with retrieved context (RAG)

**Services:**
- **Qdrant** (port 6334): Vector database
- **LangGraph API** (port 9010): RAG agent with tools
- **LlamaIndex API** (port 9020): Direct RAG queries
- **Ingestion** (port 9030): Document processing

---

## 💡 Tips

- **Cluster access**: If tunnel fails, use `uv run langgraph dev` (without `--tunnel`) and SSH port forwarding (see `CLUSTER_ACCESS.md`)
- **Ingest before querying**: Your database starts empty - ingest documents first!
- **Use OpenAI embeddings**: Recommended - Set `EMBEDDING_PROVIDER="openai"` for fast embeddings
- **Alternative**: Use `EMBEDDING_PROVIDER="huggingface"` for free local embeddings (CPU only, slower)

---

## 🐳 Docker Commands

### Basic Commands

```bash
# Start Qdrant only
docker compose up -d qdrant

# Stop all services
docker compose down

# View logs
docker compose logs -f qdrant

# Check running containers
docker compose ps
```

### Troubleshooting & Cleanup Commands

```bash
# Remove orphan containers and clean up
docker compose down --remove-orphans

# Force remove and recreate containers
docker compose down --remove-orphans && docker compose up -d --force-recreate

# Clear Docker build cache
docker builder prune -f

# Remove unused containers, networks, images
docker system prune -f

# Check for port conflicts
lsof -i :6334
docker ps | grep -E "6334|9010|9020|9030"
```

---

**Ready to use!** Configure your `.env`, ingest documents, and start querying. 🚀
