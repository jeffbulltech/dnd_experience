from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Campaign, GameState
from ..schemas.campaigns import CampaignCreate, CampaignRead, CampaignUpdate


def list_campaigns(db: Session, *, owner_id: int) -> Sequence[CampaignRead]:
    stmt = select(Campaign).where(Campaign.owner_id == owner_id)

    campaigns = db.execute(stmt).scalars().all()
    return [CampaignRead.model_validate(campaign, from_attributes=True) for campaign in campaigns]


def create_campaign(db: Session, payload: CampaignCreate, owner_id: int) -> CampaignRead:
    campaign = Campaign(
        name=payload.name,
        description=payload.description,
        owner_id=owner_id,
    )
    db.add(campaign)
    db.flush()

    if campaign.game_state is None:
        game_state = GameState(campaign_id=campaign.id, location=None, active_quests=[])
        db.add(game_state)

    db.commit()
    db.refresh(campaign)
    return CampaignRead.model_validate(campaign, from_attributes=True)


def get_campaign(db: Session, campaign_id: int) -> CampaignRead | None:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        return None
    return CampaignRead.model_validate(campaign, from_attributes=True)


def update_campaign(db: Session, campaign_id: int, payload: CampaignUpdate, *, owner_id: int) -> CampaignRead:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise ValueError("Campaign not found.")
    if campaign.owner_id != owner_id:
        raise ValueError("Campaign not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(campaign, key, value)

    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return CampaignRead.model_validate(campaign, from_attributes=True)


def delete_campaign(db: Session, campaign_id: int, *, owner_id: int) -> None:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise ValueError("Campaign not found.")
    if campaign.owner_id != owner_id:
        raise ValueError("Campaign not found.")

    db.delete(campaign)
    db.commit()
