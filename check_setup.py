#!/usr/bin/env python3
"""Quick setup validation script for verifying configuration on a new machine."""

import os
import sys
from pathlib import Path

def check_file(filepath: str, description: str) -> bool:
    """Check if a file exists."""
    exists = Path(filepath).exists()
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {filepath}")
    return exists

def check_env_var(var: str, description: str, optional: bool = True) -> bool:
    """Check if an environment variable is set."""
    value = os.getenv(var)
    if value:
        masked = value[:8] + "..." if len(value) > 8 else "***"
        print(f"✓ {description}: Set ({masked})")
        return True
    elif optional:
        print(f"○ {description}: Not set (optional)")
        return True
    else:
        print(f"✗ {description}: Not set (required)")
        return False

def check_import(module: str, description: str) -> bool:
    """Check if a Python module can be imported."""
    try:
        __import__(module)
        print(f"✓ {description}: Available")
        return True
    except ImportError:
        print(f"✗ {description}: Not installed")
        return False

def main():
    """Run setup validation checks."""
    print("=" * 60)
    print("RAG API Setup Validation")
    print("=" * 60)
    print()
    
    issues = []
    
    # Check project structure
    print("📁 Project Structure:")
    check_file("pyproject.toml", "Project config")
    check_file("rag_api", "Main package directory")
    check_file(".env", "Environment file") or check_file("env.example", "Example env file")
    print()
    
    # Check environment variables
    print("🔑 Environment Variables:")
    print("  Required for basic operation:")
    check_env_var("QDRANT_URL", "Qdrant URL", optional=False)
    check_env_var("QDRANT_COLLECTION", "Qdrant collection", optional=False)
    print()
    print("  Model configuration (at least one LLM provider):")
    llm_provider = os.getenv("LLM_PROVIDER", "ollama")
    check_env_var("LLM_PROVIDER", "LLM provider", optional=False)
    
    if llm_provider == "openai":
        check_env_var("OPENAI_API_KEY", "OpenAI API key", optional=False)
    elif llm_provider == "anthropic":
        check_env_var("ANTHROPIC_API_KEY", "Anthropic API key", optional=False)
    elif llm_provider == "ollama":
        check_env_var("OLLAMA_BASE_URL", "Ollama URL")
    print()
    print("  Optional API keys (for enhanced features):")
    check_env_var("LANGSMITH_API_KEY", "LangSmith API key", optional=True)
    check_env_var("OPENAI_API_KEY", "OpenAI API key (if using OpenAI)", optional=True)
    check_env_var("ANTHROPIC_API_KEY", "Anthropic API key (if using Anthropic)", optional=True)
    print()
    
    # Check Python dependencies
    print("🐍 Python Dependencies:")
    essential_modules = [
        ("fastapi", "FastAPI"),
        ("langchain", "LangChain"),
        ("llama_index", "LlamaIndex"),
        ("qdrant_client", "Qdrant client"),
    ]
    
    for module, name in essential_modules:
        if not check_import(module, name):
            issues.append(f"Missing: {name}")
    
    # Check optional SDK modules based on provider
    if llm_provider == "openai":
        if not check_import("langchain_openai", "LangChain OpenAI"):
            issues.append("Missing: langchain-openai (install with: uv add langchain-openai)")
    elif llm_provider == "anthropic":
        if not check_import("langchain_anthropic", "LangChain Anthropic"):
            issues.append("Missing: langchain-anthropic (install with: uv add langchain-anthropic)")
    print()
    
    # Check services
    print("🚀 Service Files:")
    check_file("rag_api/services/langchain/app.py", "LangChain service")
    check_file("rag_api/services/llamaindex/app.py", "LlamaIndex service")
    print()
    
    # Summary
    print("=" * 60)
    if issues:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        print()
        print("Fix these issues and run this script again.")
        return 1
    else:
        print("✓ All checks passed! Your setup looks good.")
        print()
        print("Next steps:")
        print("  1. Copy env.example to .env if you haven't already")
        print("  2. Update .env with your API keys and configuration")
        print("  3. Run: uv sync (if dependencies need updating)")
        print("  4. Test: uv run python -m rag_api.services.langchain.app")
        return 0

if __name__ == "__main__":
    sys.exit(main())

