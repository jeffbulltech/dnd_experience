from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth import get_current_user
from ..models import User
from ..schemas.chat import ChatHistoryEntry, ChatMessage, ChatResponse
from ..services import campaign_service, chat_service, game_master

router = APIRouter(prefix="/chat")


@router.post("", response_model=ChatResponse)
def send_message(
    message: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    campaign = campaign_service.get_campaign(db, message.campaign_id)
    if not campaign or campaign.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Campaign access denied")

    message.user_id = current_user.id
    return game_master.handle_player_message(db, message)


@router.get("/history", response_model=Sequence[ChatHistoryEntry])
def get_chat_history(
    campaign_id: int = Query(..., ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Sequence[ChatHistoryEntry]:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if not campaign or campaign.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Campaign access denied")
    return chat_service.fetch_chat_history(db, campaign_id=campaign_id, limit=limit)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
