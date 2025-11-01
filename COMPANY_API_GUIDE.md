# Company API Integration Guide

> **📖 Main README**: For general setup, see [README.md](README.md)
> 
> This is a **detailed technical guide** for company APIs with Basic authentication.
> For quick setup, see the [Company API Configuration](README.md#company-api-configuration) section in the main README.

This guide explains how to use your company's OpenAI-compatible API with Basic authentication.

## Architecture

The authentication logic is **centralized** in `rag_api/clients/openai.py` for:
- ✅ Easy debugging (all auth logic in one place)
- ✅ Reusability across LangChain, LlamaIndex, and embeddings
- ✅ Following official company API pattern
- ✅ Keeping secrets in `.env` file

## How It Works

### 1. Configuration (`.env` file)

Put your secrets in `.env`:

```env
# Company API Configuration
OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
OPENAI_AUTH_USERNAME="my-username"
OPENAI_AUTH_PASSWORD="my-password"
OPENAI_API_KEY="xxxx"  # Placeholder is fine when using Basic auth
OPENAI_MODEL="Llama-3-SauerkrautLM"
```

### 2. Client Factory (`rag_api/clients/openai.py`)

The `get_openai_client()` function:
1. Reads credentials from settings (which reads from `.env`)
2. Encodes `username:password` as Base64: `b64encode(f"{username}:{password}".encode())`
3. Creates OpenAI client with:
   ```python
   OpenAI(
       api_key="xxxx",
       base_url="https://genai.iais.fraunhofer.de/api/v2",
       default_headers={"Authorization": f"Basic {token_bytes.decode()}"}
   )
   ```
4. Returns the configured client

This follows the **exact pattern** from your company's official API reference.

### 3. Usage Throughout Codebase

All services use the same client factory:

- **LangChain**: `rag_api/services/langchain/agent.py` → `get_openai_client()`
- **LlamaIndex LLM**: `rag_api/services/llamaindex/index.py` → `get_openai_client()`
- **LangChain Embeddings**: `rag_api/clients/embeddings.py` → `get_openai_client()`
- **LlamaIndex Embeddings**: `rag_api/services/llamaindex/index.py` → `get_openai_client()`

## Example: Direct Usage

You can also use the client directly in your code:

```python
from rag_api.clients.openai import get_openai_client

# Get configured client (reads from .env automatically)
client = get_openai_client()

# Use it exactly as in company API reference
completion = client.chat.completions.create(
    model="Llama-3-SauerkrautLM",
    messages=[{"role": "user", "content": "Hello"}],
    seed=11,
    extra_headers={"X-Request-ID": "rating-00001"},
    extra_body={"guided_choice": ["positive", "negative"]},
    stream=False
)
```

## Debugging

If authentication fails:

1. **Check `.env` file** - Are credentials set correctly?
2. **Check `rag_api/clients/openai.py`** - See the exact encoding logic
3. **Check logs** - Debug messages show when Basic auth is configured
4. **Test client directly**:
   ```python
   from rag_api.clients.openai import get_openai_client
   client = get_openai_client()
   # Try a simple call to test auth
   ```

## Security Best Practices

1. ✅ **Never commit `.env`** - It's in `.gitignore`
2. ✅ **Use different `.env` files** for different environments
3. ✅ **Keep credentials separate** - Username/password in `.env`, not in code
4. ✅ **Single source of truth** - All auth logic in `rag_api/clients/openai.py`

## File Structure

```
rag_api/
├── clients/
│   ├── openai.py          ← Centralized auth logic (Base64 encoding)
│   ├── embeddings.py      ← Uses get_openai_client()
│   └── qdrant.py
├── services/
│   ├── langchain/
│   │   └── agent.py      ← Uses get_openai_client()
│   └── llamaindex/
│       └── index.py       ← Uses get_openai_client()
└── settings.py            ← Reads from .env
```

## Why This Design?

1. **Separation of Concerns**: Auth logic separate from business logic
2. **Single Responsibility**: One module handles all OpenAI client creation
3. **Easy to Debug**: All authentication code in one place
4. **Easy to Test**: Mock `get_openai_client()` in tests
5. **Easy to Maintain**: Change auth logic once, affects everywhere
6. **Follows Official Pattern**: Matches company API reference exactly

## Next Steps

1. Set your credentials in `.env`
2. Test with: `uv run python -m rag_api.services.langchain.app`
3. Check logs to see "Configured Basic authentication" message
4. Use the debug UI at http://localhost:8009/

