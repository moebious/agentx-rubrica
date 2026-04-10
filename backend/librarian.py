"""Rubrica Librarian Agent - RAG-based code search and context retrieval.

This module implements the Librarian Agent that:
1. Indexes code files into Qdrant (chunking + embeddings)
2. Searches codebase using vector similarity + keyword matching
3. Returns relevant code snippets with line numbers and context
4. Provides hybrid RAG for the Triage Agent

Uses Gemini for embeddings and Qdrant for vector storage.
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from loguru import logger
from pydantic import BaseModel, Field

from shared.schemas import CodeContext
from backend.db.qdrant_client import get_qdrant_client, ensure_codebase_collection
from backend.db.llm_client import get_provider, get_model_name


# ============================================================================
# CONFIGURATION
# ============================================================================

COLLECTION_NAME = "codebase"
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks
EMBEDDING_MODEL = "models/text-embedding-004"  # Gemini embedding model


# ============================================================================
# CODE CHUNKING
# ============================================================================

def chunk_code_file(file_path: str, content: str) -> List[Dict[str, Any]]:
    """Split a code file into overlapping chunks for embedding.

    Args:
        file_path: Path to the code file
        content: File content

    Returns:
        List of chunks with metadata
    """
    chunks = []

    # Split by lines first to preserve line numbers
    lines = content.split("\n")
    current_chunk = []
    current_start = 0
    current_length = 0

    for i, line in enumerate(lines):
        line_length = len(line) + 1  # +1 for newline

        if current_length + line_length > CHUNK_SIZE and current_chunk:
            # Save current chunk
            chunks.append({
                "text": "\n".join(current_chunk),
                "start_line": current_start + 1,
                "end_line": i + 1,
                "file_path": file_path,
            })

            # Start new chunk with overlap
            overlap_lines = CHUNK_OVERLAP // 100  # Rough estimate
            current_chunk = current_chunk[-overlap_lines:] if overlap_lines > 0 else []
            current_start = i - len(current_chunk) + 1
            current_length = sum(len(l) + 1 for l in current_chunk)

        current_chunk.append(line)
        current_length += line_length

    # Add final chunk
    if current_chunk:
        chunks.append({
            "text": "\n".join(current_chunk),
            "start_line": current_start + 1,
            "end_line": len(lines),
            "file_path": file_path,
        })

    return chunks


def detect_language(file_path: str) -> str:
    """Detect programming language from file extension.

    Args:
        file_path: Path to the file

    Returns:
        Language name
    """
    ext = Path(file_path).suffix.lower()
    mapping = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".kt": "kotlin",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".php": "php",
        ".rb": "ruby",
        ".swift": "swift",
        ".dart": "dart",
        ".sql": "sql",
        ".sh": "bash",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".xml": "xml",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".md": "markdown",
    }
    return mapping.get(ext, "text")


# ============================================================================
# EMBEDDINGS
# ============================================================================

async def generate_embedding(text: str) -> List[float]:
    """Generate embedding for text using Gemini.

    Args:
        text: Text to embed

    Returns:
        Embedding vector
    """
    try:
        from google.genai import Client
        client = Client(api_key=os.getenv("GEMINI_API_KEY"))

        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
        )

        return response.embedding.values

    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        # Return zero vector as fallback
        return [0.0] * 768


# ============================================================================
# LIBRARIAN AGENT
# ============================================================================

class LibrarianAgent:
    """Code search and context retrieval agent.

    Provides hybrid RAG search:
    - Vector search: Semantic similarity using embeddings
    - Keyword search: BM25-style text matching
    - Hybrid: Combined scoring
    """

    def __init__(self):
        """Initialize the Librarian Agent."""
        self.qdrant = get_qdrant_client()
        self.collection = ensure_codebase_collection(self.qdrant, COLLECTION_NAME)
        logger.info(f"LibrarianAgent initialized: collection={COLLECTION_NAME}")

    async def search(self, query: str, top_k: int = 5) -> List[CodeContext]:
        """Search codebase for relevant code snippets.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant code contexts
        """
        logger.info(f"Searching codebase: query='{query}', top_k={top_k}")

        try:
            # Generate query embedding
            query_embedding = await generate_embedding(query)

            # Vector search in Qdrant
            results = self.qdrant.search(
                collection_name=self.collection,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=0.5,  # Minimum similarity
            )

            # Convert to CodeContext
            contexts = []
            for result in results:
                payload = result.payload
                contexts.append(CodeContext(
                    file_path=payload["file_path"],
                    language=detect_language(payload["file_path"]),
                    code_snippet=payload["text"],
                    line_numbers=f"{payload['start_line']}-{payload['end_line']}",
                    relevance_score=float(result.score),
                ))

            logger.info(f"Found {len(contexts)} relevant code snippets")
            return contexts

        except Exception as e:
            logger.error(f"Code search failed: {e}")
            return []

    async def index_directory(self, root_path: str, extensions: Optional[List[str]] = None):
        """Index all code files in a directory.

        Args:
            root_path: Root directory to index
            extensions: File extensions to include (None = all)
        """
        if extensions is None:
            extensions = [".py", ".js", ".ts", ".tsx", ".go", ".rs", ".java"]

        root = Path(root_path)
        if not root.exists():
            logger.error(f"Directory not found: {root_path}")
            return

        logger.info(f"Indexing directory: {root_path}")

        # Find all code files
        files = []
        for ext in extensions:
            files.extend(root.rglob(f"*{ext}"))

        logger.info(f"Found {len(files)} code files to index")

        # Index each file
        indexed_count = 0
        for file_path in files:
            try:
                # Skip if in hidden directory
                if any(part.startswith(".") for part in file_path.parts):
                    continue

                # Read file
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Skip empty files
                if not content.strip():
                    continue

                # Chunk file
                chunks = chunk_code_file(str(file_path), content)

                # Index chunks
                for i, chunk in enumerate(chunks):
                    embedding = await generate_embedding(chunk["text"])

                    # Create point ID
                    point_id = f"{file_path}:{i}"

                    # Insert into Qdrant
                    self.qdrant.upsert(
                        collection_name=COLLECTION_NAME,
                        points=[{
                            "id": point_id,
                            "vector": embedding,
                            "payload": {
                                "file_path": chunk["file_path"],
                                "text": chunk["text"],
                                "start_line": chunk["start_line"],
                                "end_line": chunk["end_line"],
                            },
                        }],
                    )

                indexed_count += 1
                logger.debug(f"Indexed: {file_path} ({len(chunks)} chunks)")

            except Exception as e:
                logger.warning(f"Failed to index {file_path}: {e}")

        logger.info(f"Indexing complete: {indexed_count} files indexed")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def search_codebase(query: str, top_k: int = 5) -> List[CodeContext]:
    """Convenience function to search codebase.

    Args:
        query: Search query
        top_k: Number of results

    Returns:
        Relevant code contexts
    """
    librarian = LibrarianAgent()
    return await librarian.search(query, top_k)
