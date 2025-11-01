#!/bin/bash
set -e

echo "🧪 Testing Local Setup..."

# Check .env exists
if [ ! -f .env ]; then
    echo "❌ .env not found! Creating from template..."
    cp env.example .env
    echo "⚠️  Please edit .env and configure your API settings!"
    exit 1
fi

# Check Qdrant
echo "🔍 Checking Qdrant..."
if ! curl -s http://localhost:6334/ > /dev/null 2>&1; then
    echo "❌ Qdrant not running! Starting..."
    docker run -d -p 6334:6333 --name qdrant-local qdrant/qdrant || \
    docker start qdrant-local || true
    sleep 2
    if curl -s http://localhost:6334/ > /dev/null; then
        echo "✅ Qdrant started!"
    else
        echo "❌ Failed to start Qdrant"
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
echo "📥 Testing ingestion (2 papers about Python)..."
uv run rag-api-ingest --query "python programming" --max-docs 2

# Check API
echo ""
echo "📊 Checking API status..."
if curl -s http://localhost:9010/status > /dev/null 2>&1; then
    echo "✅ API is running!"
    curl -s http://localhost:9010/status | python3 -m json.tool 2>/dev/null || curl -s http://localhost:9010/status
else
    echo "ℹ️  API not running (start with: uv run langgraph dev)"
fi

echo ""
echo "✅ Test complete! See README.md for next steps."
