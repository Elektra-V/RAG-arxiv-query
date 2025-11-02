# Accessing LangGraph Studio on Linux Cluster

Since Cloudflare tunnel may not work on cluster networks, here are alternative access methods:

## Option 1: Run Without Tunnel (If Browser is on Cluster)

```bash
# Run without tunnel flag
uv run langgraph dev

# Then access directly
# Studio: http://localhost:8123
# API Docs: http://localhost:9010/docs
```

**Note:** If you have a browser directly on the cluster (via X11 forwarding or web browser), use this method.

## Option 2: SSH Port Forwarding (Recommended for Remote Access)

If you're accessing the cluster remotely, use SSH port forwarding:

### On Your Local Machine:

```bash
# Forward LangGraph Studio port
ssh -L 8123:localhost:8123 -L 9010:localhost:9010 your-username@cluster-hostname

# Or if you're already connected via SSH, in a separate terminal run:
ssh -L 8123:localhost:8123 -L 9010:localhost:9010 your-username@cluster-hostname
```

### On the Cluster (After SSH Connection):

```bash
# Start LangGraph (without tunnel)
uv run langgraph dev

# The server will be accessible via your local machine
```

### Access from Your Local Browser:

- **LangGraph Studio**: http://localhost:8123
- **API Documentation**: http://localhost:9010/docs
- **API Endpoint**: http://localhost:9010/query

## Option 3: Direct API Access (No UI Needed)

You can query the system directly via API without Studio:

```bash
# Query via curl
curl -X POST http://localhost:9010/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is quantum computing?", "debug": true}'

# Or use the interactive API docs
# Start server: uv run langgraph dev
# Then visit: http://localhost:9010/docs
```

## Option 4: Multiple Port Forwarding (All Services)

If you need all services accessible locally:

```bash
# Forward all ports
ssh -L 6334:localhost:6334 \
    -L 9010:localhost:9010 \
    -L 9020:localhost:9020 \
    -L 9030:localhost:9030 \
    -L 8123:localhost:8123 \
    your-username@cluster-hostname
```

**Ports:**
- `8123` - LangGraph Studio
- `9010` - LangChain API
- `9020` - LlamaIndex API  
- `9030` - Ingestion API
- `6334` - Qdrant

## Troubleshooting

### "Port already in use" on local machine
```bash
# Check what's using the port
lsof -i :8123
lsof -i :9010

# Use different local ports in SSH forwarding
ssh -L 18123:localhost:8123 -L 19010:localhost:9010 ...
```

### Connection refused
- Make sure LangGraph server is running on the cluster
- Check if firewall blocks the ports
- Verify the cluster allows port forwarding

### Browser can't connect
- Make sure SSH port forwarding is active
- Try accessing `http://127.0.0.1:8123` instead of `localhost:8123`
- Check SSH connection is still alive

## Quick Start Summary

```bash
# 1. On local machine: Setup port forwarding
ssh -L 8123:localhost:8123 -L 9010:localhost:9010 user@cluster

# 2. On cluster: Start services
uv run langgraph dev  # (without --tunnel)

# 3. On local browser: Access
# Studio: http://localhost:8123
# API: http://localhost:9010/docs
```

