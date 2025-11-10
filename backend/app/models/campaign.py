from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .character import Character
    from .campaign_attachment import CampaignAttachment
    from .chat import ChatMessage
    from .dice import DiceRoll
    from .encounter import Encounter
    from .game_state import GameState
    from .user import User


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    owner: Mapped[User] = relationship("User", back_populates="campaigns")
    characters: Mapped[list["Character"]] = relationship("Character", back_populates="campaign")
    game_state: Mapped["GameState"] = relationship(
        "GameState", back_populates="campaign", uselist=False, cascade="all, delete-orphan"
    )
    chats: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="campaign")
    encounters: Mapped[list["Encounter"]] = relationship("Encounter", back_populates="campaign")
    dice_rolls: Mapped[list["DiceRoll"]] = relationship("DiceRoll", back_populates="campaign")
    attachments: Mapped[list["CampaignAttachment"]] = relationship(
        "CampaignAttachment", back_populates="campaign", cascade="all, delete-orphan"
    )

