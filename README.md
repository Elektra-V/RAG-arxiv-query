# RAG API - Quick Start Guide

**One README. Everything you need to run this project.**

---

## 🚀 Setup (5 Minutes)

### Step 1: Copy Configuration File
```bash
cp env.example .env
```

### Step 2: Edit `.env` File
Open `.env` and replace these lines with your actual credentials:

```env
OPENAI_BASE_URL="https://genai.iais.fraunhofer.de/api/v2"
OPENAI_AUTH_USERNAME="your-actual-username"
OPENAI_AUTH_PASSWORD="your-actual-password"
OPENAI_API_KEY="xxxx"
OPENAI_MODEL="Llama-3-SauerkrautLM"
```

**Important**: Use your real username and password from your company.

### Step 3: Check Available Models
```bash
uv run python check_company_models.py
```

This will show you which models are available. Update `OPENAI_MODEL` in `.env` if needed.

### Step 4: Install Dependencies
```bash
uv sync
```

### Step 5: Start the Service
```bash
uv run rag_api/services/langchain/app.py
```

### Step 6: Open Browser
Go to: **http://localhost:8009/**

You should see the debug interface where you can ask questions!

---

## 📝 Quick Reference

**Check models available**: `uv run python check_company_models.py`

**Start LangChain service**: `uv run rag_api/services/langchain/app.py`

**Start LlamaIndex service**: `uv run rag_api/services/llamaindex/app.py`

**Check service status**: `curl http://localhost:8009/status`

**Web UI**: http://localhost:8009/ (LangChain) or http://localhost:8080/ (LlamaIndex)

---

## 🔧 Troubleshooting

**"Connection failed"**
- Run `check_company_models.py` to test your credentials
- Make sure username and password in `.env` are correct

**"Model not found"**
- Run `check_company_models.py` to see available models
- Update `OPENAI_MODEL` in `.env` with one from the list

**"Service won't start"**
- Make sure `.env` file exists
- Check that you ran `uv sync`
- Look at the error message in terminal

---

## 📂 What This Project Does

- **LangChain Service** (port 8009): Agent with RAG + web search
- **LlamaIndex Service** (port 8080): Direct RAG queries
- Both connect to your company's LLM API
- Both use Qdrant for document storage

---

## 🎯 That's It!

Follow the 6 steps above. If something breaks, check the Troubleshooting section.

**Need help?** Check the terminal output - error messages will tell you what's wrong.
