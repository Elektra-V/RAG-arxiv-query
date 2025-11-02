# RAG API - Company API Gateway

**Retrieval Augmented Generation system for academic queries using company API gateway.**

---

## 🚀 Quick Start

### 1. Setup Configuration
```bash
cp env.example .env
```

### 2. Configure Your Company API

Edit `.env` with your credentials:

```env
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="openai"
OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
OPENAI_AUTH_USERNAME="your-username"
OPENAI_AUTH_PASSWORD="your-password"
OPENAI_API_KEY="xxxx"
OPENAI_MODEL="Llama-3-SauerkrautLM"
OPENAI_EMBEDDING_MODEL="text-embedding-3-small"
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
docker compose up -d
# OR manually: docker run -d -p 6334:6333 qdrant/qdrant

# Ingest documents (REQUIRED before querying!)
uv run rag-api-ingest --query "machine learning" --max-docs 5

# Start server with tunnel (for Safari compatibility)
uv run langgraph dev --tunnel
```

**Done!** The Studio UI URL will be displayed - use it to query your RAG system.

---

## 📋 Configuration Reference

### Required Settings

| Setting | Description | Example |
|---------|-------------|---------|
| `LLM_PROVIDER` | Provider type | `"openai"` |
| `OPENAI_BASE_URL` | Company API gateway URL | `"https://genai.iais.fraunhofer.de/api/v2"` |
| `OPENAI_AUTH_USERNAME` | Basic auth username | `"my-username"` |
| `OPENAI_AUTH_PASSWORD` | Basic auth password | `"my-password"` |
| `OPENAI_API_KEY` | API key (use `"xxxx"` as placeholder) | `"xxxx"` |
| `OPENAI_MODEL` | Model name from company API | `"Llama-3-SauerkrautLM"` |

### Optional Settings

- `EMBEDDING_PROVIDER`: `"openai"` or `"huggingface"` (free local embeddings)
- `COMPANY_API_EXTRA_HEADERS`: Per-request headers (format: `"Header-Name:value"`)

---

## 🔍 How It Works

The code automatically implements your company API pattern:

```python
# Automatically handled by rag_api/clients/openai.py:
from base64 import b64encode

token_string = f"{username}:{password}"
token_bytes = b64encode(token_string.encode())

client = OpenAI(
    api_key="xxxx",
    default_headers={"Authorization": f"Basic {token_bytes.decode()}"},
    base_url="https://genai.iais.fraunhofer.de/api/v2"
)
```

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
- Qdrant already running: `docker ps | grep qdrant`
- Or stop everything: `docker compose down`

### "langgraph: command not found"
- Run: `uv sync` first
- Then: `uv run langgraph dev --tunnel`

### CUDA compatibility error (GTX 1080 Ti or older GPUs)
- **Error**: `CUDA error: no kernel image is available for execution on the device`
- **Cause**: Older GPUs (CUDA < 7.0) incompatible with modern PyTorch
- **Solution**: The code automatically forces CPU usage for embeddings
- **Note**: CPU embeddings are slower but work reliably
- If you still see errors, ensure `EMBEDDING_PROVIDER="huggingface"` in `.env`

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
- **Use HuggingFace embeddings**: Set `EMBEDDING_PROVIDER="huggingface"` for free local embeddings (no API calls)

---

## 🐳 Docker Commands

```bash
# Start Qdrant
docker compose up -d

# Stop everything
docker compose down

# View logs
docker compose logs -f

# Clean restart
docker compose down && docker compose up --build
```

---

**Ready to use!** Configure your `.env`, ingest documents, and start querying. 🚀
