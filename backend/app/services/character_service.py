from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Character
from ..schemas.characters import CharacterCreate, CharacterRead, CharacterUpdate


def list_characters(
    db: Session,
    *,
    user_id: int,
    campaign_id: int | None = None,
) -> Sequence[CharacterRead]:
    stmt = select(Character)
    stmt = stmt.where(Character.user_id == user_id)
    if campaign_id is not None:
        stmt = stmt.where(Character.campaign_id == campaign_id)

    results = db.execute(stmt).scalars().all()
    return [CharacterRead.model_validate(character, from_attributes=True) for character in results]


def create_character(db: Session, payload: CharacterCreate, user_id: int) -> CharacterRead:
    character = Character(
        name=payload.name,
        level=payload.level,
        race=payload.race,
        character_class=payload.character_class,
        background=payload.background,
        alignment=payload.alignment,
        experience_points=payload.experience_points,
        ability_scores=payload.ability_scores or {},
        skills=payload.skills or {},
        attributes=payload.attributes or {},
        notes=payload.notes,
        user_id=user_id,
        campaign_id=payload.campaign_id,
    )
    db.add(character)
    db.commit()
    db.refresh(character)
    return CharacterRead.model_validate(character, from_attributes=True)


def get_character(db: Session, character_id: int) -> CharacterRead | None:
    character = db.get(Character, character_id)
    if character is None:
        return None
    return CharacterRead.model_validate(character, from_attributes=True)


def update_character(db: Session, character_id: int, payload: CharacterUpdate) -> CharacterRead:
    character = db.get(Character, character_id)
    if character is None:
        raise ValueError("Character not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(character, key, value)

    db.add(character)
    db.commit()
    db.refresh(character)
    return CharacterRead.model_validate(character, from_attributes=True)


def delete_character(db: Session, character_id: int) -> None:
    character = db.get(Character, character_id)
    if character is None:
        raise ValueError("Character not found.")

    db.delete(character)
    db.commit()
