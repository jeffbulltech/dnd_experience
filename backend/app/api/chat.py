from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..dependencies.auth import get_current_user
from ..models import User
from ..rate_limit import limiter
from ..schemas.chat import ChatHistoryEntry, ChatHistoryPage, ChatMessage, ChatResponse
from ..services import campaign_service, chat_service, game_master

settings = get_settings()
router = APIRouter(prefix="/chat")


@router.post("", response_model=ChatResponse)
@limiter.limit(settings.rate_limit_chat)
def send_message(
    request: Request,
    message: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    campaign = campaign_service.get_campaign(db, message.campaign_id)
    if not campaign or campaign.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Campaign access denied")

    message.user_id = current_user.id
    return game_master.handle_player_message(db, message)


@router.post("/stream")
@limiter.limit(settings.rate_limit_chat)
def stream_message(
    request: Request,
    message: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    campaign = campaign_service.get_campaign(db, message.campaign_id)
    if not campaign or campaign.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Campaign access denied")

    message.user_id = current_user.id
    return StreamingResponse(
        game_master.stream_player_message(db, message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history", response_model=ChatHistoryPage)
def get_chat_history(
    campaign_id: int = Query(..., ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    before: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatHistoryPage:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if not campaign or campaign.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Campaign access denied")
    return chat_service.fetch_chat_history_page(db, campaign_id=campaign_id, limit=limit, before=before)
