from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth import get_current_user
from ..models import User
from ..schemas.combat import CombatActionRequest, CombatState, ParticipantCreate, ParticipantUpdate
from ..services import campaign_service, combat_engine

router = APIRouter(prefix="/combat")


def _verify_campaign_owner(db: Session, campaign_id: int, user_id: int) -> None:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if not campaign or campaign.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Campaign access denied")


@router.post("/action", response_model=CombatState)
def perform_combat_action(
    payload: CombatActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CombatState:
    _verify_campaign_owner(db, payload.campaign_id, current_user.id)
    try:
        return combat_engine.process_action(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/state/{campaign_id}", response_model=CombatState)
def get_combat_state(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CombatState:
    _verify_campaign_owner(db, campaign_id, current_user.id)
    return combat_engine.get_combat_state(db, campaign_id)


@router.post("/{campaign_id}/participants", response_model=CombatState, status_code=status.HTTP_201_CREATED)
def add_participant(
    campaign_id: int,
    payload: ParticipantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CombatState:
    _verify_campaign_owner(db, campaign_id, current_user.id)
    return combat_engine.add_participant(db, campaign_id, payload)


@router.put("/{campaign_id}/participants/{participant_id}", response_model=CombatState)
def update_participant(
    campaign_id: int,
    participant_id: int,
    payload: ParticipantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CombatState:
    _verify_campaign_owner(db, campaign_id, current_user.id)
    try:
        return combat_engine.update_participant(db, campaign_id, participant_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{campaign_id}/participants/{participant_id}", response_model=CombatState)
def delete_participant(
    campaign_id: int,
    participant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CombatState:
    _verify_campaign_owner(db, campaign_id, current_user.id)
    try:
        return combat_engine.remove_participant(db, campaign_id, participant_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
