# How to Get Free LLM API Keys

Since you need an LLM API key for querying, here are free options:

## Option 1: Together AI (Recommended)

1. **Go to**: https://together.ai/
2. **Sign up** (free, email only)
3. **Navigate to**: API Keys section
4. **Create API key**
5. **Copy the key**
6. **Update `.env`**:
   ```env
   OPENAI_BASE_URL="https://api.together.xyz/v1"
   OPENAI_API_KEY="your-actual-key-here"
   OPENAI_MODEL="meta-llama/Llama-3-8b-chat-hf"
   ```

---

## Option 2: OpenRouter

1. **Go to**: https://openrouter.ai/
2. **Sign up** (free)
3. **Get API key**
4. **Update `.env`**:
   ```env
   OPENAI_BASE_URL="https://openrouter.ai/api/v1"
   OPENAI_API_KEY="your-key"
   OPENAI_MODEL="meta-llama/llama-3-8b-instruct"
   ```

---

## Option 3: Test WITHOUT LLM First

**No API key needed!** Just test ingestion:

1. **Use**: `env.no-llm-test.example`
   ```bash
   cp env.no-llm-test.example .env
   ```

2. **Test ingestion** (downloads papers, creates embeddings, stores in Qdrant):
   ```bash
   docker run -d -p 6334:6333 qdrant/qdrant
   uv run rag-api-ingest --query "python" --max-docs 2
   ```

3. **Verify it worked**:
   ```bash
   curl http://localhost:9010/status  # Check collections
   ```

This tests the **ingestion pipeline** without needing LLM!

Once you get an API key, just update `.env` and test querying.

---

## Quick Test Plan

```bash
# Step 1: Test ingestion (no API key needed)
cp env.no-llm-test.example .env
docker run -d -p 6334:6333 qdrant/qdrant
uv run rag-api-ingest --query "python" --max-docs 2

# Step 2: Get API key from Together AI (2 minutes)
# → https://together.ai/ → Sign up → Get key

# Step 3: Update .env with API key
# Edit .env and add your Together AI key

# Step 4: Test querying
uv run rag_api/services/langchain/app.py
curl -X POST http://localhost:9010/query ...
```

---

**Recommendation**: Start with **ingestion-only testing** to verify the pipeline works, then add LLM API key when ready!

