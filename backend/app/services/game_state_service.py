from sqlalchemy.orm import Session

from ..models import Campaign, GameState
from ..schemas.game_state import GameStateRead, GameStateUpdate


def get_game_state(db: Session, campaign_id: int) -> GameStateRead:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise ValueError("Campaign not found.")

    game_state = (
        db.query(GameState).filter(GameState.campaign_id == campaign_id).one_or_none()
    )

    if game_state is None:
        game_state = GameState(campaign_id=campaign_id, active_quests=[], extra={})
        db.add(game_state)
        db.commit()
        db.refresh(game_state)

    return GameStateRead(
        campaign_id=game_state.campaign_id,
        location=game_state.location,
        active_quests=game_state.active_quests or [],
        summary=game_state.summary,
        metadata=game_state.extra or {},
        updated_at=game_state.updated_at,
    )


def update_game_state(db: Session, campaign_id: int, payload: GameStateUpdate, *, owner_id: int) -> GameStateRead:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None or campaign.owner_id != owner_id:
        raise ValueError("Campaign not found.")

    game_state = (
        db.query(GameState)
        .filter(GameState.campaign_id == campaign_id)
        .one_or_none()
    )
    if game_state is None:
        raise ValueError("Game state not found.")

    update_data = payload.model_dump(exclude_unset=True)
    metadata_update = update_data.pop("metadata", None)
    for key, value in update_data.items():
        setattr(game_state, key, value)
    if metadata_update is not None:
        game_state.extra = metadata_update

    db.add(game_state)
    db.commit()
    db.refresh(game_state)
    return GameStateRead(
        campaign_id=game_state.campaign_id,
        location=game_state.location,
        active_quests=game_state.active_quests or [],
        summary=game_state.summary,
        metadata=game_state.extra or {},
        updated_at=game_state.updated_at,
    )
