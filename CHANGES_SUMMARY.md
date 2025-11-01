# Project Changes Summary & How It Works

## 📋 Overview

This project has been **simplified and focused** on using the company LLM provider (Fraunhofer GenAI) with proper authentication following the official API documentation.

## 🔄 Key Changes Made

### 1. **Simplified Configuration** (`env.example`)
- ✅ Focused ONLY on company API configuration
- ✅ Removed confusing multiple provider options
- ✅ Clear sections with comments
- ✅ Instructions to check available models first

**Before**: Mixed configuration for Ollama, OpenAI, Anthropic, etc.  
**After**: Clean, focused company API setup

### 2. **Centralized OpenAI Client** (`rag_api/clients/openai.py`)
- ✅ **NEW FILE**: Single source of truth for authentication
- ✅ Follows EXACT pattern from company API documentation:
  ```python
  token_string = f"{username}:{password}"
  token_bytes = b64encode(token_string.encode())
  client = OpenAI(
      api_key="xxxx",
      default_headers={"Authorization": f"Basic {token_bytes.decode()}"},
      base_url="https://genai.iais.fraunhofer.de/api/v2"
  )
  ```
- ✅ All services use the same client factory
- ✅ Easy to debug - all auth logic in one place

### 3. **Model Checker Script** (`check_company_models.py`)
- ✅ **NEW FILE**: Checks what models are available on gateway
- ✅ Tests your credentials before running
- ✅ Lists all available models
- ✅ Prevents errors from using wrong model names

### 4. **Simplified Service Code**
All services now use the centralized client:
- `rag_api/services/langchain/agent.py` - Uses `get_openai_client()`
- `rag_api/services/llamaindex/index.py` - Uses `get_openai_client()`
- `rag_api/clients/embeddings.py` - Uses `get_openai_client()`

**Before**: Each service had its own auth logic (duplicated)  
**After**: One client factory, reused everywhere

### 5. **Documentation**
- ✅ `README_COMPANY_API.md` - Focused company API guide
- ✅ Simplified `README.md` with clear quick start
- ✅ `env.example` has clear comments and instructions

## 🏗️ How The Project Works Now

### Architecture Flow

```
┌─────────────────────────────────────────────────────────┐
│                    .env file                             │
│  (Credentials: username, password, base_url, model)     │
└──────────────────┬──────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              rag_api/settings.py                        │
│         (Reads from .env, provides Settings)            │
└──────────────────┬──────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│         rag_api/clients/openai.py                       │
│                                                          │
│  get_openai_client()                                    │
│    ├─ Reads credentials from settings                   │
│    ├─ Encodes username:password as Base64               │
│    ├─ Creates OpenAI client with Basic auth header      │
│    └─ Returns configured client                         │
└──────────────────┬──────────────────────────────────────┘
                    │
                    ▼
        ┌───────────┴───────────┬──────────────┐
        │                       │              │
        ▼                       ▼              ▼
┌───────────────┐   ┌──────────────┐  ┌──────────────┐
│  LangChain    │   │  LlamaIndex  │  │  Embeddings  │
│  Service      │   │  Service     │  │  Client      │
│               │   │              │  │              │
│  Uses client  │   │  Uses client │  │  Uses client │
│  from factory │   │  from factory│  │  from factory│
└───────────────┘   └──────────────┘  └──────────────┘
```

### Authentication Flow (Following Company API Pattern)

```
1. User sets credentials in .env:
   OPENAI_AUTH_USERNAME="my-username"
   OPENAI_AUTH_PASSWORD="my-password"
   OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"

2. get_openai_client() is called:
   
   a) Reads credentials from settings
   
   b) Creates token string:
      token_string = f"{username}:{password}"
   
   c) Encodes as Base64:
      token_bytes = b64encode(token_string.encode())
   
   d) Creates OpenAI client:
      client = OpenAI(
          api_key="xxxx",
          default_headers={
              "Authorization": f"Basic {token_bytes.decode()}"
          },
          base_url="https://genai.iais.fraunhofer.de/api/v2"
      )

3. Client is used by all services:
   - LangChain agent → uses client for LLM
   - LlamaIndex → uses client for LLM
   - Embeddings → uses client for embeddings
```

