"""Qdrant client for vector search."""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from loguru import logger
from backend.config import get_settings


def get_qdrant_client():
    """Get a Qdrant client instance.

    Returns:
        QdrantClient configured with settings

    Note:
        This should not require LLM credentials. It's safe to use even when
        running offline indexing / diagnostics.
    """
    try:
        settings = get_settings()
        qdrant_url = settings.qdrant_url
    except Exception:
        # Allow Qdrant access even if Settings validation fails (e.g. missing LLM keys)
        import os

        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")

    try:
        client = QdrantClient(url=qdrant_url)
        collections = client.get_collections()
        logger.info(f"Qdrant connected: {qdrant_url}")
        logger.info(f"Existing collections: {[c.name for c in collections.collections]}")
        return client
    except Exception as e:
        logger.error(f"❌ Qdrant connection error: {e}")
        raise


def reset_collection(client: QdrantClient, collection_name: str = "codebase") -> None:
    """Drop and recreate a collection for reproducible indexing."""
    try:
        client.delete_collection(collection_name=collection_name)
        logger.info(f"Deleted collection '{collection_name}'")
    except Exception:
        # Collection may not exist; ignore
        pass

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
    logger.info(f"Created collection '{collection_name}'")


def ensure_codebase_collection(client: QdrantClient, collection_name: str = "codebase") -> str:
    """Ensure the codebase collection exists.

    Args:
        client: Qdrant client
        collection_name: Name of the collection

    Returns:
        Collection name
    """
    try:
        # Check if collection exists
        collections = client.get_collections()
        existing = [c.name for c in collections.collections]

        if collection_name in existing:
            logger.info(f"📁 Collection '{collection_name}' already exists")
            return collection_name

        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
        logger.info(f"Created collection '{collection_name}'")
        return collection_name

    except Exception as e:
        logger.error(f"❌ Error creating collection: {e}")
        raise
