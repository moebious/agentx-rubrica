#!/usr/bin/env python3
"""Quick setup helper for OpenRouter."""

import os

print("🔑 OpenRouter Setup for Rubrica")
print("=" * 40)
print()
print("1. Get your OpenRouter API key:")
print("   → https://openrouter.ai/keys")
print()
print("2. Add it to your .env file:")
print("   OPENROUTER_API_KEY=your_key_here")
print()
print("3. Then run: ./dev.sh test-api")
print()
print("💡 Why OpenRouter?")
print("   ✅ Single API key for multiple providers")
print("   ✅ Judge can choose any model (Gemini, Claude, GPT, etc.)")
print("   ✅ No vendor lock-in")
print("   ✅ Easy to use existing credits")
print()

# Check current status
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if api_key and api_key != "your_openrouter_api_key_here":
    print("✅ OPENROUTER_API_KEY is set!")
    print(f"   Key: {api_key[:10]}...{api_key[-4:]}")
    print()
    print("Ready to test! Run: ./dev.sh test-api")
else:
    print("⚠️  OPENROUTER_API_KEY not set yet")
    print("   Please add it to your .env file")
