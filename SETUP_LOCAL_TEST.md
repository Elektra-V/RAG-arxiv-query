# Local Testing Setup (Free APIs - No Company Credentials)

This guide helps you test the project locally with **free services** before using company API.

## Why This Approach?

✅ **Debug locally** - See what's happening without company API issues  
✅ **Test the full pipeline** - Ingest → Query → Debug  
✅ **Once working** - Just swap env vars for company API  
✅ **No credentials needed** - Use free services first  

---

## Step 1: Choose Free Services

### Option A: Groq + HuggingFace (Recommended - Fast & Free)

**Groq**: Free LLM API (fast responses)  
**HuggingFace**: Free embeddings (no API key!)

1. **Get Groq API key** (free):
   - Go to: https://console.groq.com/
   - Sign up (free)
   - Create API key
   - Copy it

2. **Use HuggingFace embeddings** (already free, no signup needed!)

### Option B: Together AI + HuggingFace

**Together AI**: Free LLM API  
**HuggingFace**: Free embeddings

1. **Get Together AI key**:
   - Go to: https://together.ai/
   - Sign up (free tier)
   - Get API key

### Option C: Local Ollama + HuggingFace

**Ollama**: Run LLM locally (no internet needed!)  
**HuggingFace**: Free embeddings

1. **Install Ollama**:
   ```bash
   # macOS
   brew install ollama
   ollama serve
   
   # Or use Docker
   docker run -d -p 11434:11434 ollama/ollama
   ```

2. **Download model**:
   ```bash
   ollama pull llama3.1:8b
   ```

---

## Step 2: Configure Environment

```bash
# Copy the local test config
cp env.local-test.example .env

# Edit .env and add your free API key
# For Groq example:
OPENAI_BASE_URL="https://api.groq.com/openai/v1"
OPENAI_API_KEY="gsk_your-actual-groq-key"
OPENAI_MODEL="llama-3.1-70b-versatile"
EMBEDDING_PROVIDER="huggingface"  # Free!
```

**Important**: No `OPENAI_AUTH_USERNAME` or `OPENAI_AUTH_PASSWORD` needed for free services!

---

## Step 3: Test the Pipeline

### 3.1: Start Services

```bash
# Start Qdrant
docker run -d -p 6334:6333 qdrant/qdrant

# Or use Docker Compose (but update .env first)
docker compose up
```

### 3.2: Ingest Documents

```bash
uv run rag-api-ingest run --query "quantum computing" --max-docs 5
```

**Watch the logs** - you should see:
- ✅ Documents downloaded
- ✅ Embeddings created (using HuggingFace)
- ✅ Stored in Qdrant

### 3.3: Query the System

```bash
curl -X POST http://localhost:9010/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the latest developments in quantum computing?", "debug": true}'
```

### 3.4: Check Debug Info

```bash
curl http://localhost:9010/debug | jq '.'
```

Should show:
- ✅ Qdrant connected
- ✅ Collections exist with documents
- ✅ Embeddings working (HuggingFace)
- ✅ LLM configured (Groq/Together/etc)

---

## Step 4: Switch to Company API (Once Working)

Once everything works with free APIs, switch to company API:

```bash
# Update .env with company credentials
OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
OPENAI_AUTH_USERNAME="your-username"
OPENAI_AUTH_PASSWORD="your-password"
OPENAI_API_KEY="xxxx"
OPENAI_MODEL="gpt-4"  # Or whatever model is available
EMBEDDING_PROVIDER="openai"  # Switch to OpenAI embeddings
OPENAI_EMBEDDING_MODEL="text-embedding-3-small"
```

**That's it!** Just change env vars - code stays the same.

---

## Quick Start Commands

```bash
# 1. Setup
cp env.local-test.example .env
# Edit .env with your free API key

# 2. Install
uv sync

# 3. Start Qdrant
docker run -d -p 6334:6333 qdrant/qdrant

# 4. Test ingestion
uv run rag-api-ingest run --query "machine learning" --max-docs 3

# 5. Test query
curl -X POST http://localhost:9010/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}'

# 6. Debug
curl http://localhost:9010/debug | jq '.'
```

---

## Troubleshooting Free APIs

**"API key invalid"**:
- Make sure you copied the full key
- Check if free tier has limits
- Try a different free provider

**"Model not found"**:
- Check available models for your provider
- Update `OPENAI_MODEL` in `.env`

**"Rate limit exceeded"**:
- Free tiers have limits
- Wait a bit or try another provider

---

## Benefits of This Approach

1. ✅ **Works immediately** - No waiting for company API access
2. ✅ **Full debugging** - See logs, test everything locally
3. ✅ **Easy switch** - Just change env vars later
4. ✅ **Learn the flow** - Understand how everything works
5. ✅ **Identify issues** - Find problems before company deployment

Once it works locally, you know the code is correct. Then company API issues are just configuration!

