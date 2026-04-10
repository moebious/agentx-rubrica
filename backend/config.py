"""Rubrica Configuration Management.

Loads and validates environment variables using pydantic-settings.
Fails fast if required configuration is missing.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger


class Settings(BaseSettings):
    """Application settings with validation.

    This will crash the application on startup if required
    environment variables are missing (fail-fast principle).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM Configuration (support both providers)
    gemini_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None

    # Model configuration
    shield_model: str = "models/gemini-2.5-flash"
    triage_model: str = "models/gemini-2.5-pro"

    # Infrastructure
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"

    # Codebase indexing / RAG
    codebase_root: Optional[str] = None

    # ITSM Integrations
    jira_domain: Optional[str] = None
    jira_user_email: Optional[str] = None
    jira_api_token: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    sendgrid_api_key: Optional[str] = None

    # Observability
    langchain_tracing_v2: bool = False
    langchain_endpoint: Optional[str] = None
    langchain_api_key: Optional[str] = None
    langchain_project: str = "rubrica-sre"
    opik_api_key: Optional[str] = None
    opik_workspace: Optional[str] = None

    # System
    debug: bool = True
    port: int = 8000


# Global settings instance (lazy loading)
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance.

    Returns:
        Validated Settings object

    Raises:
        ValidationError: If both API keys are missing
    """
    global _settings
    if _settings is None:
        _settings = Settings()

        # Validate at least one LLM provider is configured
        has_gemini = _settings.gemini_api_key and _settings.gemini_api_key != "your_gemini_api_key_here"
        has_openrouter = _settings.openrouter_api_key and _settings.openrouter_api_key != "your_openrouter_api_key_here"

        if not has_gemini and not has_openrouter:
            raise ValueError(
                "No LLM API key configured. Please set either:\n"
                "  - GEMINI_API_KEY (for direct Google AI Studio access)\n"
                "  - OPENROUTER_API_KEY (for multi-provider access)\n\n"
                "Get your key at:\n"
                "  - Google: https://aistudio.google.com/app/apikey\n"
                "  - OpenRouter: https://openrouter.ai/keys\n"
            )

        # Disable tracing if API keys are placeholders
        has_langchain_key = (
            _settings.langchain_api_key and
            _settings.langchain_api_key != "your_langsmith_key_here" and
            _settings.langchain_api_key.startswith("lsv2_")
        )
        if not has_langchain_key:
            _settings.langchain_tracing_v2 = False
            logger.info("LangSmith tracing disabled (no valid API key)")
        else:
            logger.info(f"LangSmith tracing enabled for project: {_settings.langchain_project}")

        # Check OPIK key
        has_opik_key = (
            _settings.opik_api_key and
            _settings.opik_api_key != "your_opik_key_here"
        )
        if has_opik_key:
            logger.info(f"OPIK enabled for workspace: {_settings.opik_workspace}")
        else:
            logger.info("OPIK disabled (no valid API key)")

        logger.info("Configuration loaded successfully")
        logger.info(f"Shield Model: {_settings.shield_model}")
        logger.info(f"Triage Model: {_settings.triage_model}")

    return _settings


# Convenience function for backward compatibility
def load_settings() -> Settings:
    """Load settings (alias for get_settings)."""
    return get_settings()
