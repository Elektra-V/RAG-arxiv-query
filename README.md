# RAG API - Gateway with Qwen Tooling Model

**Retrieval Augmented Generation system using company API gateway with free Qwen model (full tooling support).**

## ✨ Features

- **FREE** Qwen models with full tooling/function calling support
- Gateway mode with Basic auth (no API key needed)
- Fast embeddings via gateway (no CUDA issues)
- Ready-to-use RAG pipeline with academic paper queries

---

## 🚀 Quick Start

### 1. Setup Configuration
```bash
cp env.example .env
```

### 2. Configure Gateway (Free Qwen Models)

Edit `.env` with your gateway credentials:

```env
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="openai"  # Uses gateway (fast, no CUDA issues)
OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
OPENAI_AUTH_USERNAME="your-username"
OPENAI_AUTH_PASSWORD="your-password"
OPENAI_MODEL="Qwen2.5-7B-Instruct"  # FREE Qwen with full tooling support!
# OPENAI_EMBEDDING_MODEL=""  # Leave empty for auto-detection (recommended!)
# Qwen models automatically use Qwen-compatible embeddings
# OPENAI_API_KEY=""  # Leave empty - NOT needed for gateway!
```

### 3. Check Available Models
```bash
uv run python check_company_models.py
```

This connects to your company API and lists available models. Update `OPENAI_MODEL` in `.env` with the model you want to use.

### 4. Install Dependencies & Start Services
```bash
# Install dependencies
uv sync

# Start Qdrant (vector database)
# If you see port conflicts, first run: docker compose down --remove-orphans
docker compose up -d qdrant
# OR manually: docker run -d -p 6334:6333 --name qdrant-local qdrant/qdrant

# Ingest documents (REQUIRED before querying!)
uv run rag-api-ingest --query "machine learning" --max-docs 5

# Start server with tunnel (for Safari compatibility)
uv run langgraph dev --tunnel
```

**Done!** The Studio UI URL will be displayed - use it to query your RAG system.

---

## 📋 Configuration Reference

### Required Settings - Gateway Mode (Recommended)

**Gateway mode is the primary and recommended setup - FREE Qwen models with tooling support!**

| Setting | Description | Example |
|---------|-------------|---------|
| `OPENAI_BASE_URL` | Company API gateway URL | `"https://genai.iais.fraunhofer.de/api/v2"` |
| `OPENAI_AUTH_USERNAME` | Basic auth username | `"my-username"` |
| `OPENAI_AUTH_PASSWORD` | Basic auth password | `"my-password"` |
| `OPENAI_MODEL` | **Qwen model with tooling** | `"Qwen2.5-7B-Instruct"` (default, recommended) |
| `OPENAI_EMBEDDING_MODEL` | Embedding model (auto-detected) | Leave empty for auto-detection (recommended)<br/>- Qwen models → `text-embedding-3-small`<br/>- Non-Qwen → `all-mpnet-base-v2_t2e` |
| `OPENAI_API_KEY` | **Leave empty** (not needed!) | Omit or set to `""` |

**Alternative Gateway Models:**
- `"Qwen2.5-VL-72B-Instruct"` - Larger Qwen model (auto-uses Qwen-compatible embeddings)
- `"Llama-3-SauerkrautLM"` - German-focused model (auto-uses all-mpnet-base-v2)
- `"gpt-4o-mini"` - GPT model (if available on gateway, auto-uses all-mpnet-base-v2)

**Embedding Model Auto-Detection:**
The system automatically selects the appropriate embedding model based on your LLM model:
- **Qwen models** (Qwen2.5-7B-Instruct, Qwen2.5-VL-72B-Instruct, etc.) → Use `text-embedding-3-small` (or set to `text-embedding-3-large` for higher quality)
- **Non-Qwen models** (Llama-3-SauerkrautLM, gpt-4o-mini, etc.) → Use `all-mpnet-base-v2_t2e`

**Available Gateway Embedding Models:**
- `text-embedding-3-small` - Fast, good quality (default for Qwen)
- `text-embedding-3-large` - Higher quality, slower (alternative for Qwen)
- `all-mpnet-base-v2_t2e` - Default for non-Qwen models

You can override by setting `OPENAI_EMBEDDING_MODEL`, but auto-detection is recommended for optimal compatibility.

### Optional: OpenAI Platform Mode (Advanced - Paid)

Only use if you need direct OpenAI Platform access. Gateway mode above is FREE and recommended!

| Setting | Description | Example |
|---------|-------------|---------|
| `OPENAI_BASE_URL` | OpenAI Platform URL | `"https://api.openai.com/v1"` |
| `OPENAI_API_KEY` | Your OpenAI Platform API key | `"sk-..."` |
| `OPENAI_AUTH_USERNAME` | Leave empty | Omit |
| `OPENAI_AUTH_PASSWORD` | Leave empty | Omit |

### Optional Settings

- `EMBEDDING_PROVIDER`: `"openai"` (recommended - uses company API) or `"huggingface"` (free local, CPU only, slower)
- `COMPANY_API_EXTRA_HEADERS`: Per-request headers (format: `"Header-Name:value"`)

**💡 Tip**: Use `EMBEDDING_PROVIDER="openai"` to avoid CUDA compatibility issues and get faster embeddings via your company API!

---

## 🔍 How It Works

The code automatically handles Gateway authentication (Basic auth) for free Qwen models:

```python
# Automatically handled by rag_api/clients/openai.py:
from base64 import b64encode

token_string = f"{username}:{password}"
token_bytes = b64encode(token_string.encode())

client = OpenAI(
    base_url="https://genai.iais.fraunhofer.de/api/v2",
    default_headers={"Authorization": f"Basic {token_bytes.decode()}"}
    # No api_key needed for gateway mode!
)
```

