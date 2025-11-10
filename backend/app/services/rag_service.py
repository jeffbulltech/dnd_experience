from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from sqlalchemy.orm import Session

from ..config import get_settings
from ..schemas.chat import ChatHistoryEntry, ChatMessage

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class RAGContext:
    citations: Sequence["RAGCitation"] = field(default_factory=tuple)

    @property
    def context_chunks(self) -> list[str]:
        return [citation.excerpt for citation in self.citations]

    @property
    def sources(self) -> list[str]:
        return [citation.source for citation in self.citations]


@dataclass
class RAGCitation:
    excerpt: str
    source: str
    chunk_id: str | None = None
    score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "excerpt": self.excerpt,
            "source": self.source,
            "chunk_id": self.chunk_id,
            "score": self.score,
            "metadata": self.metadata or {},
        }
        return {key: value for key, value in payload.items() if value not in (None, {}, [])}


@dataclass
class IngestionSummary:
    source_directory: Path
    persist_directory: Path
    documents_ingested: int
    chunks_written: int


def fetch_relevant_rules(db: Session, message: ChatMessage, *, top_k: int | None = None) -> RAGContext:
    """Retrieve rule excerpts relevant to the player's message."""
    _ = db  # Reserved for future per-campaign filtering.
    store = _get_vector_store()

    if store is None:
        logger.debug("Vector store unavailable; returning empty RAG context.")
        return RAGContext()

    query = message.content.strip()
    if not query:
        return RAGContext()

    search_limit = top_k or settings.rag_top_k
    try:
        docs_with_scores = store.similarity_search_with_score(query, k=search_limit)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Similarity search failed: %s", exc)
        return RAGContext()

    citations: list[RAGCitation] = []
    for doc, score in docs_with_scores:
        metadata = doc.metadata or {}
        citation = RAGCitation(
            excerpt=doc.page_content.strip(),
            source=_format_source(metadata),
            chunk_id=metadata.get("chunk_id"),
            score=float(score) if score is not None else None,
            metadata={
                key: value
                for key, value in metadata.items()
                if key not in {"chunk_id"} and value is not None
            },
        )
        citations.append(citation)

    return RAGContext(citations=tuple(citations))


def ingest_corpus(
    source_dir: Path,
    *,
    recreate: bool = False,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> IngestionSummary:
    """Load SRD documents, create embeddings, and persist them to Chroma."""
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory '{source_dir}' does not exist.")

    if recreate and settings.vector_store_path.exists():
        shutil.rmtree(settings.vector_store_path)
        _get_vector_store.cache_clear()

    documents = _load_documents(source_dir)
    if not documents:
        raise ValueError(f"No ingestible documents found in '{source_dir}'.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.rag_chunk_size,
        chunk_overlap=chunk_overlap or settings.rag_chunk_overlap,
    )

    splits: list[Document] = []
    for doc in documents:
        per_doc_splits = text_splitter.split_documents([doc])
        for index, chunk in enumerate(per_doc_splits):
            chunk.metadata.setdefault("source", doc.metadata.get("source"))
            chunk.metadata["chunk_index"] = index
            chunk.metadata["chunk_id"] = f"{chunk.metadata['source']}#chunk-{index}"
            splits.append(chunk)

    settings.vector_store_path.mkdir(parents=True, exist_ok=True)
    Chroma.from_documents(
        documents=splits,
        embedding=_get_embeddings(),
        collection_name=settings.rag_collection_name,
        persist_directory=str(settings.vector_store_path),
    ).persist()

    _get_vector_store.cache_clear()

    logger.info(
        "Ingested %s documents into vector store at %s",
        len(splits),
        settings.vector_store_path,
    )

    return IngestionSummary(
        source_directory=source_dir,
        persist_directory=settings.vector_store_path,
        documents_ingested=len(documents),
        chunks_written=len(splits),
    )


@lru_cache
def _get_embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(model=settings.ollama_model, base_url=settings.ollama_base_url)


@lru_cache
def _get_vector_store() -> Chroma | None:
    if not settings.vector_store_path.exists():
        return None

    try:
        return Chroma(
            collection_name=settings.rag_collection_name,
            persist_directory=str(settings.vector_store_path),
            embedding_function=_get_embeddings(),
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to initialize Chroma vector store: %s", exc)
        return None


def _load_documents(source_dir: Path) -> list[Document]:
    supported_extensions = (".txt", ".md", ".json")
    documents: list[Document] = []

    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in supported_extensions:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1")

        metadata = {
            "source": str(path.relative_to(source_dir)),
            "filename": path.name,
        }
        documents.append(Document(page_content=text, metadata=metadata))

    return documents


def _format_source(metadata: dict[str, Any]) -> str:
    source = metadata.get("source", "SRD reference")
    chunk_index = metadata.get("chunk_index")
    if chunk_index is not None:
        return f"{source} (section {chunk_index + 1})"
    return str(source)


def summarize_chat_history(
    entries: Sequence[ChatHistoryEntry],
    *,
    tail: int = 6,
    max_points: int = 6,
    max_chars: int = 600,
) -> str:
    """Produce a lightweight summary of older chat messages."""
    if not entries:
        return ""

    chronological = list(reversed(entries))
    if len(chronological) <= tail:
        return ""

    older_entries = chronological[:-tail]
    summary_points: list[str] = []
    for entry in older_entries[-20:]:
        role = "Player" if entry.role == "player" else "GM"
        content = entry.content.strip().replace("\n", " ")
        if len(content) > 140:
            content = f"{content[:137]}..."
        summary_points.append(f"{role}: {content}")

    summary_points = summary_points[-max_points:]
    summary = "\n".join(f"- {point}" for point in summary_points)
    return summary[:max_chars]
