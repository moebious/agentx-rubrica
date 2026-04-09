"""Flexible LLM client supporting multiple providers.

This module provides a unified interface that works with:
- Direct Google AI Studio (Gemini) - Your current setup
- OpenRouter (multi-provider access) - For judges' flexibility

Judge can use whichever API key they have available.
"""

import os
from typing import Literal
from loguru import logger
from openai import OpenAI
import instructor
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment once at module import
load_dotenv()

from backend.config import get_settings


# ============================================================================
# LLM PROVIDER CONFIGURATION
# ============================================================================

LLMProvider = Literal["google", "openrouter"]


def get_provider() -> LLMProvider:
    """Detect which LLM provider to use.

    Priority:
    1. OpenRouter (if key is set) - for judge flexibility
    2. Google (if key is set) - your current setup

    Returns:
        The detected provider
    """
    # Load from environment directly
    load_dotenv()

    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    # Check if OpenRouter key is configured and not placeholder
    if openrouter_key and openrouter_key != "your_openrouter_api_key_here" and openrouter_key != "":
        logger.info("🌐 Using OpenRouter provider")
        return "openrouter"

    # Check if Gemini key is configured (your current setup)
    if gemini_key and gemini_key.startswith("AIza"):
        logger.info("🔧 Using Google Gemini provider")
        return "google"

    raise ValueError(
        "No LLM API key configured. Please set either:\n"
        "  - GEMINI_API_KEY (for direct Google AI Studio access)\n"
        "  - OPENROUTER_API_KEY (for multi-provider access)\n\n"
        "Get your key at: https://aistudio.google.com/app/apikey or https://openrouter.ai/keys"
    )


def get_model_name(model_type: str = "shield") -> str:
    """Get the model name for a specific use case.

    Args:
        model_type: "shield" or "triage"

    Returns:
        Model name (compatible with chosen provider)
    """
    # Load from environment
    load_dotenv()

    shield_model = os.getenv("SHIELD_MODEL", "google/gemini-2.5-flash-exp")
    triage_model = os.getenv("TRIAGE_MODEL", "google/gemini-2.5-pro-exp")

    defaults = {
        "shield": shield_model,
        "triage": triage_model,
    }

    return defaults.get(model_type, defaults["shield"])


# ============================================================================
# CLIENT FACTORIES
# ============================================================================

def get_openai_client() -> OpenAI:
    """Get OpenAI-compatible client (works with OpenRouter).

    Returns:
        OpenAI client configured for the chosen provider
    """
    provider = get_provider()

    if provider == "openrouter":
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
    else:
        # For Gemini, we use a different client (see below)
        raise NotImplementedError("Use get_gemini_client() for Google provider")


def get_gemini_client():
    """Get Gemini client for direct Google AI Studio access.

    Returns:
        Configured Gemini generativeai instance
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    return genai


def get_instructor_client(model_type: str = "shield"):
    """Get Instructor client for structured outputs.

    Automatically detects provider and returns appropriate client.

    Args:
        model_type: Type of model ("shield" or "triage")

    Returns:
        Instructor client ready for use
    """
    provider = get_provider()
    model = get_model_name(model_type)

    if provider == "openrouter":
        # Use OpenAI-compatible client with Instructor
        client = get_openai_client()
        return instructor.from_openai(client, model=model)

    else:  # google
        # Use Gemini directly with Instructor
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        return instructor.from_gemini(
            genai,
            model=model.replace("google/", ""),  # Remove prefix for Gemini
        )


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def validate_with_llm(messages, response_model):
    """Convenience function for LLM validation.

    Args:
        messages: Chat messages
        response_model: Pydantic model for structured output

    Returns:
        Structured response from LLM
    """
    client = get_instructor_client("shield")
    return client.messages.create(
        messages=messages,
        response_model=response_model,
    )
