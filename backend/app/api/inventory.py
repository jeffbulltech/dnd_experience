from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth import get_current_user
from ..models import InventoryItem, User
from ..services import character_service, inventory_service
from ..schemas.inventory import InventoryItemCreate, InventoryItemRead, InventoryItemUpdate

router = APIRouter(prefix="/inventory")


def _verify_character_ownership(db: Session, character_id: int, user_id: int) -> None:
    character = character_service.get_character(db, character_id)
    if not character or character.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Character access denied")


@router.get("", response_model=Sequence[InventoryItemRead])
def list_inventory_items(
    character_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Sequence[InventoryItemRead]:
    if character_id is not None:
        _verify_character_ownership(db, character_id, current_user.id)
        return inventory_service.list_inventory_items(db, character_id=character_id)

    characters = character_service.list_characters(db, user_id=current_user.id)
    items: list[InventoryItemRead] = []
    for character in characters:
        items.extend(inventory_service.list_inventory_items(db, character_id=character.id))
    return items


@router.post("", response_model=InventoryItemRead, status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    payload: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InventoryItemRead:
    _verify_character_ownership(db, payload.character_id, current_user.id)
    return inventory_service.create_inventory_item(db, payload)


@router.put("/{item_id}", response_model=InventoryItemRead)
def update_inventory_item(
    item_id: int,
    payload: InventoryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InventoryItemRead:
    item = db.get(InventoryItem, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    _verify_character_ownership(db, item.character_id, current_user.id)
    try:
        return inventory_service.update_inventory_item(db, item_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    item = db.get(InventoryItem, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    _verify_character_ownership(db, item.character_id, current_user.id)
    try:
        inventory_service.delete_inventory_item(db, item_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

