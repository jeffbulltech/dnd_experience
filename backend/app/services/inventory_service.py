from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import InventoryItem
from ..schemas.inventory import InventoryItemCreate, InventoryItemRead, InventoryItemUpdate


def list_inventory_items(
    db: Session,
    *,
    character_id: int | None = None,
) -> Sequence[InventoryItemRead]:
    stmt = select(InventoryItem)
    if character_id is not None:
        stmt = stmt.where(InventoryItem.character_id == character_id)

    items = db.execute(stmt).scalars().all()
    return [InventoryItemRead.model_validate(item, from_attributes=True) for item in items]


def create_inventory_item(db: Session, payload: InventoryItemCreate) -> InventoryItemRead:
    item = InventoryItem(
        character_id=payload.character_id,
        name=payload.name,
        quantity=payload.quantity,
        weight=payload.weight,
        description=payload.description,
        properties=payload.properties or {},
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return InventoryItemRead.model_validate(item, from_attributes=True)


def update_inventory_item(db: Session, item_id: int, payload: InventoryItemUpdate) -> InventoryItemRead:
    item = db.get(InventoryItem, item_id)
    if item is None:
        raise ValueError("Inventory item not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    db.add(item)
    db.commit()
    db.refresh(item)
    return InventoryItemRead.model_validate(item, from_attributes=True)


def delete_inventory_item(db: Session, item_id: int) -> None:
    item = db.get(InventoryItem, item_id)
    if item is None:
        raise ValueError("Inventory item not found.")

    db.delete(item)
    db.commit()

