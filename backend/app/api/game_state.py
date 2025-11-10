from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth import get_current_user
from ..models import User
from ..schemas.game_state import GameStateRead, GameStateUpdate
from ..services import campaign_service, game_state_service

router = APIRouter(prefix="/game-state")


@router.get("/{campaign_id}", response_model=GameStateRead)
def get_game_state(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GameStateRead:
    try:
        state = game_state_service.get_game_state(db, campaign_id)
        campaign = campaign_service.get_campaign(db, campaign_id)
        if not campaign or campaign.owner_id != current_user.id:
            raise ValueError("Campaign not found.")
        return state
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{campaign_id}", response_model=GameStateRead)
def update_game_state(
    campaign_id: int,
    payload: GameStateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GameStateRead:
    try:
        return game_state_service.update_game_state(db, campaign_id, payload, owner_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
