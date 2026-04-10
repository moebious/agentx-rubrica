#!/usr/bin/env python
"""Rubrica codebase ingestion script.

Hybrid root selection (in priority order):
1) CLI --root
2) env CODEBASE_ROOT
3) ./codebase

Use --reset for reproducible demos.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Allow running as a script from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from loguru import logger

from backend.db.qdrant_client import get_qdrant_client, reset_collection, ensure_codebase_collection
from backend.librarian import LibrarianAgent, COLLECTION_NAME


def resolve_root(cli_root: str | None) -> Path:
    if cli_root:
        return Path(cli_root).expanduser().resolve()

    env_root = os.getenv("CODEBASE_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    return (Path.cwd() / "codebase").resolve()


async def main():
    parser = argparse.ArgumentParser(description="Ingest an e-commerce codebase into Qdrant for Rubrica RAG.")
    parser.add_argument("--root", help="Filesystem path to the e-commerce repo checkout")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate the Qdrant collection")
    parser.add_argument(
        "--ext",
        action="append",
        default=None,
        help="File extensions to index (repeatable). Example: --ext .ts --ext .js",
    )
    args = parser.parse_args()

    root = resolve_root(args.root)

    print("Rubrica Codebase Ingestion")
    print("=========================")
    print(f"Root: {root}")
    print(f"Collection: {COLLECTION_NAME}")

    if not root.exists() or not root.is_dir():
        raise SystemExit(
            "Codebase root not found. Provide --root, set CODEBASE_ROOT, or create ./codebase.\n"
            f"Resolved root was: {root}"
        )

    qdrant = get_qdrant_client()
    if args.reset:
        reset_collection(qdrant, COLLECTION_NAME)
    else:
        ensure_codebase_collection(qdrant, COLLECTION_NAME)

    librarian = LibrarianAgent()

    extensions = args.ext
    await librarian.index_directory(str(root), extensions=extensions)

    # Best-effort: print point count
    try:
        info = qdrant.get_collection(COLLECTION_NAME)
        print(f"Indexed. Points: {info.points_count}")
    except Exception as e:
        logger.warning(f"Could not read collection info: {e}")


if __name__ == "__main__":
    asyncio.run(main())
