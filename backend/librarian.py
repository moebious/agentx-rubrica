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
import uuid
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
    """Generate embedding for text.

    Prefers Gemini embeddings when GEMINI_API_KEY is configured. If not available
    (or calls fail), falls back to a deterministic local embedding to keep demos
    and offline indexing usable.

    Args:
        text: Text to embed

    Returns:
        Embedding vector (size 768)
    """

    def _local_fallback_embedding(s: str) -> List[float]:
        import hashlib

        digest = hashlib.sha256(s.encode("utf-8", errors="ignore")).digest()
        vals: List[float] = []
        for i in range(768):
            b = digest[i % len(digest)]
            vals.append(((b / 255.0) * 2.0) - 1.0)
        return vals

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key in {"your_gemini_api_key_here", ""}:
        return _local_fallback_embedding(text)

    try:
        from google.genai import Client

        client = Client(api_key=api_key)
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
        )
        return response.embedding.values

    except Exception as e:
        logger.warning(f"Gemini embedding failed, using local fallback: {e}")
        return _local_fallback_embedding(text)


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
            # Detect whether we're using local fallback embeddings (Gemini key missing)
            api_key = os.getenv("GEMINI_API_KEY")
            use_local_embedding = not api_key or api_key in {"your_gemini_api_key_here", ""}

            # Generate query embedding (may be local fallback)
            query_embedding = await generate_embedding(query)

            contexts: List[CodeContext] = []

            # Vector search in Qdrant (attempt semantic search first)
            try:
                results = self.qdrant.query_points(
                    collection_name=self.collection,
                    query=query_embedding,
                    limit=top_k,
                    with_payload=True,
                ).points

                for result in results:
                    payload = result.payload
                    contexts.append(CodeContext(
                        file_path=payload["file_path"],
                        language=detect_language(payload["file_path"]),
                        code_snippet=payload["text"],
                        line_numbers=f"{payload['start_line']}-{payload['end_line']}",
                        relevance_score=float(result.score),
                    ))

            except Exception as ve:
                logger.warning(f"Vector search failed: {ve}")

            # If we found results and are using a real embedding provider, return them.
            # If using local fallback embeddings, the vectors are deterministic and
            # semantic similarity is unreliable — fall through to payload keyword search
            # to guarantee citations.
            if contexts and not use_local_embedding:
                logger.info(f"Found {len(contexts)} relevant code snippets (vector search)")
                return contexts

            # Fallback: simple keyword match over payload text (demo resilience)
            tokens = [t for t in re.split(r"\W+", query.lower()) if len(t) >= 4]
            if not tokens:
                return contexts if contexts else []

            matched: List[CodeContext] = []
            next_offset = None
            while len(matched) < top_k:
                points, next_offset = self.qdrant.scroll(
                    collection_name=self.collection,
                    limit=128,
                    with_payload=True,
                    offset=next_offset,
                )
                if not points:
                    break

                for p in points:
                    payload = p.payload or {}
                    text = (payload.get("text") or "").lower()
                    if not text:
                        continue
                    if any(tok in text for tok in tokens):
                        file_path = payload.get("file_path")
                        if not file_path:
                            continue
                        matched.append(CodeContext(
                            file_path=file_path,
                            language=detect_language(file_path),
                            code_snippet=payload.get("text") or "",
                            line_numbers=f"{payload.get('start_line', 0)}-{payload.get('end_line', 0)}",
                            relevance_score=0.0,
                        ))
                        if len(matched) >= top_k:
                            break

                if next_offset is None:
                    break

            if matched:
                logger.info(f"Fallback keyword search found {len(matched)} snippets")
                return matched

            # If we had vector contexts but didn't return earlier (because of local embeddings),
            # return them as a last resort so we always return something when available.
            if contexts:
                logger.info(f"Returning vector search results as last resort: {len(contexts)} snippets")
                return contexts

            return []

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
                # Skip if in hidden directory or common build/dependency dirs
                skip_dirs = {".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__"}
                if any(part.startswith(".") or part in skip_dirs for part in file_path.parts):
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

                    # Create deterministic UUID point ID (Qdrant requires int or UUID)
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{file_path}:{i}"))

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
