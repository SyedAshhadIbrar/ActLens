#!/usr/bin/env python3
"""CLI script to ingest EU AI Act documents into the ActLens index.

Usage:
    python scripts/ingest.py
    python scripts/ingest.py --source hf
    python scripts/ingest.py --source files --data-dir data/raw
    python scripts/ingest.py --source both --languages en,nl,fr

Default source is the Hugging Face dataset:
    https://huggingface.co/datasets/jeroenherczeg/eu-ai-act

You can still ingest local PDF/HTML files from data/raw/ with --source files.
"""

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))


async def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest EU AI Act documents into ActLens")
    parser.add_argument(
        "--source",
        choices=["hf", "files", "both"],
        default=None,
        help="Data source (default: DATA_SOURCE from .env, usually hf)",
    )
    parser.add_argument(
        "--data-dir",
        default=str(ROOT / "data" / "raw"),
        help="Directory for local files when using --source files or both",
    )
    parser.add_argument(
        "--languages",
        default=None,
        help="Comma-separated ISO language codes for HF dataset (e.g. en,nl,fr)",
    )
    args = parser.parse_args()

    from app.config import settings
    from app.core.providers.registry import get_embedding_provider
    from app.ingestion.indexer import Indexer

    source = args.source or settings.data_source
    languages = None
    if args.languages:
        languages = [lang.strip().lower() for lang in args.languages.split(",") if lang.strip()]

    if source in ("files", "both"):
        data_dir = Path(args.data_dir)
        if not data_dir.exists():
            print(f"Error: data directory not found: {data_dir}")
            sys.exit(1)

        supported = {".pdf", ".html", ".htm", ".txt", ".md"}
        doc_files = [
            f for f in data_dir.iterdir() if f.is_file() and f.suffix.lower() in supported
        ]
        if source == "files" and not doc_files:
            print(f"No supported documents found in {data_dir}")
            print("Supported formats: PDF, HTML, TXT, MD")
            sys.exit(1)
        if doc_files:
            print(f"Found {len(doc_files)} local document(s):")
            for f in doc_files:
                print(f"  - {f.name}")

    if source in ("hf", "both"):
        lang_label = ", ".join(languages or settings.hf_language_list) or "all languages"
        print(f"Using Hugging Face dataset: {settings.hf_dataset_id} ({lang_label})")

    embedding = get_embedding_provider()
    indexer = Indexer(embedding)

    print("\nIngesting...")
    stats = await indexer.ingest(source, languages=languages)

    print(f"\nIngestion complete:")
    print(f"  Sources processed: {stats['files_processed']}")
    print(f"  Chunks added:      {stats['chunks_added']}")
    print(f"  Chunks updated:    {stats['chunks_updated']}")
    print(f"  Chunks unchanged:  {stats['chunks_unchanged']}")


if __name__ == "__main__":
    asyncio.run(main())
