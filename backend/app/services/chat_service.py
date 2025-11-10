from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..models import ChatMessage
from ..schemas.chat import ChatHistoryEntry


def fetch_chat_history(
    db: Session,
    *,
    campaign_id: int,
    limit: int = 50,
) -> Sequence[ChatHistoryEntry]:
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.campaign_id == campaign_id)
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    messages = db.execute(stmt).scalars().all()
    history: list[ChatHistoryEntry] = []
    for message in messages:
        history.append(
            ChatHistoryEntry(
                id=message.id,
                campaign_id=message.campaign_id,
                character_id=message.character_id,
                role=message.role,
                content=message.content,
                rag_context=message.rag_context or [],
                metadata=message.extra or {},
                created_at=message.created_at,
            )
        )
    return history

