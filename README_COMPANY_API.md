# Company API Setup Guide

This is a **simplified guide** focused only on using the company LLM provider.

## Quick Start

1. **Copy environment template**: `cp env.example .env`
2. **Edit `.env`** with your company API credentials:
   ```env
   OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
   OPENAI_AUTH_USERNAME="your-username"
   OPENAI_AUTH_PASSWORD="your-password"
   OPENAI_API_KEY="xxxx"
   ```
3. **Check available models**:
   ```bash
   uv run python check_company_models.py
   ```
4. **Update model name** in `.env` based on available models
5. **Install dependencies**: `uv sync`
6. **Start service**: `uv run rag_api/services/langchain/app.py`

## Check Available Models

Before running, **always check what models are available**:

```bash
uv run python check_company_models.py
```

This script will:
- Connect to the company API gateway
- List all available models
- Test your credentials
- Show which models you can use

**Update your `.env`** with one of the available model names:
```env
OPENAI_MODEL="Llama-3-SauerkrautLM"  # Use the model name from the list
```

## Configuration

Your `.env` file should look like this:

```env
# Company API Configuration
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="openai"

# Company API Gateway
OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
OPENAI_AUTH_USERNAME="my-username"
OPENAI_AUTH_PASSWORD="my-password"
OPENAI_API_KEY="xxxx"

# Model name (check with check_company_models.py first!)
OPENAI_MODEL="Llama-3-SauerkrautLM"

# Qdrant
QDRANT_URL="http://localhost:6333"
QDRANT_COLLECTION="arxiv_papers"
```

## How It Works

The authentication follows the **exact pattern** from company documentation:

```python
from base64 import b64encode
from openai import OpenAI

# Get credentials from .env
username = "my-username"
password = "my-password"

# Encode as Base64
token_string = f"{username}:{password}"
token_bytes = b64encode(token_string.encode())

# Create client
client = OpenAI(
    api_key="xxxx",
    default_headers={"Authorization": f"Basic {token_bytes.decode()}"},
    base_url="https://genai.iais.fraunhofer.de/api/v2"
)
```

All this is handled automatically in `rag_api/clients/openai.py`.

## Testing

1. **Test credentials and list models**:
   ```bash
   uv run python check_company_models.py
   ```

2. **Test the service**:
   ```bash
   uv run rag_api/services/langchain/app.py
   ```
   Then open: http://localhost:8009/

3. **Check status**:
   ```bash
   curl http://localhost:8009/status
   ```

## Troubleshooting

**Can't connect?**
- Check credentials in `.env`
- Verify `OPENAI_BASE_URL` is correct
- Run `check_company_models.py` to test connection

**Model not found?**
- Run `check_company_models.py` to see available models
- Update `OPENAI_MODEL` in `.env` with correct model name

**Authentication fails?**
- Check `rag_api/clients/openai.py` - all auth logic is there
- Verify username/password are correct in `.env`
- Check logs for specific error messages

