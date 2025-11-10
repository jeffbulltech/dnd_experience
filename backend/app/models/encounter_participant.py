from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .character import Character
    from .encounter import Encounter


class EncounterParticipant(Base):
    __tablename__ = "encounter_participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    encounter_id: Mapped[int] = mapped_column(ForeignKey("encounters.id", ondelete="CASCADE"), nullable=False)
    character_id: Mapped[int | None] = mapped_column(ForeignKey("characters.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    initiative: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hit_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_hit_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    armor_class: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    conditions: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    attributes: Mapped[dict | None] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    encounter: Mapped[Encounter] = relationship("Encounter", back_populates="participants")
    character: Mapped[Character | None] = relationship("Character")

