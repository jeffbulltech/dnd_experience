from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth import get_current_user
from ..models import User
from ..services import campaign_service, character_service, dice_service
from ..schemas.dice import DiceRollLog, DiceRollRequest, DiceRollResult
from ..utils.dice_roller import roll_dice

router = APIRouter(prefix="/dice")


@router.post("/roll", response_model=DiceRollResult)
def roll_dice_endpoint(
    payload: DiceRollRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DiceRollResult:
    if payload.campaign_id is not None:
        campaign = campaign_service.get_campaign(db, payload.campaign_id)
        if not campaign or campaign.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Campaign access denied")
    if payload.character_id is not None:
        character = character_service.get_character(db, payload.character_id)
        if not character or character.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Character access denied")

    result = roll_dice(payload)
    dice_service.record_roll(
        db,
        campaign_id=payload.campaign_id,
        character_id=payload.character_id,
        roller_type=payload.roller_type or "player",
        expression=result.expression,
        total=result.total,
        detail=result.detail,
    )
    return result


@router.get("/history", response_model=Sequence[DiceRollLog])
def get_roll_history(
    campaign_id: int | None = Query(default=None, ge=1),
    character_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Sequence[DiceRollLog]:
    if campaign_id is not None:
        campaign = campaign_service.get_campaign(db, campaign_id)
        if not campaign or campaign.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Campaign access denied")
    if character_id is not None:
        character = character_service.get_character(db, character_id)
        if not character or character.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Character access denied")
    return dice_service.list_rolls(db, campaign_id=campaign_id, character_id=character_id, limit=limit)
from typing import Sequence

