from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CharacterDraftCreate(BaseModel):
    name: str | None = Field(None, max_length=150)
    starting_level: int = Field(1, ge=1, le=20)
    allow_feats: bool = False
    variant_flags: dict[str, Any] = Field(default_factory=dict)


class CharacterDraftSummary(BaseModel):
    id: int
    name: str | None
    status: str
    current_step: str | None
    starting_level: int
    allow_feats: bool
    updated_at: datetime
    character_id: int | None = None

    class Config:
        from_attributes = True


class CharacterDraftRead(CharacterDraftSummary):
    variant_flags: dict[str, Any] = Field(default_factory=dict)
    step_data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class CharacterDraftStepUpdate(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)
    mark_complete: bool | None = False

