# Quick Fix for Current Issues

## Problem 1: Port 6334 Already Allocated

**Solution**: Stop the container using port 6334

```bash
# Find what's using port 6334
docker ps | grep 6334

# Or find by container name
docker ps -a | grep qdrant

# Stop it (replace CONTAINER_ID with actual ID from above)
docker stop CONTAINER_ID

# Or stop all related containers
docker compose down
```

## Problem 2: Orphan Containers (ollama)

**Solution**: Use `--remove-orphans` flag

```bash
docker compose up --build --remove-orphans
```

## Complete Clean Start

If you want to start completely fresh:

```bash
# Stop and remove everything
docker compose down -v

# Remove orphan containers manually (if needed)
docker container prune -f

# Then start fresh
docker compose up --build --remove-orphans
```

## Quick One-Liner Fix

```bash
docker compose down && docker compose up --build --remove-orphans
```

