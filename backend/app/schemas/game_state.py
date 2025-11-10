from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class GameStateRead(BaseModel):
    campaign_id: int
    location: str | None = None
    active_quests: list[str] = Field(default_factory=list)
    summary: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class GameStateUpdate(BaseModel):
    location: str | None = None
    active_quests: list[str] | None = None
    summary: str | None = None
    metadata: dict[str, Any] | None = None
