#!/usr/bin/env python3
"""Test OpenAI API key validity."""

import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed")
    print("Install it with: uv add openai")
    sys.exit(1)

# Load .env file if it exists
env_file = Path(".env")
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("Warning: python-dotenv not installed, using system environment variables")

# Get API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ Error: OPENAI_API_KEY not found")
    print("\nPlease set it in one of these ways:")
    print("1. Add to .env file: OPENAI_API_KEY=sk-...")
    print("2. Set environment variable: export OPENAI_API_KEY=sk-...")
    sys.exit(1)

api_key_clean = api_key.strip()

# Check format
if not api_key_clean.startswith(("sk-", "sk_proj-", "sess-")):
    print(f"⚠️  Warning: API key format looks unusual")
    print(f"   OpenAI keys typically start with 'sk-'. Got: '{api_key_clean[:10]}...'")
else:
    print(f"✓ API key format looks correct")

print(f"\n🔑 Testing API key (length: {len(api_key_clean)} characters)")

# Test the key
try:
    client = OpenAI(api_key=api_key_clean)
    
    # Try a simple API call
    print("📡 Testing connection to OpenAI API...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'OK' if you can read this"}],
        max_tokens=5,
    )
    
    print("✅ SUCCESS! API key is valid and working")
    print(f"   Response: {response.choices[0].message.content}")
    
except Exception as e:
    error_str = str(e)
    
    if "401" in error_str or "Unauthorized" in error_str or "AuthenticationError" in str(type(e)):
        print("❌ AUTHENTICATION FAILED")
        print("\nThis means:")
        print("1. API key is invalid/expired, OR")
        print("2. API key has no credits/usage remaining, OR")
        print("3. API key belongs to a different organization")
        print("\nNext steps:")
        print("1. Check your API key at: https://platform.openai.com/api-keys")
        print("2. Verify the key is active and has credits")
        print("3. Make sure you're using the correct key (check for typos)")
        print("4. Try creating a new API key")
        sys.exit(1)
    elif "429" in error_str:
        print("⚠️  Rate limit error - key is valid but rate limited")
        print("   Wait a moment and try again")
    else:
        print(f"❌ Error: {e}")
        sys.exit(1)

