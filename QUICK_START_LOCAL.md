# Quick Start - Local Testing on This Machine

Let's get this running locally first! 🚀

## What We Need

### Free Services (No Credit Card Required!):

1. **Groq API Key** (FREE, fast responses):
   - Go to: https://console.groq.com/
   - Sign up (free, no credit card)
   - Go to API Keys section
   - Create a new key
   - Copy it (starts with `gsk_`)

2. **HuggingFace Embeddings** (FREE, no API key needed!):
   - Already configured - no signup needed!
   - Just works out of the box

### Or Alternative Free Options:

- **Together AI** (also free tier): https://together.ai/
- **Local Ollama** (if you have it installed)

---

## Step-by-Step Setup

### Step 1: Get Groq API Key (2 minutes)

```bash
# 1. Open browser: https://console.groq.com/
# 2. Sign up (free, email only)
# 3. Go to API Keys → Create API Key
# 4. Copy the key (starts with gsk_...)
```

### Step 2: Configure Environment

```bash
# Backup existing .env if it has company config
cp .env .env.company-backup  # Save company config

# Use local test config
cp env.local-test.example .env

# Edit .env and add your Groq key:
# OPENAI_API_KEY="gsk_your-actual-key-here"
```

### Step 3: Install Dependencies

```bash
uv sync
```

### Step 4: Start Qdrant

**Option A: Docker** (if Docker is running):
```bash
docker run -d -p 6334:6333 --name qdrant-local qdrant/qdrant
```

**Option B: Docker Compose** (starts Qdrant only):
```bash
docker compose up -d qdrant
```

**Option C: Install Qdrant locally** (if no Docker):
```bash
# macOS
brew install qdrant
qdrant

# Or download binary from: https://github.com/qdrant/qdrant/releases
```

### Step 5: Test Ingestion

```bash
uv run rag-api-ingest run --query "machine learning" --max-docs 3
```

**Expected output:**
```
Starting ingestion for query 'machine learning' (max_docs=3)
Downloading papers...
Creating embeddings...
Ingested 3 documents into Qdrant
Ingestion completed successfully ✅
```

### Step 6: Test Query

```bash
curl -X POST http://localhost:9010/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?", "debug": true}'
```

### Step 7: Start API Service (Optional)

```bash
# In one terminal - start API
uv run rag_api/services/langchain/app.py

# In another terminal - test it
curl http://localhost:9010/status
```

---

## Quick Test Script

Save this as `test_local.sh`:

```bash
#!/bin/bash
set -e

echo "🧪 Testing Local Setup..."

# Check .env exists
if [ ! -f .env ]; then
    echo "❌ .env not found! Run: cp env.local-test.example .env"
    exit 1
fi

# Check Groq API key
if ! grep -q "gsk_" .env && ! grep -q "your-groq-api-key" .env; then
    echo "⚠️  Warning: Groq API key not set in .env"
    echo "   Get free key at: https://console.groq.com/"
fi

# Check Qdrant
if ! curl -s http://localhost:6334/ > /dev/null; then
    echo "❌ Qdrant not running! Start it with:"
    echo "   docker run -d -p 6334:6333 qdrant/qdrant"
    exit 1
fi

echo "✅ Qdrant is running"

# Install deps
echo "📦 Installing dependencies..."
uv sync

# Test ingestion
echo "📥 Testing ingestion..."
uv run rag-api-ingest run --query "python programming" --max-docs 2

# Check status
echo "📊 Checking status..."
curl -s http://localhost:9010/status | jq '.qdrant.collections' || echo "API not running - that's OK"

echo "✅ Local test complete!"
```

Run: `chmod +x test_local.sh && ./test_local.sh`

---

## What You'll See When It Works

**Ingestion:**
```
✅ Documents downloaded from arXiv
✅ Embeddings created (using HuggingFace)
✅ Stored in Qdrant
✅ Ready to query!
```

**Query:**
```json
{
  "answer": "Machine learning is...",
  "status": "success",
  "debug": {
    "tools_used": ["rag_query"],
    "execution_time_ms": 1234.56
  }
}
```

---

## Need Help?

- **No Groq API key?** → Use Together AI or local Ollama (see env.local-test.example)
- **Docker not running?** → Install Docker Desktop or use local Qdrant
- **Import errors?** → Run `uv sync` again
- **Still stuck?** → Check logs: `uv run rag-api-ingest run` (will show errors)

Once this works locally, switching to company API is just changing env vars! 🎉

