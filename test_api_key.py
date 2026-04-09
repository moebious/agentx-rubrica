#!/usr/bin/env python3
"""Test Gemini API key connectivity."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "your_gemini_api_key_here":
    print("❌ GEMINI_API_KEY not set or still has placeholder value")
    sys.exit(1)

print(f"🔑 API Key found: {api_key[:10]}...{api_key[-4:]}")

# Test the API
try:
    import google.generativeai as genai

    genai.configure(api_key=api_key)

    # Try Gemini 2.5 Flash (latest available)
    model_name = 'models/gemini-2.5-flash'

    print(f"🧪 Testing API with {model_name}...")

    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Say 'API working!' if you can read this.")

    print(f"✅ API Response: {response.text}")
    print(f"\n🎉 Your Gemini API key is working with model: {model_name}")

    print(f"✅ API Response: {response.text}")
    print("\n🎉 Your Gemini API key is working!")

except Exception as e:
    print(f"❌ API Error: {e}")
    sys.exit(1)
