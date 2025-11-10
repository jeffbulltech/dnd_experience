from __future__ import annotations

from datetime import datetime
from typing import Literal, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .campaign import Campaign
    from .character import Character


class DiceRoll(Base):
    __tablename__ = "dice_rolls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    character_id: Mapped[int | None] = mapped_column(ForeignKey("characters.id", ondelete="SET NULL"))
    roller_type: Mapped[Literal["player", "gm", "system"]] = mapped_column(String(20), nullable=False)
    expression: Mapped[str] = mapped_column(String(50), nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    detail: Mapped[dict | None] = mapped_column(JSON, default=dict)
    extra: Mapped[dict | None] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    campaign: Mapped[Campaign] = relationship("Campaign", back_populates="dice_rolls")
    character: Mapped[Character | None] = relationship("Character")

