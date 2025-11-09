# Manual Start Guide for LangGraph Studio (Chrome/Chromium)

## Quick Start (Using Script)

```bash
cd /Users/vedikachauhan/project/rag-query/rag-api
./start_studio.sh
```

Then open Chrome and go to the Studio URL shown in the output.

---

## Manual Step-by-Step Commands

### Step 1: Stop Any Existing Processes

```bash
cd /Users/vedikachauhan/project/rag-query/rag-api

# Stop LangGraph and tunnel processes
pkill -9 -f "langgraph\|cloudflared"

# Free up port 2024 if needed
lsof -ti :2024 | xargs kill -9 2>/dev/null

# Wait a moment
sleep 2
```

### Step 2: Verify Port is Free (Optional)

```bash
# Check if port 2024 is free
lsof -i :2024

# Should show nothing (or "Port 2024 is free")
```

### Step 3: Start LangGraph Dev Server

```bash
cd /Users/vedikachauhan/project/rag-query/rag-api

# Start server in background with debug logging
uv run langgraph dev --server-log-level debug > /tmp/langgraph_debug.log 2>&1 &

# Wait for server to start (about 10-15 seconds)
sleep 12
```

### Step 4: Verify Server Started

```bash
# Check if server is running
ps aux | grep "langgraph dev" | grep -v grep

# Check if API is responding
curl http://127.0.0.1:2024/docs | head -3

# View startup logs
tail -30 /tmp/langgraph_debug.log | grep -E "API:|Studio UI:|Server started"
```

### Step 5: Access Studio in Chrome

1. **Open Chrome/Chromium browser** (not Safari)
2. **Navigate to:**
   ```
   https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
   ```
3. **Submit a query** - it should work without redirecting to login

---

## Monitoring and Debugging

### View Logs in Real-Time

```bash
# Follow all logs
tail -f /tmp/langgraph_debug.log

# Filter for errors only
tail -f /tmp/langgraph_debug.log | grep -E "error|Error|Exception|403|502"

# Filter for LangSmith status
tail -f /tmp/langgraph_debug.log | grep -E "LangSmith|metadata|403|204"
```

### Check Server Status

```bash
# Check if server is running
ps aux | grep "langgraph dev" | grep -v grep

# Check port usage
lsof -i :2024

# Test API endpoint
curl http://127.0.0.1:2024/docs
```

### Stop the Server

```bash
# Stop LangGraph server
pkill -f "langgraph dev"

# Or kill by port
lsof -ti :2024 | xargs kill -9
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find what's using port 2024
lsof -i :2024

# Kill it
lsof -ti :2024 | xargs kill -9
```

### Server Won't Start

```bash
# Check logs for errors
tail -50 /tmp/langgraph_debug.log | grep -E "error|Error|Exception"

# Verify .env file has correct settings
grep -E "LANGSMITH|OPENAI" .env
```

### Studio Still Redirects to Login

```bash
# Check LangSmith configuration
grep LANGSMITH .env

# Should show:
# LANGSMITH_API_KEY=lsv2_pt_...
# LANGSMITH_ENDPOINT="https://eu.api.smith.langchain.com"
# LANGSMITH_PROJECT="RAG_ARXIV"
# LANGSMITH_TRACING=false (or true)

# Check logs for 403 errors
tail -100 /tmp/langgraph_debug.log | grep "403\|Forbidden"
```

---

## Complete Command Sequence (Copy-Paste Ready)

```bash
# Navigate to project
cd /Users/vedikachauhan/project/rag-query/rag-api

# Stop existing processes
pkill -9 -f "langgraph\|cloudflared" 2>/dev/null
lsof -ti :2024 | xargs kill -9 2>/dev/null
sleep 2

# Start server
uv run langgraph dev --server-log-level debug > /tmp/langgraph_debug.log 2>&1 &

# Wait for startup
sleep 12

# Verify it's running
curl -s http://127.0.0.1:2024/docs | head -3

# Show Studio URL
echo ""
echo "🎨 Studio URL: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"
echo "📚 API Docs: http://127.0.0.1:2024/docs"
echo ""
echo "Open Chrome and navigate to the Studio URL above"
```

---

## Notes

- **No `--tunnel` flag**: We're running locally, so Chrome can access `localhost` directly
- **Chrome only**: Safari blocks localhost connections, so use Chrome/Chromium
- **Background process**: Server runs in background, logs go to `/tmp/langgraph_debug.log`
- **Auto-reload**: Server will auto-reload when you make code changes

