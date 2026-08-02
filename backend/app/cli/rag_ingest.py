from __future__ import annotations

import argparse
import logging
from pathlib import Path

from app.logging_config import setup_logging
from app.services import rag_service

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser(description="Ingest SRD documents into the vector store.")
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "data" / "srd",
        help="Directory containing SRD source documents (default: backend/data/srd).",
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Rebuild the vector store from scratch before ingestion.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=None,
        help="Override the default chunk size for text splitting.",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=None,
        help="Override the default chunk overlap for text splitting.",
    )
    args = parser.parse_args()

    summary = rag_service.ingest_corpus(
        args.source_dir,
        recreate=args.recreate,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    logger.info(
        "Ingested %d documents into %d chunks at %s",
        summary.documents_ingested,
        summary.chunks_written,
        summary.persist_directory,
    )


if __name__ == "__main__":
    main()

