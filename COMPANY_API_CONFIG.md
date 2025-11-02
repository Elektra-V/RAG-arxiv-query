# Company API Configuration Guide

This project is configured to work with your company API gateway following the exact pattern from your API documentation.

## ✅ What's Already Configured

The code matches your company API pattern exactly:

```python
# Your API reference pattern:
from base64 import b64encode
from openai import OpenAI

genai_username = "my-username"
genai_password = "my-password"

token_string = f"{genai_username}:{genai_password}"
token_bytes = b64encode(token_string.encode())

client = OpenAI(
    api_key="xxxx",
    default_headers={"Authorization": f"Basic {token_bytes.decode()}"},
    base_url="https://genai.iais.fraunhofer.de/api/v2"
)
```

**Our code does exactly this** - it's in `rag_api/clients/openai.py` and runs automatically based on your `.env` file.

## 📝 Setup Steps

### 1. Create `.env` file

Copy `env.example` to `.env`:

```bash
cp env.example .env
```

### 2. Edit `.env` with your credentials

```env
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="openai"
OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
OPENAI_AUTH_USERNAME="your-actual-username"
OPENAI_AUTH_PASSWORD="your-actual-password"
OPENAI_API_KEY="xxxx"
OPENAI_MODEL="Llama-3-SauerkrautLM"  # Check available models first!
```

### 3. Check available models

```bash
uv run python check_company_models.py
```

This will:
- Connect to your company API
- List all available models
- Test the connection

### 4. Update model name

After checking available models, update `OPENAI_MODEL` in `.env` with the model you want to use.

### 5. Run the project

```bash
# Install dependencies
uv sync

# Start Qdrant (vector database)
docker compose up -d

# Ingest documents
uv run rag-api-ingest --query "topic" --max-docs 5

# Start server
uv run langgraph dev --tunnel
```

## 🔍 How It Works

1. **Basic Authentication**: The code automatically:
   - Reads `OPENAI_AUTH_USERNAME` and `OPENAI_AUTH_PASSWORD` from `.env`
   - Encodes them as Base64: `b64encode(f"{username}:{password}".encode())`
   - Adds to `default_headers`: `{"Authorization": "Basic <token>"}`

2. **Client Creation**: Creates OpenAI client with:
   - `api_key="xxxx"` (matches your pattern)
   - `base_url` from `.env`
   - `default_headers` with Basic auth

3. **LangChain Integration**: LangChain uses this client automatically - no extra configuration needed!

## 📋 Configuration Reference

### Required Settings

| Setting | Value | Example |
|---------|-------|---------|
| `LLM_PROVIDER` | `"openai"` | Required |
| `OPENAI_BASE_URL` | Your API gateway URL | `"https://genai.iais.fraunhofer.de/api/v2"` |
| `OPENAI_AUTH_USERNAME` | Your username | `"my-username"` |
| `OPENAI_AUTH_PASSWORD` | Your password | `"my-password"` |
| `OPENAI_API_KEY` | `"xxxx"` | Always `"xxxx"` (matches your pattern) |
| `OPENAI_MODEL` | Model name | `"Llama-3-SauerkrautLM"` |

### Optional Settings

- `COMPANY_API_EXTRA_HEADERS`: Per-request headers (if needed)
  - Format: `"Header-Name:value"` separated by commas
  - Example: `"X-Request-ID:default-id"`

## ⚠️ Note on `extra_headers` and `extra_body`

Your API documentation shows passing `extra_headers` and `extra_body` to individual API calls:

```python
completion = client.completions.create(
    model="Llama-3-SauerkrautLM",
    prompt="...",
    extra_headers={"X-Request-ID": "rating-00001"},
    extra_body={"guided_choice": ["positive", "negative"]}
)
```

**For LangChain usage:**
- The Basic auth header is automatically in `default_headers` ✓
- `extra_headers` can be set via `COMPANY_API_EXTRA_HEADERS` if needed
- `extra_body` is used for advanced features and can be configured in LangChain if required

For most use cases, you only need the Basic auth (which is automatic)!

## ✅ Verification

Test your configuration:

```bash
# 1. Check models
uv run python check_company_models.py

# 2. Test ingestion
uv run rag-api-ingest --query "test" --max-docs 1

# 3. Start server and test query
uv run langgraph dev --tunnel
```

If all steps work, you're ready to go! 🚀

