# LangGraph Studio Integration with Optimized Prompts

## ✅ Yes! You Can Use LangGraph Studio with Optimized Prompts

After running APO training, the optimized prompt is **automatically loaded** by both:
1. **LangGraph Studio** (via `graph.py`)
2. **API endpoints** (via `agent.py` in `routes.py`)

## How It Works

### Automatic Prompt Loading

Both `graph.py` (for LangGraph Studio) and `agent.py` (for API) automatically:

1. **Check for optimized prompt**:
   - First checks `APO_OPTIMIZED_PROMPT_PATH` from `.env` (if set)
   - Then checks `optimized_prompt.txt` in current directory
   - Finally checks `optimized_prompt.txt` in project root

2. **Load if found**:
   - If `optimized_prompt.txt` exists → uses optimized prompt
   - If not found → falls back to baseline prompt

3. **Log status**:
   - `🚀 Using OPTIMIZED prompt from APO training` (if optimized)
   - `📝 Using baseline prompt (run train_apo.py to optimize)` (if baseline)

## Workflow

### Step 1: Run APO Training

```bash
cd rag-api
uv run python -m rag_api.services.langchain.train_apo
```

This creates `optimized_prompt.txt` with the best prompt.

### Step 2: Start LangGraph Studio

```bash
uv run langgraph dev
```

**The graph automatically loads the optimized prompt!** No manual steps needed.

### Step 3: Query in Studio

1. Open LangGraph Studio in your browser
2. Enter queries as usual
3. The agent uses the **optimized prompt** automatically

### Step 4: Use API Endpoints

The API endpoints (`/query`, `/query/stream`) also use the optimized prompt automatically.

## Restart After Optimization

**Important**: After running APO training:

1. **Restart LangGraph Studio** if it's running:
   ```bash
   # Stop current instance (Ctrl+C)
   # Then restart
   uv run langgraph dev
   ```

2. **Restart API server** if running:
   ```bash
   # Stop current instance
   # Then restart
   uv run uvicorn rag_api.services.langchain.app:app --reload
   ```

The optimized prompt is loaded at **module import time**, so you need to restart to pick up the new prompt.

## Custom Prompt Path

You can specify a custom path for the optimized prompt in `.env`:

```bash
APO_OPTIMIZED_PROMPT_PATH=/path/to/my/optimized_prompt.txt
```

## Verification

### Check if Optimized Prompt is Loaded

When you start LangGraph Studio or the API, look for these log messages:

**Optimized prompt loaded:**
```
✓ Loaded optimized prompt from optimized_prompt.txt
🚀 Using OPTIMIZED prompt from APO training
```

**Baseline prompt (no optimization):**
```
📝 Using baseline prompt (run train_apo.py to optimize)
```

### Test in Studio

1. Start LangGraph Studio
2. Check the logs for prompt loading message
3. Query the agent - it will use the optimized prompt
4. Compare behavior with baseline (if you have both)

## Files Involved

- **`graph.py`**: Exports graph for LangGraph Studio (auto-loads optimized prompt)
- **`agent.py`**: Creates agent for API endpoints (auto-loads optimized prompt)
- **`optimized_prompt.txt`**: Created by `train_apo.py` after optimization

## Troubleshooting

### Optimized Prompt Not Loading

1. **Check file exists**:
   ```bash
   ls -la optimized_prompt.txt
   ```

2. **Check file location**:
   - Should be in `rag-api/` directory (where you run `langgraph dev`)
   - Or set `APO_OPTIMIZED_PROMPT_PATH` in `.env`

3. **Check logs**:
   - Look for "Loaded optimized prompt" or "Using baseline prompt" messages
   - Check for any error messages about loading

### Want to Use Baseline Again

1. **Rename optimized file**:
   ```bash
   mv optimized_prompt.txt optimized_prompt.txt.bak
   ```

2. **Restart services**:
   - Restart LangGraph Studio
   - Restart API server

3. **Or set custom path**:
   ```bash
   # In .env
   APO_OPTIMIZED_PROMPT_PATH=/path/to/baseline_prompt.txt
   ```

## Summary

✅ **Optimized prompts work automatically** with LangGraph Studio  
✅ **No manual configuration needed** - just run training and restart  
✅ **Works for both Studio and API** endpoints  
✅ **Easy to switch** between optimized and baseline prompts  

Just run `train_apo.py`, restart your services, and query as usual! 🚀

