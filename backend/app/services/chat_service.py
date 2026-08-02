from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..models import ChatMessage
from ..schemas.chat import ChatHistoryEntry, ChatHistoryPage


def _to_entry(message: ChatMessage) -> ChatHistoryEntry:
    return ChatHistoryEntry(
        id=message.id,
        campaign_id=message.campaign_id,
        character_id=message.character_id,
        role=message.role,
        content=message.content,
        rag_context=message.rag_context or [],
        metadata=message.extra or {},
        created_at=message.created_at,
    )


def fetch_chat_history(
    db: Session,
    *,
    campaign_id: int,
    limit: int = 50,
) -> Sequence[ChatHistoryEntry]:
    """Fetch chat history (newest first). Used internally by game_master for context."""
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.campaign_id == campaign_id)
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    messages = db.execute(stmt).scalars().all()
    return [_to_entry(m) for m in messages]


def fetch_chat_history_page(
    db: Session,
    *,
    campaign_id: int,
    limit: int = 50,
    before: int | None = None,
) -> ChatHistoryPage:
    """Fetch a page of chat history with cursor-based pagination.

    Args:
        campaign_id: The campaign to fetch history for.
        limit: Max messages to return.
        before: If provided, only return messages with id < this value (older).

    Returns:
        ChatHistoryPage with items (newest-first), has_more flag, and next_cursor.
    """
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.campaign_id == campaign_id)
    )
    if before is not None:
        stmt = stmt.where(ChatMessage.id < before)

    # Fetch one extra to determine has_more
    stmt = stmt.order_by(desc(ChatMessage.id)).limit(limit + 1)
    messages = db.execute(stmt).scalars().all()

    has_more = len(messages) > limit
    page_messages = messages[:limit]

    items = [_to_entry(m) for m in page_messages]
    next_cursor = page_messages[-1].id if has_more and page_messages else None

    return ChatHistoryPage(items=items, has_more=has_more, next_cursor=next_cursor)

