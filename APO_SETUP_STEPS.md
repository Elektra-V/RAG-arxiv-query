# APO Integration - Setup and Testing Steps

## Current Status

The APO integration has been adapted to work with Agent-lightning 0.1.2. Since the API differs from initial assumptions, the current implementation provides:

1. **Standalone evaluation framework** - Evaluates prompt performance
2. **Rollout function** - Executes agent with given prompts
3. **Grader function** - Scores agent responses
4. **Dataset management** - Training and validation datasets

## Concrete Steps to Run and Test

### Step 1: Verify Dependencies

```bash
cd rag-api
uv sync
```

This should install:
- `agentlightning==0.1.2`
- `rich>=13.0.0`
- All other dependencies

### Step 2: Verify Environment Setup

Ensure your `.env` file has:
```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini  # or your preferred model
```

### Step 3: Start Qdrant (Vector Database)

```bash
docker compose up -d
```

Or if already running:
```bash
docker compose ps
```

### Step 4: Ingest Some Papers (Optional but Recommended)

For better evaluation results, ingest some papers:

```bash
uv run rag-api-ingest --query "machine learning" --max-docs 10
uv run rag-api-ingest --query "quantum computing" --max-docs 5
```

### Step 5: Test Imports

Verify all modules load correctly:

```bash
uv run python -c "from rag_api.services.langchain.train_apo import main; print('✓ All imports successful')"
```

### Step 6: Run Evaluation Script

Run the prompt evaluation:

```bash
uv run python -m rag_api.services.langchain.train_apo
```

This will:
- Load training and validation datasets
- Evaluate baseline prompt performance
- Display metrics (average, min, max scores)
- Save baseline prompt to `baseline_prompt.txt`

### Step 7: Review Results

The script outputs:
- **Training set performance**: Average score across training queries
- **Validation set performance**: Average score across validation queries
- **Individual task scores**: Per-query evaluation

### Step 8: Manual Optimization (Current Approach)

Since full automated APO requires Agent-lightning's `LitAgent` pattern:

1. Review low-scoring tasks from the evaluation
2. Identify common failure patterns
3. Manually refine the prompt in `rag_api/services/langchain/prompt_template.py`
4. Re-run evaluation to compare

### Step 9: Use Optimized Prompt in Production

After optimization:

```python
from pathlib import Path
from rag_api.services.langchain.agent import build_agent

# Load optimized prompt
optimized_prompt = Path("baseline_prompt.txt").read_text()

# Build agent with optimized prompt
agent = build_agent(prompt_template=optimized_prompt)
```

## Troubleshooting

### Import Errors

If you see `ImportError: cannot import name 'APO'`:
- This is expected - Agent-lightning 0.1.2 doesn't have a standalone APO class
- The current implementation uses standalone evaluation

### OpenAI API Errors

If you see API errors:
- Verify `OPENAI_API_KEY` is set in `.env`
- Check API rate limits
- Ensure model name is correct

### Qdrant Connection Errors

If RAG queries fail:
- Ensure Qdrant is running: `docker compose ps`
- Start Qdrant: `docker compose up -d`
- Verify connection: Check `QDRANT_URL` in `.env` (default: `http://localhost:6334`)

### Empty RAG Results

If `rag_query` always returns empty:
- Run ingestion: `uv run rag-api-ingest --query "topic" --max-docs 5`
- Check Qdrant collection exists
- Verify embeddings are working

## Next Steps for Full APO

To implement full automated prompt optimization with Agent-lightning:

1. **Subclass LitAgent**:
   ```python
   from agentlightning import LitAgent
   
   class RAGAgent(LitAgent):
       def training_rollout(self, task, rollout_id, resources):
           # Implement rollout logic
           pass
   ```

2. **Use Trainer**:
   ```python
   from agentlightning import Trainer
   
   agent = RAGAgent()
   trainer = Trainer(n_workers=4)
   trainer.fit(agent, backend="local")
   ```

3. **Integrate with existing rollout function**: Adapt `rag_agent_rollout` to work within `LitAgent.training_rollout`

## Files Created/Modified

- ✅ `rag_api/services/langchain/prompt_template.py` - Prompt extraction
- ✅ `rag_api/services/langchain/apo_agent.py` - Rollout and grader
- ✅ `rag_api/services/langchain/apo_dataset.py` - Training datasets
- ✅ `rag_api/services/langchain/train_apo.py` - Evaluation script
- ✅ `rag_api/services/langchain/apo_config.py` - Configuration
- ✅ `rag_api/services/langchain/agent.py` - Updated to accept prompts
- ✅ `pyproject.toml` - Added dependencies
- ✅ `README.md` - Added APO documentation

## Success Criteria

✅ Script runs without import errors
✅ Baseline evaluation completes
✅ Metrics are displayed
✅ Prompt is saved to file
✅ Can load optimized prompt in production

