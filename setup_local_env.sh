#!/bin/bash
# Setup .env for local testing

echo "Setting up local test configuration..."

# Backup existing .env
if [ -f .env ]; then
    cp .env .env.backup-$(date +%Y%m%d-%H%M%S)
    echo "✅ Backed up existing .env"
fi

# Create .env from local test template
cat > .env << 'ENVEOF'
# ============================================================================
# LOCAL TESTING - Free APIs
# ============================================================================
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="huggingface"

# Groq (free - get key at https://console.groq.com/)
OPENAI_BASE_URL="https://api.groq.com/openai/v1"
OPENAI_API_KEY="PASTE_GROQ_KEY_HERE"
OPENAI_MODEL="llama-3.1-70b-versatile"

# HuggingFace embeddings (FREE, no key needed!)
HUGGINGFACE_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# No Basic auth for free services
OPENAI_AUTH_USERNAME=""
OPENAI_AUTH_PASSWORD=""

QDRANT_URL="http://localhost:6334"
QDRANT_COLLECTION="arxiv_papers"
ARXIV_QUERY="machine learning"
ARXIV_MAX_DOCS=3

LANGCHAIN_PORT=9010
LLAMAINDEX_PORT=9020
INGESTION_PORT=9030
LANGSMITH_TRACING=false
DUCKDUCKGO_RESULTS=3

# ============================================================================
# COMPANY API (Commented - Uncomment when ready)
# ============================================================================
# LLM_PROVIDER="openai"
# EMBEDDING_PROVIDER="openai"
# OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
# OPENAI_AUTH_USERNAME="your-username"
# OPENAI_AUTH_PASSWORD="your-password"
# OPENAI_API_KEY="xxxx"
# OPENAI_MODEL="gpt-4"
# OPENAI_EMBEDDING_MODEL="text-embedding-3-small"
ENVEOF

echo "✅ Created .env for local testing"
echo ""
echo "⚠️  IMPORTANT: Edit .env and add your Groq API key:"
echo "   1. Get free key: https://console.groq.com/"
echo "   2. Edit .env file"
echo "   3. Replace PASTE_GROQ_KEY_HERE with your actual key"
echo ""
echo "Or test ingestion first (no LLM key needed for that!):"
echo "   uv run rag-api-ingest run --query 'python' --max-docs 2"
