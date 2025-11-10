from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CombatantState(BaseModel):
    id: int
    name: str
    initiative: int = 0
    hit_points: int
    max_hit_points: int
    armor_class: int
    conditions: list[str] = Field(default_factory=list)


class CombatState(BaseModel):
    campaign_id: int
    round_number: int = 0
    turn_order: list[int] = Field(default_factory=list)
    active_combatant_id: int | None = None
    combatants: dict[int, CombatantState] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class CombatActionRequest(BaseModel):
    campaign_id: int
    actor_id: int
    target_id: int | None = None
    action_type: Literal["attack", "spell", "ability", "item", "movement", "reaction"]
    description: str


class ParticipantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    initiative: int = Field(0)
    hit_points: int = Field(0)
    max_hit_points: int = Field(0)
    armor_class: int = Field(10, ge=0)
    conditions: list[str] = Field(default_factory=list)
    attributes: dict | None = None


class ParticipantCreate(ParticipantBase):
    pass


class ParticipantUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    initiative: int | None = None
    hit_points: int | None = None
    max_hit_points: int | None = None
    armor_class: int | None = None
    conditions: list[str] | None = None
    attributes: dict | None = None
