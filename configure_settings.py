#!/usr/bin/env python3
"""
Interactive configuration helper for .env file.
Helps you set up model and API settings quickly.
"""

import os
from pathlib import Path

def main():
    env_file = Path(".env")
    env_example = Path("env.example")
    
    print("🔧 RAG API Configuration Helper")
    print("=" * 60)
    print()
    
    # Check if .env exists
    if env_file.exists():
        print(f"⚠️  {env_file} already exists!")
        response = input("   Do you want to edit it? (y/n): ").strip().lower()
        if response != 'y':
            print("   Keeping existing .env file.")
            print("   Edit it manually to change settings.")
            return
        print()
    else:
        print(f"📝 Creating new {env_file} from {env_example}...")
        if env_example.exists():
            env_file.write_text(env_example.read_text())
        else:
            print(f"❌ {env_example} not found!")
            return
        print()
    
    print("Select your configuration:")
    print()
    print("1. Company API (Production)")
    print("2. Together AI (Free tier)")
    print("3. OpenRouter (Free/Paid)")
    print("4. Ollama (Local, 100% Free)")
    print("5. Custom configuration")
    print()
    
    choice = input("Enter choice (1-5): ").strip()
    
    configs = {
        "1": {
            "name": "Company API",
            "settings": {
                "LLM_PROVIDER": "openai",
                "EMBEDDING_PROVIDER": "openai",
                "OPENAI_BASE_URL": "https://genai.iais.fraunhofer.de/api/v2",
                "OPENAI_MODEL": "gpt-4",
                "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
            },
            "prompts": {
                "OPENAI_AUTH_USERNAME": "Enter your username: ",
                "OPENAI_AUTH_PASSWORD": "Enter your password: ",
                "OPENAI_API_KEY": "Enter your API key: ",
            }
        },
        "2": {
            "name": "Together AI",
            "settings": {
                "LLM_PROVIDER": "openai",
                "EMBEDDING_PROVIDER": "huggingface",
                "OPENAI_BASE_URL": "https://api.together.xyz/v1",
                "OPENAI_MODEL": "meta-llama/Llama-3-8b-chat-hf",
                "HUGGINGFACE_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
                "OPENAI_AUTH_USERNAME": "",
                "OPENAI_AUTH_PASSWORD": "",
            },
            "prompts": {
                "OPENAI_API_KEY": "Enter your Together AI API key: ",
            }
        },
        "3": {
            "name": "OpenRouter",
            "settings": {
                "LLM_PROVIDER": "openai",
                "EMBEDDING_PROVIDER": "huggingface",
                "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
                "OPENAI_MODEL": "qwen/qwen3-coder:free",
                "HUGGINGFACE_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
                "OPENAI_AUTH_USERNAME": "",
                "OPENAI_AUTH_PASSWORD": "",
                "OPENROUTER_HTTP_REFERER": "",
                "OPENROUTER_X_TITLE": "",
            },
            "prompts": {
                "OPENAI_API_KEY": "Enter your OpenRouter API key: ",
            }
        },
        "4": {
            "name": "Ollama (Local)",
            "settings": {
                "LLM_PROVIDER": "ollama",
                "EMBEDDING_PROVIDER": "huggingface",
                "OLLAMA_MODEL": "llama3.1:8b-instruct-q4_0",
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "HUGGINGFACE_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
                "OPENAI_AUTH_USERNAME": "",
                "OPENAI_AUTH_PASSWORD": "",
            },
            "prompts": {}
        },
        "5": {
            "name": "Custom",
            "settings": {},
            "prompts": {}
        }
    }
    
    if choice not in configs:
        print("❌ Invalid choice!")
        return
    
    config = configs[choice]
    print()
    print(f"📝 Configuring: {config['name']}")
    print()
    
    # Read existing .env
    lines = env_file.read_text().splitlines()
    new_lines = []
    
    # Process each line
    for line in lines:
        stripped = line.strip()
        
        # Skip comments and empty lines initially (we'll add them back)
        if not stripped or stripped.startswith("#"):
            # Keep section headers
            if stripped.startswith("#") and ("===" in stripped or stripped.startswith("# ")):
                new_lines.append(line)
            continue
        
        # Check if this is a setting we need to update
        key = None
        if "=" in stripped:
            key = stripped.split("=")[0].strip()
        
        if key and key in config["settings"]:
            # Update with configured value
            value = config["settings"][key]
            new_lines.append(f'{key}="{value}"')
        elif key and key in config["prompts"]:
            # Prompt for value
            prompt = config["prompts"][key]
            value = input(prompt).strip()
            new_lines.append(f'{key}="{value}"')
        elif choice == "5":
            # Custom mode - show the line for reference
            print(f"   Current: {line}")
            keep = input(f"   Keep this line? (y/n/edit): ").strip().lower()
            if keep == "y":
                new_lines.append(line)
            elif keep == "edit":
                new_key = line.split("=")[0] if "=" in line else ""
                new_value = input(f"   Enter new value for {new_key}: ").strip()
                if new_key:
                    new_lines.append(f'{new_key}="{new_value}"')
        else:
            # Keep existing lines that aren't in our config
            new_lines.append(line)
    
    # Add any missing settings
    for key, value in config["settings"].items():
        if not any(key in line for line in new_lines):
            new_lines.append(f'{key}="{value}"')
    
    # Write back
    env_file.write_text("\n".join(new_lines) + "\n")
    
    print()
    print(f"✅ Configuration saved to {env_file}")
    print()
    print("📋 Summary of settings:")
    for line in new_lines:
        if "=" in line and not line.strip().startswith("#"):
            print(f"   {line}")
    print()
    print("✅ You can now run: uv sync && docker compose up")

if __name__ == "__main__":
    main()

