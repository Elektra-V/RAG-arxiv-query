#!/bin/bash
# Script to start LangGraph Studio for local Chrome access (no tunnel)

echo "=== Starting LangGraph Studio ==="
echo ""

# Step 1: Stop any existing processes
echo "1. Stopping any existing LangGraph processes..."
pkill -9 -f "langgraph\|cloudflared" 2>/dev/null
lsof -ti :2024 | xargs kill -9 2>/dev/null
sleep 2
echo "   ✓ Cleaned up"

# Step 2: Check port is free
echo ""
echo "2. Checking port 2024..."
if lsof -i :2024 >/dev/null 2>&1; then
    echo "   ⚠️  Port 2024 is still in use. Please check manually."
    exit 1
else
    echo "   ✓ Port 2024 is free"
fi

# Step 3: Start LangGraph dev server
echo ""
echo "3. Starting LangGraph dev server..."
echo "   (Logs will be written to /tmp/langgraph_debug.log)"
echo ""

cd "$(dirname "$0")"
# Force Chrome/Chromium for auto-open (avoid Safari)
export BROWSER="open -a 'Google Chrome' %s"
uv run langgraph dev --server-log-level debug --studio-url https://smith.langchain.com > /tmp/langgraph_debug.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo "   Waiting for server to start..."
sleep 12

# Step 4: Check if server started successfully
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "   ✓ Server started (PID: $SERVER_PID)"
else
    echo "   ❌ Server failed to start. Check /tmp/langgraph_debug.log"
    exit 1
fi

# Step 5: Get Studio URL (prefer US Studio) - compatible with macOS grep
# Try to extract the URL from logs; fallback to US URL with localhost base
STUDIO_URL=$(grep -Eo 'https://[^ ]+/studio/\?baseUrl=http://127\.0\.0\.1:2024' /tmp/langgraph_debug.log | tail -1)
if [ -z "$STUDIO_URL" ]; then
  STUDIO_URL="https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"
fi

echo ""
echo "=== Server is Ready ==="
echo ""
echo "🚀 API: http://127.0.0.1:2024"
echo "📚 API Docs: http://127.0.0.1:2024/docs"
echo "🎨 Studio UI: $STUDIO_URL"
echo ""
echo "To access Studio:"
echo "1. Open Chrome/Chromium browser"
echo "2. Navigate to: $STUDIO_URL"
echo ""
echo "To stop the server:"
echo "  pkill -f 'langgraph dev'"
echo ""
echo "To view logs:"
echo "  tail -f /tmp/langgraph_debug.log"
echo ""

