"""Test script for new google.genai package."""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Check if API key is set
if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "your_gemini_api_key_here":
    print("ERROR: GEMINI_API_KEY not set in .env file")
    print("Please add your API key to test the new google.genai package")
    sys.exit(1)

# Now import after checking env
from google.genai import Client
from pydantic import BaseModel
from typing import List


class TestResult(BaseModel):
    """Test result model."""
    is_safe: bool
    risk_score: int
    reasons: List[str]


async def test_genai():
    """Test the new google.genai package."""
    print("Testing new google.genai package...")

    # Create client
    api_key = os.getenv("GEMINI_API_KEY")
    client = Client(api_key=api_key)
    print(f"Client created: {type(client)}")

    # Test content generation
    prompt = "Test prompt: Is this safe?"
    print(f"\nTesting with prompt: {prompt}")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-exp",
            contents=prompt,
        )
        print(f"Response: {response.candidates[0].content.parts[0].text[:200]}")
        print("\nTest passed!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_genai())
