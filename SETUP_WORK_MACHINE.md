# Setting Up on Your Work Machine

This guide helps you set up the RAG API on a new machine (like your work machine) where you might have different permissions or need to use different API keys.

## Quick Start

1. **Copy the project** to your work machine
2. **Run setup validation**:
   ```bash
   uv run python check_setup.py
   ```
3. **Copy environment template**:
   ```bash
   cp env.example .env
   ```
4. **Edit `.env`** with your work machine's configuration
5. **Install dependencies** (if needed):
   ```bash
   uv sync
   ```

## Configuration Guide

### Minimum Configuration (No API Keys Needed)

If you're using Ollama locally, you can run with minimal config:

```env
# Required
QDRANT_URL="http://localhost:6333"  # or your Qdrant instance
QDRANT_COLLECTION="arxiv_papers"

# Use local models
LLM_PROVIDER="ollama"
EMBEDDING_PROVIDER="huggingface"
OLLAMA_BASE_URL="http://localhost:11434"

# Optional - disable LangSmith if you don't have a key
LANGSMITH_TRACING=false
```

### With Cloud API Keys

When you're ready to use cloud models:

```env
# Model provider
LLM_PROVIDER="openai"  # or "anthropic"
EMBEDDING_PROVIDER="openai"

# API Keys (set these on your work machine)
OPENAI_API_KEY="your-key-here"
# OR
ANTHROPIC_API_KEY="your-key-here"

# LangSmith for debugging (optional)
LANGSMITH_API_KEY="your-key-here"
LANGSMITH_TRACING=true
```

### With Company API (Custom OpenAI-Compatible with Basic Auth)

For company APIs like Fraunhofer GenAI that use Basic authentication:

```env
# Model provider
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="openai"

# Company API configuration
OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
OPENAI_AUTH_USERNAME="my-username"
OPENAI_AUTH_PASSWORD="my-password"
OPENAI_API_KEY="xxxx"  # Can be placeholder, Basic auth handles authentication
OPENAI_MODEL="Llama-3-SauerkrautLM"  # Your company's model name
```

The code automatically:
- Encodes username:password as Base64
- Adds `Authorization: Basic <token>` header to all requests
- Uses the custom base URL instead of OpenAI's default
- Works with both LangChain and LlamaIndex services

## Important Notes

### API Key Handling

- **The code won't crash if API keys are missing** - it will:
  - Disable LangSmith tracing (with a warning)
  - Use environment variables if the SDK supports it
  - Only fail when you actually try to use a provider that needs a key

### Portable Code

- ✅ No hardcoded paths - everything uses environment variables
- ✅ Works with relative paths
- ✅ No machine-specific configurations
- ✅ Can switch between local and cloud models easily

### Testing Without Keys

You can test the basic structure even without API keys:

```bash
# Check status (will show configuration)
curl http://localhost:8009/status

# View the debug UI
# Open http://localhost:8009/ in browser
```

### Switching Between Machines

1. Keep your `.env` file **out of git** (it's in `.gitignore`)
2. Copy `env.example` as a template on each machine
3. Use different `.env` files per machine
4. All code remains the same

## Troubleshooting

### "LangSmith tracing disabled" warning

This is **normal** if you don't have a LangSmith API key. The app will still work, just without tracing. To disable the warning, set `LANGSMITH_TRACING=false` in your `.env`.

### Missing Dependencies

If `check_setup.py` shows missing packages:

```bash
# For OpenAI
uv add langchain-openai llama-index-llms-openai llama-index-embeddings-openai

# For Anthropic
uv add langchain-anthropic llama-index-llms-anthropic

# For Ollama (should already be there)
uv add langchain-ollama llama-index-llms-ollama
```

### Different Qdrant Location

If Qdrant is on a different machine or port:

```env
QDRANT_URL="http://your-qdrant-host:6333"
```

### Docker vs Local

- **Docker**: URLs like `http://qdrant:6333` (service names)
- **Local**: URLs like `http://localhost:6333`

Update your `.env` accordingly.

## Next Steps

Once setup is validated:

1. Start a service: `uv run rag_api/services/langchain/app.py`
2. Test with: `curl http://localhost:8009/status`
3. Open the UI: http://localhost:8009/
4. Check LangSmith: https://smith.langchain.com/ (if configured)