## 📝 Step-by-Step Usage

### Initial Setup

1. **Copy environment template**:
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` with your credentials**:
   ```env
   OPENAI_AUTH_USERNAME="your-username"
   OPENAI_AUTH_PASSWORD="your-password"
   OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
   ```

3. **Check available models** (IMPORTANT):
   ```bash
   uv run python check_company_models.py
   ```
   
   Output will show:
   ```
   ✅ Connection successful!
   📋 Available models:
   ✓ Llama-3-SauerkrautLM
   ✓ Llama-3-8B-Instruct
   ...
   ```

4. **Update model name in `.env`**:
   ```env
   OPENAI_MODEL="Llama-3-SauerkrautLM"  # Use one from the list
   ```

5. **Install dependencies**:
   ```bash
   uv sync
   ```

6. **Start service**:
   ```bash
   uv run rag_api/services/langchain/app.py
   ```

### Running the Services

**LangChain Service** (port 8009):
```bash
uv run rag_api/services/langchain/app.py
```
- Open: http://localhost:8009/
- Query endpoint: `POST /query`
- Status: `GET /status`

**LlamaIndex Service** (port 8080):
```bash
uv run rag_api/services/llamaindex/app.py
```
- Open: http://localhost:8080/
- Query endpoint: `POST /query`
- Status: `GET /status`

## 🔍 Key Files & Their Roles

### Configuration Files
- **`env.example`** - Template with company API configuration
- **`.env`** - Your actual credentials (not in git)

### Core Authentication
- **`rag_api/clients/openai.py`** - Centralized client factory
  - `create_openai_client()` - Creates client with auth
  - `get_openai_client()` - Main entry point (uses settings)

### Settings
- **`rag_api/settings.py`** - Reads from `.env`, provides Settings class

### Services (All use the same client)
- **`rag_api/services/langchain/agent.py`** - LangChain agent service
- **`rag_api/services/llamaindex/index.py`** - LlamaIndex service
- **`rag_api/clients/embeddings.py`** - Embeddings client

### Utilities
- **`check_company_models.py`** - Check available models on gateway
- **`check_setup.py`** - Validate project setup

## ✅ Benefits of This Architecture

1. **Single Source of Truth**: All auth logic in `rag_api/clients/openai.py`
2. **Easy Debugging**: Check one file to see how auth works
3. **Follows Official Pattern**: Matches company API documentation exactly
4. **No Duplication**: One client factory, reused everywhere
5. **Type Safety**: Proper typing throughout
6. **Clear Separation**: Settings → Client Factory → Services

## 🔧 Troubleshooting

**"Can't connect to API"**
- Run `check_company_models.py` to test credentials
- Verify `.env` has correct username/password
- Check `OPENAI_BASE_URL` is correct

**"Model not found"**
- Run `check_company_models.py` to see available models
- Update `OPENAI_MODEL` in `.env` with correct model name

**"Authentication fails"**
- Check `rag_api/clients/openai.py` for encoding logic
- Verify credentials in `.env`
- Check logs for specific error

## 📊 What Changed vs. Before

| Aspect | Before | After |
|--------|--------|-------|
| **Configuration** | Multiple providers, confusing | Focused on company API only |
| **Auth Logic** | Duplicated in each service | Centralized in one file |
| **Model Discovery** | Manual guesswork | Script to check available models |
| **Documentation** | Scattered across files | Clear, focused guides |
| **Debugging** | Hard to find auth issues | All auth in `openai.py` |

## 🎯 Next Steps

1. ✅ Set up `.env` with your credentials
2. ✅ Run `check_company_models.py` to verify connection
3. ✅ Update `OPENAI_MODEL` with available model
4. ✅ Start service and test
5. ✅ Use debug UI at http://localhost:8009/

---

**The project is now simplified, focused, and ready for company API usage!** 🚀