**Gateway mode (recommended):** Basic auth only - FREE Qwen models with full tooling support!  
**No code changes needed** - just set your `.env` values!

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

**Option A: LangGraph Studio (Recommended)**
```bash
uv run langgraph dev --tunnel
# Use the Studio UI URL displayed
# Interactive debugging and query interface
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
- Verify credentials in `.env` are correct
- Test connection: `uv run python check_company_models.py`
- Check if VPN or special network access is required

### "Model not found"
- List available models: `uv run python check_company_models.py`
- Update `OPENAI_MODEL` in `.env` with correct model name

### "collections": [] - Empty database
- **You must ingest documents first!**
- Run: `uv run rag-api-ingest --query "topic" --max-docs 5`

### "Port already in use"
- **Check what's using the port**: `lsof -i :6334` or `docker ps | grep qdrant`
- **Stop containers**: `docker compose down`
- **Kill specific process**: `kill -9 <PID>` (from lsof output)
- **Remove stuck containers**: `docker compose down --remove-orphans`

### "langgraph: command not found"
- Run: `uv sync` first
- Then: `uv run langgraph dev --tunnel`

### CUDA compatibility error (GTX 1080 Ti or older GPUs)
- **Error**: `CUDA error: no kernel image is available for execution on the device`
- **Cause**: Older GPUs (CUDA < 7.0) incompatible with modern PyTorch
- **Best Solution**: Use OpenAI embeddings via company API:
  ```env
  EMBEDDING_PROVIDER="openai"
  OPENAI_EMBEDDING_MODEL="text-embedding-3-small"
  ```
  This avoids CUDA entirely and is faster!
- **Alternative**: HuggingFace embeddings on CPU (automatically forced, slower but works)

### Safari blocks localhost
- Always use `--tunnel` flag: `uv run langgraph dev --tunnel`
- This creates a secure Cloudflare tunnel (HTTPS URL)

---

## 📂 Project Structure

```
rag-api/
├── .env                      # Your configuration (copy from env.example)
├── env.example               # Configuration template
├── check_company_models.py   # List available models from company API
├── check_setup.py            # Verify your setup
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
2. **Creates embeddings** (vector representations using OpenAI or HuggingFace)
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

- **Use `--tunnel` flag**: Always run `uv run langgraph dev --tunnel` for Safari compatibility
- **Check models first**: Always run `check_company_models.py` before setting `OPENAI_MODEL`
- **Ingest before querying**: Your database starts empty - ingest documents first!
- **Use OpenAI embeddings**: Recommended - Set `EMBEDDING_PROVIDER="openai"` for fast embeddings via company API (no CUDA issues!)
- **Alternative**: Use `EMBEDDING_PROVIDER="huggingface"` for free local embeddings (CPU only, slower)

---

## 🐳 Docker Commands

### Basic Commands

```bash
# Start Qdrant only (recommended for local development)
docker compose up -d qdrant

# Start all services (if using Docker for everything)
docker compose up -d

# Stop all services
docker compose down

# Stop and remove volumes (clears Qdrant data)
docker compose down -v

# View logs
docker compose logs -f
docker compose logs -f qdrant  # Specific service logs

# Check running containers
docker compose ps
docker ps | grep qdrant  # Check if Qdrant is running
```

### Troubleshooting & Cleanup Commands

```bash
# Remove orphan containers and clean up
docker compose down --remove-orphans

# Force remove and recreate containers
docker compose down --remove-orphans && docker compose up -d --force-recreate

# Clear Docker build cache (fixes stale build issues)
docker builder prune -f

# Remove unused containers, networks, images (safe cleanup)
docker system prune -f

# Full cleanup (removes everything including volumes - WARNING: deletes data!)
docker system prune -a --volumes -f

# Clean rebuild without cache (fixes build issues)
docker compose build --no-cache
docker compose up -d

# Check for port conflicts
docker ps | grep -E "6334|9010|9020|9030"
lsof -i :6334  # Check if port 6334 is in use
lsof -i :9010  # Check if port 9010 is in use

# Remove specific container if stuck
docker rm -f $(docker ps -aq --filter "name=qdrant")
docker rm -f $(docker ps -aq --filter "name=rag-api")
```

### Common Problem Fixes

**Problem: Port already in use**
```bash
# Find what's using the port
lsof -i :6334
# Kill the process or stop the container
docker compose down
# Or kill specific process: kill -9 <PID>
```

**Problem: Stale containers/orphans**
```bash
# Remove orphans and restart
docker compose down --remove-orphans
docker compose up -d
```

**Problem: Build cache issues**
```bash
# Clean rebuild
docker compose build --no-cache --pull
docker compose up -d
```

**Problem: Volume/data conflicts**
```bash
# Reset Qdrant data (careful: deletes all stored documents!)
docker compose down -v
docker volume rm rag-api_qdrant_data  # If volume exists
docker compose up -d
```

**Problem: Container won't start**
```bash
# Check logs for errors
docker compose logs qdrant
# Restart specific service
docker compose restart qdrant
# Force recreate
docker compose up -d --force-recreate qdrant
```

### Quick Reference

| Command | Purpose |
|---------|---------|
| `docker compose up -d qdrant` | Start Qdrant only |
| `docker compose down --remove-orphans` | Clean shutdown |
| `docker compose build --no-cache` | Rebuild without cache |
| `docker system prune -f` | Clean unused resources |
| `docker compose logs -f qdrant` | View Qdrant logs |
| `docker compose ps` | Check running services |

---

**Ready to use!** Configure your `.env`, ingest documents, and start querying. 🚀
