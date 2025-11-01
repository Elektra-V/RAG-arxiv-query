# Plug-and-Play Setup Checklist

## ✅ Verified Working Components

### Environment
- ✅ `uv` package manager installed
- ✅ Docker installed and running
- ✅ Python 3.12+ available

### Configuration
- ✅ `.env` file with OpenRouter credentials
- ✅ Model: `google/gemini-2.5-flash-preview-09-2025`
- ✅ Embeddings: HuggingFace (free, no API key needed)

### Services
- ✅ Qdrant: Running on port 6334
- ✅ Ingestion: Working (6 documents stored)
- ✅ RAG Retrieval: Functional
- ✅ LangGraph Dev: Running with `--tunnel` flag

## 📋 For New Machine Setup

### Step 1: Clone/Copy Project
```bash
git clone <repo-url>
cd rag-api
```

### Step 2: Configure Environment
```bash
cp env.example .env
# Edit .env with your OpenRouter API key
```

### Step 3: Install Dependencies
```bash
uv sync
```

### Step 4: Start Qdrant
```bash
docker run -d -p 6334:6333 --name qdrant-local qdrant/qdrant
```

### Step 5: Ingest Documents
```bash
uv run rag-api-ingest --query "machine learning" --max-docs 5
```

### Step 6: Start Server
```bash
uv run langgraph dev --tunnel
```

### Step 7: Access Studio UI
- Copy the Studio UI URL from terminal output
- Format: `https://smith.langchain.com/studio/?baseUrl=<TUNNEL_URL>`
- Open in Safari (or any browser)

## 🐛 Known Issues & Solutions

### Port Already in Use
- Solution: `pkill -f langgraph` then restart

### Qdrant Not Accessible
- Solution: Check if Docker is running: `docker ps`
- Restart Qdrant: `docker start qdrant-local`

### Tool Calling Errors
- Solution: Ensure model supports tool calling
- Current: `google/gemini-2.5-flash-preview-09-2025` should work
- Alternative: `openai/gpt-4o-mini` (confirmed working)

## ✅ Test Results

- ✅ Ingestion: 6 documents stored
- ✅ Retrieval: Working (found relevant results)
- ✅ Server: Running with tunnel
- ✅ Configuration: All settings verified

