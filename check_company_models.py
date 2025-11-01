#!/usr/bin/env python3
"""Check available models on company API gateway.

This script connects to the company API and lists available models.
"""

import os
import sys
from base64 import b64encode

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed")
    print("Install it with: uv add openai")
    sys.exit(1)


def get_company_client() -> OpenAI:
    """Create OpenAI client configured for company API."""
    # Get credentials from environment
    username = os.getenv("OPENAI_AUTH_USERNAME")
    password = os.getenv("OPENAI_AUTH_PASSWORD")
    base_url = os.getenv("OPENAI_BASE_URL", "https://genai.iais.fraunhofer.de/api/v2")
    api_key = os.getenv("OPENAI_API_KEY", "xxxx")
    
    if not username or not password:
        print("Error: OPENAI_AUTH_USERNAME and OPENAI_AUTH_PASSWORD must be set")
        print("Set them in .env file or environment variables")
        sys.exit(1)
    
    # Encode credentials as Base64 (following company API pattern)
    token_string = f"{username}:{password}"
    token_bytes = b64encode(token_string.encode())
    
    # Create client exactly as in company documentation
    client = OpenAI(
        api_key=api_key,
        default_headers={"Authorization": f"Basic {token_bytes.decode()}"},
        base_url=base_url
    )
    
    return client


def list_models(client: OpenAI) -> None:
    """List available models on the gateway."""
    try:
        print("🔍 Connecting to company API gateway...")
        print(f"   Base URL: {client.base_url}")
        print()
        
        # Try to list models
        print("📋 Available models:")
        print("-" * 60)
        
        # Most OpenAI-compatible APIs support models.list()
        try:
            models = client.models.list()
            for model in models.data:
                print(f"  ✓ {model.id}")
            
            if not models.data:
                print("  (No models found)")
        except Exception as e:
            # If models.list() doesn't work, try a test call with a known model
            print(f"  ⚠️  Cannot list models directly: {e}")
            print()
            print("  Trying to detect available models by testing common names...")
            
            # Try common model names
            test_models = [
                "Llama-3-SauerkrautLM",
                "Llama-3-8B-Instruct",
                "Llama-3-70B-Instruct",
                "gpt-4",
                "gpt-3.5-turbo",
            ]
            
            for model_name in test_models:
                try:
                    # Try a minimal call to see if model exists
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=1,
                    )
                    print(f"  ✓ {model_name} (available)")
                except Exception as test_error:
                    # Model doesn't exist or not accessible
                    if "model" in str(test_error).lower() or "not found" in str(test_error).lower():
                        print(f"  ✗ {model_name} (not available)")
                    # Don't print other errors as they might be auth issues
            
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check your credentials in .env file")
        print("  2. Verify OPENAI_BASE_URL is correct")
        print("  3. Check network connectivity")
        sys.exit(1)


def test_connection(client: OpenAI) -> None:
    """Test connection with a simple request."""
    print("🧪 Testing connection...")
    print()
    
    # Try to get model list first (lightweight)
    try:
        models = client.models.list()
        print(f"✅ Connection successful!")
        print(f"   Found {len(models.data)} model(s)")
        return
    except:
        pass
    
    # If that fails, try a simple chat completion
    try:
        test_model = os.getenv("OPENAI_MODEL", "Llama-3-SauerkrautLM")
        print(f"   Testing with model: {test_model}")
        
        response = client.chat.completions.create(
            model=test_model,
            messages=[{"role": "user", "content": "Say 'ok' if you can read this"}],
            max_tokens=10,
        )
        
        print(f"✅ Connection successful!")
        print(f"   Model responded: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("Please check:")
        print("  1. OPENAI_AUTH_USERNAME and OPENAI_AUTH_PASSWORD in .env")
        print("  2. OPENAI_BASE_URL is correct")
        print("  3. Model name is correct")
        sys.exit(1)


def main():
    """Main function."""
    print("=" * 60)
    print("Company API Gateway - Model Checker")
    print("=" * 60)
    print()
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("⚠️  Warning: .env file not found")
        print("   Make sure to copy env.example to .env and set your credentials")
        print()
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment variables")
    
    # Create client
    client = get_company_client()
    
    # Test connection
    test_connection(client)
    print()
    
    # List models
    list_models(client)
    print()
    print("=" * 60)
    print("✅ Done! Use one of these model names in your OPENAI_MODEL setting")
    print("=" * 60)


if __name__ == "__main__":
    main()

