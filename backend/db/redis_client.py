"""Redis client for state management."""

import redis
from loguru import logger
from backend.config import get_settings


def get_redis_client():
    """Get a Redis client instance.

    Returns:
        Redis client configured with settings
    """
    try:
        settings = get_settings()
        client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
        # Test connection
        client.ping()
        logger.info(f"Redis connected: {settings.redis_url}")
        return client
    except Exception as e:
        logger.error(f"❌ Redis connection error: {e}")
        raise
