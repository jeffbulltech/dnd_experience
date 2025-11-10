from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from ..models import ChatMessage as ChatLogEntry
from ..schemas.chat import ChatMessage, ChatResponse
from . import chat_service, ollama_service, rag_service


def handle_player_message(db: Session, message: ChatMessage) -> ChatResponse:
    """Process player input using RAG and Ollama, persisting the exchange."""
    rag_context = rag_service.fetch_relevant_rules(db, message)
    history_entries = chat_service.fetch_chat_history(db, campaign_id=message.campaign_id, limit=120)
    chat_summary = rag_service.summarize_chat_history(history_entries)

    gm_reply = ollama_service.generate_gm_response(message, rag_context, chat_summary=chat_summary)

    metadata: dict[str, Any] = {"combatActive": False}
    if gm_reply.model:
        metadata["model"] = gm_reply.model
    if gm_reply.prompt_tokens is not None:
        metadata["promptTokens"] = gm_reply.prompt_tokens
    if gm_reply.completion_tokens is not None:
        metadata["completionTokens"] = gm_reply.completion_tokens
    if rag_context.citations:
        metadata["ragCitations"] = [citation.as_dict() for citation in rag_context.citations]
    if rag_context.sources:
        metadata["ragSources"] = rag_context.sources
    if chat_summary:
        metadata["chatSummary"] = chat_summary

    player_entry = ChatLogEntry(
        campaign_id=message.campaign_id,
        character_id=message.character_id,
        role="player",
        content=message.content,
        extra={"user_id": message.user_id} if message.user_id else {},
    )
    gm_entry = ChatLogEntry(
        campaign_id=message.campaign_id,
        character_id=None,
        role="gm",
        content=gm_reply.content,
        rag_context=list(rag_context.context_chunks),
        extra=metadata,
    )

    db.add(player_entry)
    db.add(gm_entry)
    db.commit()

    return ChatResponse(
        response=gm_reply.content,
        rag_sources=rag_context.sources,
        metadata=metadata,
        timestamp=gm_entry.created_at,
    )
