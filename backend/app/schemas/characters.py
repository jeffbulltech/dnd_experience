from typing import Any

from pydantic import BaseModel, Field


class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    level: int = Field(1, ge=1, le=20)
    race: str | None = Field(None, max_length=50)
    character_class: str | None = Field(None, max_length=50)
    background: str | None = Field(None, max_length=100)
    alignment: str | None = Field(None, max_length=50)
    experience_points: int = Field(0, ge=0)
    ability_scores: dict[str, int] | None = None
    skills: dict[str, int] | None = None
    attributes: dict[str, Any] | None = None
    notes: str | None = None
    campaign_id: int | None = Field(None, ge=1)


class CharacterCreate(CharacterBase):
    pass


class CharacterUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    level: int | None = Field(None, ge=1, le=20)
    race: str | None = Field(None, max_length=50)
    character_class: str | None = Field(None, max_length=50)
    background: str | None = Field(None, max_length=100)
    alignment: str | None = Field(None, max_length=50)
    experience_points: int | None = Field(None, ge=0)
    ability_scores: dict[str, int] | None = None
    skills: dict[str, int] | None = None
    attributes: dict[str, Any] | None = None
    notes: str | None = None
    campaign_id: int | None = Field(None, ge=1)


class CharacterRead(CharacterBase):
    id: int
    user_id: int | None = None

    class Config:
        from_attributes = True
