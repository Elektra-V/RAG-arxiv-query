# Company API Configuration Guide

**Switch from OpenRouter to your Company API Gateway - Same Structure, Just Change Values!**

---

## 🎯 Quick Setup

Your company API gateway works **exactly like OpenRouter** - it's an OpenAI-compatible API that provides access to open source models. Just update your `.env` file values!

### Current OpenRouter Setup:
```env
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="huggingface"
OPENAI_BASE_URL="https://openrouter.ai/api/v1"
OPENAI_API_KEY="sk-or-v1-..."
OPENAI_MODEL="qwen/qwen3-coder:free"
```

### Switch to Company API:
```env
LLM_PROVIDER="openai"  # Same - keeps using OpenAI-compatible client
EMBEDDING_PROVIDER="openai"  # or "huggingface" if you want free embeddings
OPENAI_BASE_URL="https://your-company-api.com/api/v2"  # Change this!
OPENAI_AUTH_USERNAME="your-username"  # Add if required
OPENAI_AUTH_PASSWORD="your-password"  # Add if required
OPENAI_API_KEY="xxxx"  # Usually "xxxx" or your actual key
OPENAI_MODEL="Llama-3-SauerkrautLM"  # Change to your company's model name
```

**That's it!** The code structure stays the same - it's designed to work with any OpenAI-compatible API gateway.

---

## 📋 Step-by-Step Configuration

### 1. Find Your Company API Details

You need these values:
- **API Gateway URL**: `https://your-company-api.com/api/v2` (or similar)
- **Authentication**: Username/password (Basic Auth) or API key
- **Available Models**: List of model names your company API provides
- **Custom Headers**: Any additional headers required (optional)

### 2. Update `.env` File

```env
# Provider settings (usually same as OpenRouter)
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="openai"  # Use "huggingface" for free local embeddings

# Company API configuration
OPENAI_BASE_URL="https://your-company-api.com/api/v2"
OPENAI_AUTH_USERNAME="your-username"
OPENAI_AUTH_PASSWORD="your-password"
OPENAI_API_KEY="xxxx"  # Usually "xxxx" placeholder

# Model names from your company API
OPENAI_MODEL="Llama-3-SauerkrautLM"  # Check available models first!
OPENAI_EMBEDDING_MODEL="text-embedding-3-small"

# Optional: Custom headers if your gateway requires them
# Format: "Header-Name:value" separated by commas
COMPANY_API_EXTRA_HEADERS="X-Custom-Header:value1,Another-Header:value2"
```

### 3. Check Available Models

Before setting `OPENAI_MODEL`, check what models are available:

```bash
uv run python check_company_models.py
```

This will:
- Connect to your company API
- List all available models
- Test the connection

### 4. Test Your Configuration

```bash
# Test connection
uv run python check_company_models.py

# If successful, you're ready!
```

---

## 🔄 Migration from OpenRouter

### Before (OpenRouter):
```env
OPENAI_BASE_URL="https://openrouter.ai/api/v1"
OPENAI_API_KEY="sk-or-v1-..."
OPENAI_MODEL="qwen/qwen3-coder:free"
OPENAI_AUTH_USERNAME=""  # Empty
OPENAI_AUTH_PASSWORD=""  # Empty
```

### After (Company API):
```env
OPENAI_BASE_URL="https://your-company-api.com/api/v2"  # Changed!
OPENAI_API_KEY="xxxx"  # Changed!
OPENAI_MODEL="Llama-3-SauerkrautLM"  # Changed!
OPENAI_AUTH_USERNAME="your-username"  # Added!
OPENAI_AUTH_PASSWORD="your-password"  # Added!
```

**Everything else stays the same!**

---

## 📝 Common Configurations

### Configuration A: Basic Auth (Most Common)
```env
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="openai"
OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
OPENAI_AUTH_USERNAME="username"
OPENAI_AUTH_PASSWORD="password"
OPENAI_API_KEY="xxxx"
OPENAI_MODEL="Llama-3-SauerkrautLM"
```

### Configuration B: API Key Only
```env
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="openai"
OPENAI_BASE_URL="https://your-company-api.com/api/v2"
OPENAI_API_KEY="your-actual-api-key"
OPENAI_MODEL="gpt-4"
# No username/password needed
```

### Configuration C: With Custom Headers
```env
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="openai"
OPENAI_BASE_URL="https://your-company-api.com/api/v2"
OPENAI_API_KEY="xxxx"
OPENAI_AUTH_USERNAME="username"
OPENAI_AUTH_PASSWORD="password"
OPENAI_MODEL="Llama-3-SauerkrautLM"
COMPANY_API_EXTRA_HEADERS="X-Request-ID:12345,X-Source:RAG-API"
```

### Configuration D: Free Embeddings (Save API Calls)
```env
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="huggingface"  # FREE - runs locally!
OPENAI_BASE_URL="https://your-company-api.com/api/v2"
OPENAI_API_KEY="xxxx"
OPENAI_AUTH_USERNAME="username"
OPENAI_AUTH_PASSWORD="password"
OPENAI_MODEL="Llama-3-SauerkrautLM"
HUGGINGFACE_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

---

## ✅ Verification Checklist

After configuring, verify:

- [ ] `.env` file has correct `OPENAI_BASE_URL`
- [ ] Authentication credentials are set (username/password or API key)
- [ ] Model name matches available models from your company API
- [ ] Run `uv run python check_company_models.py` - should list models
- [ ] Test ingestion: `uv run rag-api-ingest --query "test" --max-docs 1`
- [ ] Test query: Start server and query the RAG system

---

## 🐛 Troubleshooting

### Error: "Invalid API key"
- Check `OPENAI_API_KEY` is correct (or use "xxxx" if your API doesn't require it)
- Verify `OPENAI_AUTH_USERNAME` and `OPENAI_AUTH_PASSWORD` are set correctly

### Error: "Model not found"
- Run `uv run python check_company_models.py` to see available models
- Update `OPENAI_MODEL` with correct model name from the list

### Error: "Connection refused" or "Network error"
- Verify `OPENAI_BASE_URL` is correct
- Check if you need VPN or special network access
- Test connectivity: `curl https://your-company-api.com/api/v2/models`

### Error: "Unauthorized" or "403 Forbidden"
- Check Basic Auth credentials (username/password)
- Verify you have access to the API gateway
- Check if additional headers are required (use `COMPANY_API_EXTRA_HEADERS`)

---

## 🚀 Ready to Use!

Once configured, the workflow is exactly the same:

```bash
1. uv sync
2. docker compose up -d          # or docker run -d -p 6334:6333 qdrant/qdrant
3. uv run rag-api-ingest --query "topic" --max-docs 5
4. uv run langgraph dev --tunnel
5. Use Studio UI to query!
```

**The project is designed to work with any OpenAI-compatible API gateway - just change the `.env` values!** 🎉

