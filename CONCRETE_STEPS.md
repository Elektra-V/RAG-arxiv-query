# Concrete Steps to Run APO Evaluation

## ✅ Current Status

The code has been updated to work with Agent-lightning 0.1.2 API. All imports and structure are verified.

## Step-by-Step Execution Guide

### Step 1: Verify Environment Setup

```bash
cd /Users/vedikachauhan/project/rag-query/rag-api
```

### Step 2: Install/Update Dependencies

```bash
uv sync
```

**Expected output**: Should show `agentlightning==0.1.2` and `rich>=13.0.0` installed.

### Step 3: Verify Environment Variables

Check that `.env` file exists and has:

```bash
OPENAI_API_KEY=sk-...  # Your OpenAI API key
OPENAI_MODEL=gpt-4o-mini  # or your preferred model
```

**Verify**:
```bash
# Check if .env exists
ls -la .env

# Or check if key is set (don't print the actual key)
grep -q "OPENAI_API_KEY" .env && echo "✓ API key configured" || echo "✗ API key missing"
```

### Step 4: Start Qdrant (Vector Database)

```bash
# Start Qdrant in background
docker compose up -d

# Verify it's running
docker compose ps
```

**Expected**: Qdrant should show as "Up" on port 6334.

### Step 5: (Optional) Ingest Papers for Better Evaluation

For more realistic evaluation, ingest some papers:

```bash
# Ingest machine learning papers
uv run rag-api-ingest --query "machine learning" --max-docs 10

# Ingest quantum computing papers  
uv run rag-api-ingest --query "quantum computing" --max-docs 5

# Ingest transformer papers
uv run rag-api-ingest --query "transformer architecture" --max-docs 5
```

**Note**: This step is optional but recommended for better evaluation results.

### Step 6: Test Imports (Dry Run)

Verify all code loads correctly:

```bash
uv run python -c "
from rag_api.services.langchain.train_apo import main
from rag_api.services.langchain.apo_agent import rag_agent_rollout, rag_response_grader
from rag_api.services.langchain.prompt_template import create_agentlightning_prompt_template
print('✓ All imports successful')
"
```

**Expected**: Should print "✓ All imports successful" without errors.

### Step 7: Run Evaluation Script

Execute the evaluation:

```bash
uv run python -m rag_api.services.langchain.train_apo
```

**What it does**:
1. Loads 15 training samples and 5 validation samples
2. Creates baseline prompt template
3. Evaluates each query using the agent
4. Calculates scores (tool usage, format, completeness, quality)
5. Displays metrics
6. Saves baseline prompt to `baseline_prompt.txt`

**Expected output**:
```
RAG Agent Prompt Evaluation

Note: This script evaluates prompt performance.
For full APO, integrate with Agent-lightning's LitAgent pattern.

Configuration:
  Training samples: 15
  Validation samples: 5

Loading datasets...
  Training samples: 15
  Validation samples: 5

Creating baseline prompt template...
✓ Baseline prompt created

==================================================
BASELINE EVALUATION
==================================================

Evaluating on training set...
  Task 1/15: What is quantum computing?... Score: 0.XX
  ...
```

### Step 8: Review Results

The script outputs:

1. **Training Performance**:
   - Average score (0.0 to 1.0)
   - Min score
   - Max score

2. **Validation Performance**:
   - Average score
   - Min score  
   - Max score

3. **Individual Task Scores**: Per-query evaluation

**Interpretation**:
- **0.8-1.0**: Excellent (tool usage, format, completeness all good)
- **0.6-0.8**: Good (minor issues)
- **0.4-0.6**: Needs improvement
- **0.0-0.4**: Poor (major issues)

### Step 9: Analyze Low-Scoring Tasks

Review tasks with low scores to identify patterns:

- **No tool usage**: Agent didn't call `rag_query` or `arxiv_search`
- **Format issues**: Missing TOOL_LOG structure
- **Incomplete responses**: Empty or error messages
- **Quality issues**: Missing citations or irrelevant content

### Step 10: Manual Optimization (If Needed)

Based on low-scoring tasks, refine the prompt:

1. Edit `rag_api/services/langchain/prompt_template.py`
2. Modify `get_baseline_prompt_template()` function
3. Re-run evaluation to compare

### Step 11: Use Optimized Prompt in Production

After optimization, update the agent:

```python
from pathlib import Path
from rag_api.services.langchain.agent import build_agent

# Load optimized prompt
optimized_prompt = Path("baseline_prompt.txt").read_text()

# Build agent with optimized prompt
agent = build_agent(prompt_template=optimized_prompt)
```

Or directly in code:

```python
from rag_api.services.langchain.agent import build_agent
from rag_api.services.langchain.prompt_template import get_baseline_prompt_template

# Use baseline (or your optimized version)
prompt = get_baseline_prompt_template()
agent = build_agent(prompt_template=prompt)
```

## Troubleshooting

### Error: "OPENAI_API_KEY is not set"

**Solution**:
```bash
# Check .env file exists
ls -la .env

# If missing, copy from example
cp env.example .env

# Edit .env and add your API key
# OPENAI_API_KEY=sk-...
```

### Error: "Failed to connect to Qdrant"

**Solution**:
```bash
# Start Qdrant
docker compose up -d

# Check it's running
docker compose ps

# Check logs if issues
docker compose logs qdrant
```

### Error: "RAG_EMPTY" for all queries

**Solution**: Run ingestion first:
```bash
uv run rag-api-ingest --query "machine learning" --max-docs 10
```

### Error: Import errors

**Solution**: Reinstall dependencies:
```bash
uv sync --reinstall
```

### Low Scores on All Tasks

**Possible causes**:
1. Qdrant is empty (run ingestion)
2. OpenAI API issues (check key, rate limits)
3. Network connectivity issues

**Debug**:
```bash
# Test Qdrant connection
curl http://localhost:6334/collections

# Test OpenAI API
uv run python -c "from rag_api.clients.openai import get_openai_client; client = get_openai_client(); print('✓ OpenAI client works')"
```

## Files Generated

After running, you'll have:

- `baseline_prompt.txt` - The baseline prompt for reference
- Console output with metrics

## Next Steps for Full APO

For automated prompt optimization, you would need to:

1. **Subclass LitAgent** from Agent-lightning
2. **Implement training_rollout** method
3. **Use Trainer.fit()** with the agent

See `APO_SETUP_STEPS.md` for more details on full APO integration.

## Success Criteria

✅ Script runs without errors
✅ All 15 training tasks evaluated
✅ All 5 validation tasks evaluated  
✅ Metrics displayed (average, min, max)
✅ Baseline prompt saved to file
✅ Can import and use optimized prompt in production

## Quick Test Command

To quickly verify everything works:

```bash
# One-liner to test
cd /Users/vedikachauhan/project/rag-query/rag-api && \
uv run python -c "from rag_api.services.langchain.train_apo import main; print('✓ Ready to run')" && \
echo "Run: uv run python -m rag_api.services.langchain.train_apo"
```

