#!/bin/bash
echo "Setting up for ingestion-only testing (no LLM API key needed)..."

if [ -f .env ]; then
    cp .env .env.backup-$(date +%Y%m%d-%H%M%S)
fi

cp env.no-llm-test.example .env

echo "✅ Created .env for ingestion-only testing"
echo ""
echo "This configuration:"
echo "  ✅ Downloads papers from arXiv"
echo "  ✅ Creates embeddings (HuggingFace - FREE!)"
echo "  ✅ Stores in Qdrant"
echo "  ❌ Won't query LLM (but ingestion will work!)"
echo ""
echo "To test ingestion:"
echo "  1. Start Qdrant: docker run -d -p 6334:6333 qdrant/qdrant"
echo "  2. Run: uv run rag-api-ingest --query 'python' --max-docs 2"
echo ""
echo "When you get an LLM API key (Together AI/OpenRouter),"
echo "just update .env with the API settings!"
