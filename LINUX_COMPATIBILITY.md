# Linux Compatibility Verification

## ✅ Verified for Linux Cluster Deployment

All code has been verified for Linux compatibility and is ready to run on your Linux cluster.

### Cross-Platform Compatibility Checks

1. **File Paths**: ✅
   - Uses `pathlib.Path` for all file operations (cross-platform)
   - No hardcoded paths (no `/Users`, `/home`, `C:`)
   - Relative paths for output files (`baseline_prompt.txt`)

2. **Environment Variables**: ✅
   - All configuration loaded from `.env` file via `pydantic-settings`
   - No OS-specific environment variable handling
   - Works with standard Linux environment variables

3. **Dependencies**: ✅
   - All dependencies are Python packages (no OS-specific binaries)
   - `agentlightning>=0.1.0` - Pure Python
   - `rich>=13.0.0` - Cross-platform terminal formatting
   - All other dependencies are standard Python packages

4. **Network Operations**: ✅
   - Uses standard `requests` library (cross-platform)
   - HTTP connections work on Linux
   - Qdrant client uses standard HTTP (works on Linux)

5. **File I/O**: ✅
   - Uses `pathlib` for file operations
   - UTF-8 encoding specified for file reads/writes
   - No Windows-specific file handling

### Environment Setup for Linux Cluster

The code expects these environment variables (in `.env` file):

```bash
# Required
OPENAI_API_KEY=sk-...                    # Your OpenAI API key
OPENAI_MODEL=gpt-4o-mini                  # Model name

# Optional but recommended
LANGSMITH_API_KEY=...                    # LangSmith/LangChain Studio key
LANGSMITH_TRACING=true                    # Enable tracing
LANGSMITH_PROJECT=rag-api-langchain      # Project name
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# Qdrant (if running locally)
QDRANT_URL=http://localhost:6334         # Or your cluster Qdrant URL
QDRANT_COLLECTION=arxiv_papers
```

### Quick Start on Linux

```bash
# 1. Clone/navigate to repo
cd rag-api

# 2. Install dependencies (uv works on Linux)
uv sync

# 3. Set up .env file
cp env.example .env
# Edit .env with your keys

# 4. Run evaluation
uv run python -m rag_api.services.langchain.train_apo
```

### Verified Components

- ✅ `rag_api/services/langchain/prompt_template.py` - Cross-platform
- ✅ `rag_api/services/langchain/apo_agent.py` - Cross-platform
- ✅ `rag_api/services/langchain/apo_dataset.py` - Cross-platform
- ✅ `rag_api/services/langchain/train_apo.py` - Cross-platform
- ✅ `rag_api/services/langchain/apo_config.py` - Cross-platform
- ✅ `rag_api/services/langchain/agent.py` - Cross-platform
- ✅ `pyproject.toml` - Standard Python packaging

### No OS-Specific Code Found

Verified that the code contains:
- ❌ No macOS-specific code
- ❌ No Windows-specific code
- ❌ No hardcoded paths
- ❌ No OS-specific imports
- ✅ Pure Python with standard libraries

### Testing Recommendations

Before running on the cluster, test locally:

1. **Verify imports**:
   ```bash
   uv run python -c "from rag_api.services.langchain.train_apo import main; print('✓ OK')"
   ```

2. **Check environment**:
   ```bash
   uv run python -c "from rag_api.settings import get_settings; s = get_settings(); print('API Key set:', bool(s.openai_api_key))"
   ```

3. **Test Qdrant connection** (if using local Qdrant):
   ```bash
   curl http://localhost:6334/collections
   ```

### Cluster-Specific Considerations

1. **Qdrant URL**: If Qdrant is on a different host, update `QDRANT_URL` in `.env`
2. **File Permissions**: Ensure write permissions for output files
3. **Network Access**: Verify cluster can reach:
   - OpenAI API (api.openai.com)
   - LangSmith (if using tracing)
   - arXiv API (export.arxiv.org)
4. **Python Version**: Requires Python >= 3.12

### Output Files

The script creates:
- `baseline_prompt.txt` - Saved in current working directory
- Console output with metrics

Both use relative paths and work on Linux.

### Success Criteria

✅ Code committed and pushed to repository
✅ All dependencies specified in `pyproject.toml`
✅ No OS-specific code
✅ Uses cross-platform libraries
✅ Environment variables from `.env` file
✅ Relative file paths
✅ Ready for Linux cluster deployment

