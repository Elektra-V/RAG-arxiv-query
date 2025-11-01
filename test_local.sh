#!/bin/bash
set -e

echo "🧪 Testing Local Setup..."

# Check .env exists
if [ ! -f .env ]; then
    echo "❌ .env not found! Creating from template..."
    cp env.local-test.example .env
    echo "⚠️  Please edit .env and add your Groq API key!"
    echo "   Get free key at: https://console.groq.com/"
    exit 1
fi

# Check if Groq API key is set
if grep -q "your-groq-api-key" .env || ! grep -q "gsk_" .env; then
    echo "⚠️  Warning: Groq API key not set in .env"
    echo "   Edit .env and set OPENAI_API_KEY"
    echo "   Get free key at: https://console.groq.com/"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Qdrant
echo "🔍 Checking Qdrant..."
if ! curl -s http://localhost:6334/ > /dev/null 2>&1; then
    echo "❌ Qdrant not running!"
    echo "   Starting Qdrant with Docker..."
    if command -v docker &> /dev/null; then
        docker run -d -p 6334:6333 --name qdrant-local qdrant/qdrant || \
        docker start qdrant-local || true
        sleep 2
        if curl -s http://localhost:6334/ > /dev/null; then
            echo "✅ Qdrant started!"
        else
            echo "❌ Failed to start Qdrant. Please start manually:"
            echo "   docker run -d -p 6334:6333 qdrant/qdrant"
            exit 1
        fi
    else
        echo "❌ Docker not found. Please install Docker or start Qdrant manually"
        exit 1
    fi
else
    echo "✅ Qdrant is running"
fi

# Install deps
echo "📦 Installing dependencies..."
uv sync

# Test ingestion
echo ""
echo "📥 Testing ingestion (downloading 2 papers about Python)..."
uv run rag-api-ingest --query "python programming" --max-docs 2

# Check if API is running
echo ""
echo "📊 Checking API status..."
if curl -s http://localhost:9010/status > /dev/null 2>&1; then
    echo "✅ API is running!"
    curl -s http://localhost:9010/status | python3 -m json.tool 2>/dev/null || curl -s http://localhost:9010/status
else
    echo "ℹ️  API not running (that's OK for now)"
    echo "   Start it with: uv run rag_api/services/langchain/app.py"
fi

echo ""
echo "✅ Local test setup complete!"
echo ""
echo "Next steps:"
echo "1. Test a query: curl -X POST http://localhost:9010/query -H 'Content-Type: application/json' -d '{\"question\": \"What is Python?\"}'"
echo "2. Or start API and use web UI: uv run rag_api/services/langchain/app.py"
echo "3. Then open: http://localhost:9010/docs"

