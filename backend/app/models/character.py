from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .campaign import Campaign
    from .character_draft import CharacterDraft
    from .chat import ChatMessage
    from .inventory import InventoryItem
    from .user import User


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    campaign_id: Mapped[int | None] = mapped_column(
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    race: Mapped[str | None] = mapped_column(String(50))
    character_class: Mapped[str | None] = mapped_column(String(50))
    background: Mapped[str | None] = mapped_column(String(100))
    alignment: Mapped[str | None] = mapped_column(String(50))
    experience_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ability_scores: Mapped[dict | None] = mapped_column(JSON, default=dict)
    skills: Mapped[dict | None] = mapped_column(JSON, default=dict)
    attributes: Mapped[dict | None] = mapped_column(JSON, default=dict)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    player: Mapped[User | None] = relationship("User", back_populates="characters")
    campaign: Mapped[Campaign | None] = relationship("Campaign", back_populates="characters")
    inventory_items: Mapped[list["InventoryItem"]] = relationship(
        "InventoryItem", back_populates="character", cascade="all, delete-orphan"
    )
    chats: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="character")
    builder_drafts: Mapped[list["CharacterDraft"]] = relationship("CharacterDraft", back_populates="character")

