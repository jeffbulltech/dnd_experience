from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..models import DiceRoll
from ..schemas.dice import DiceRollLog


def record_roll(
    db: Session,
    *,
    campaign_id: int | None,
    character_id: int | None,
    roller_type: str,
    expression: str,
    total: int,
    detail: dict | None,
) -> DiceRollLog:
    entry = DiceRoll(
        campaign_id=campaign_id,
        character_id=character_id,
        roller_type=roller_type,
        expression=expression,
        total=total,
        detail=detail or {},
        extra={},
        created_at=datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return DiceRollLog(
        id=entry.id,
        campaign_id=entry.campaign_id,
        character_id=entry.character_id,
        roller_type=entry.roller_type,
        expression=entry.expression,
        total=entry.total,
        detail=entry.detail or {},
        metadata=entry.extra or {},
        created_at=entry.created_at.isoformat(),
    )


def list_rolls(
    db: Session,
    *,
    campaign_id: int | None = None,
    character_id: int | None = None,
    limit: int = 20,
) -> Sequence[DiceRollLog]:
    stmt = select(DiceRoll).order_by(desc(DiceRoll.created_at))
    if campaign_id is not None:
        stmt = stmt.where(DiceRoll.campaign_id == campaign_id)
    if character_id is not None:
        stmt = stmt.where(DiceRoll.character_id == character_id)
    stmt = stmt.limit(limit)

    rolls = db.execute(stmt).scalars().all()
    return [
        DiceRollLog(
            id=roll.id,
            campaign_id=roll.campaign_id,
            character_id=roll.character_id,
            roller_type=roll.roller_type,
            expression=roll.expression,
            total=roll.total,
            detail=roll.detail or {},
            metadata=roll.extra or {},
            created_at=roll.created_at.isoformat(),
        )
        for roll in rolls
    ]

