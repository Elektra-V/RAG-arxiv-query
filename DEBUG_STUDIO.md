# Debugging LangGraph Studio "Failed to fetch" Error

## Current Status

**Studio UI (EU)**: https://eu.smith.langchain.com/studio/?baseUrl=https://maintains-improvements-costumes-dark.trycloudflare.com

**API Docs**: https://maintains-improvements-costumes-dark.trycloudflare.com/docs

**Local API**: http://localhost:2024/docs

## Possible Sources of "Failed to fetch" Error

### 1. **CORS Issues**
The Studio UI (eu.smith.langchain.com) tries to fetch from the tunnel URL. Chrome might block this due to CORS.

**Check in Chrome DevTools:**
- Open Chrome DevTools (F12)
- Go to Network tab
- Try loading the Studio UI
- Look for failed requests and check the error details
- Check Console tab for CORS errors

### 2. **Tunnel Not Fully Established**
Cloudflare tunnels can take 10-30 seconds to become fully accessible.

**Solution:** Wait a minute after starting, then try again.

### 3. **DNS Propagation Delay**
The tunnel URL might not be resolvable yet.

**Test:** Try accessing the tunnel URL directly in Chrome:
```
https://maintains-improvements-costumes-dark.trycloudflare.com/docs
```

### 4. **Network/Firewall Issues**
Your network might be blocking Cloudflare tunnels.

**Check:** Can you access other trycloudflare.com URLs?

## How to Get More Logging

### Real-time Log Monitoring

```bash
# Monitor all logs in real-time
tail -f /tmp/langgraph_tunnel.log

# Or use the helper script
./monitor_logs.sh
```

### Chrome DevTools Debugging

1. **Open Chrome DevTools** (F12 or Cmd+Option+I)
2. **Go to Network tab**
3. **Reload the Studio UI page**
4. **Look for failed requests** - they'll be in red
5. **Click on failed requests** to see:
   - Request URL
   - Response status
   - Error message
   - CORS headers (if CORS issue)

### Check Specific Endpoints

```bash
# Test tunnel connectivity
curl -v "https://maintains-improvements-costumes-dark.trycloudflare.com/docs"

# Test local server
curl http://localhost:2024/docs

# Test graphs endpoint
curl http://localhost:2024/graphs | python3 -m json.tool
```

### Enable Verbose Logging

The server is already running with `--server-log-level debug`. All logs are in:
```
/tmp/langgraph_tunnel.log
```

### Common Error Patterns

1. **"Failed to fetch"** - Usually CORS or network connectivity
2. **"Network error"** - Tunnel not accessible
3. **"CORS policy"** - Cross-origin request blocked
4. **"Connection refused"** - Local server not running

## Alternative: Use API Docs Directly

If Studio UI continues to have issues, you can use the API Docs directly:

```
https://maintains-improvements-costumes-dark.trycloudflare.com/docs
```

This is a Swagger UI where you can:
- Test queries interactively
- See all available endpoints
- View request/response schemas
- Execute queries directly

## Check Current Tunnel Status

```bash
# See latest tunnel URL
head -30 /tmp/langgraph_tunnel.log | grep -E "Studio UI|API:|https://"

# Check if tunnel is registered
tail -100 /tmp/langgraph_tunnel.log | grep "Registered tunnel"
```

