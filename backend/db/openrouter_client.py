"""OpenRouter LLM client for flexible model access.

This module provides a unified interface to multiple LLM providers
through OpenRouter, making it easier for judges to run the code with
their preferred models and existing credits.
"""

import os
from typing import Optional
from loguru import logger
from openai import OpenAI

from backend.config import settings


# ============================================================================
# OPENROUTER CLIENT
# ============================================================================

def get_openrouter_client() -> OpenAI:
    """Get an OpenRouter client instance.

    OpenRouter provides unified access to multiple LLM providers:
    - Google (Gemini 2.5, etc.)
    - Anthropic (Claude 3.5, etc.)
    - OpenAI (GPT-4o, etc.)
    - And many more

    Returns:
        OpenAI client configured for OpenRouter
    """
    api_key = settings.openrouter_api_key

    if not api_key or api_key == "your_openrouter_api_key_here":
        raise ValueError(
            "OPENROUTER_API_KEY not set. Please set it in your .env file.\n"
            "Get your key at: https://openrouter.ai/keys"
        )

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    logger.info(f"OpenRouter client initialized")
    return client


def get_model_name(model_type: str = "shield") -> str:
    """Get the model name for a specific use case.

    Args:
        model_type: Type of model ("shield" or "triage")

    Returns:
        Model name for OpenRouter
    """
    # Check environment variables first
    shield_model = os.getenv("SHIELD_MODEL")
    triage_model = os.getenv("TRIAGE_MODEL")

    # Default models (optimized for cost/speed)
    defaults = {
        "shield": shield_model or "google/gemini-2.5-flash-exp",
        "triage": triage_model or "google/gemini-2.5-pro-exp",
    }

    model = defaults.get(model_type, defaults["shield"])
    logger.info(f"Using model: {model} for {model_type}")

    return model


# ============================================================================
# MODEL RECOMMENDATIONS
# ============================================================================

RECOMMENDED_MODELS = {
    "shield": [
        "google/gemini-2.5-flash-exp",  # Fast, cost-effective
        "anthropic/claude-3.5-haiku",     # Very fast
        "openai/gpt-4o-mini",             # Fast and cheap
    ],
    "triage": [
        "google/gemini-2.5-pro-exp",     # Deep reasoning
        "anthropic/claude-3.5-sonnet",    # Excellent reasoning
        "openai/gpt-4o",                  # Strong all-around
    ],
}


def list_available_models() -> dict:
    """Return available model recommendations.

    Returns:
        Dictionary of recommended models by use case
    """
    return RECOMMENDED_MODELS
