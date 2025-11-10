from datetime import datetime

from typing import Any

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    campaign_id: int
    character_id: int | None = None
    content: str = Field(..., min_length=1)
    user_id: int | None = None


class ChatResponse(BaseModel):
    response: str
    rag_sources: list[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatHistoryEntry(BaseModel):
    id: int
    campaign_id: int
    character_id: int | None = None
    role: str
    content: str
    rag_context: list[str] | None = None
    metadata: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True
