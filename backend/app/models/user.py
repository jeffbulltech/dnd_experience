from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


if TYPE_CHECKING:
    from .campaign import Campaign
    from .character import Character
    from .character_draft import CharacterDraft


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    campaigns: Mapped[list["Campaign"]] = relationship("Campaign", back_populates="owner", cascade="all, delete-orphan")
    characters: Mapped[list["Character"]] = relationship(
        "Character", back_populates="player", cascade="all, delete-orphan"
    )
    character_drafts: Mapped[list["CharacterDraft"]] = relationship(
        "CharacterDraft", back_populates="user", cascade="all, delete-orphan"
    )

