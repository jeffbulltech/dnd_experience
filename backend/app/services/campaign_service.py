from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Campaign, ChatMessage as ChatLogEntry, GameState
from ..schemas.campaigns import CampaignCreate, CampaignRead, CampaignUpdate
from ..schemas.chat import ChatMessage
from . import adventure_service, game_master, rag_service


def list_campaigns(db: Session, *, owner_id: int) -> Sequence[CampaignRead]:
    stmt = select(Campaign).where(Campaign.owner_id == owner_id)

    campaigns = db.execute(stmt).scalars().all()
    return [CampaignRead.model_validate(campaign, from_attributes=True) for campaign in campaigns]


def create_campaign(db: Session, payload: CampaignCreate, owner_id: int) -> CampaignRead:
    campaign = Campaign(
        name=payload.name,
        description=payload.description,
        adventure_template_id=payload.adventure_template_id,
        owner_id=owner_id,
    )
    db.add(campaign)
    db.flush()

    if campaign.game_state is None:
        game_state = GameState(campaign_id=campaign.id, location=None, active_quests=[])
        db.add(game_state)

    db.commit()
    db.refresh(campaign)

    # Generate welcome message
    _generate_welcome_message(db, campaign, owner_id)

    db.refresh(campaign)
    return CampaignRead.model_validate(campaign, from_attributes=True)


def _generate_welcome_message(db: Session, campaign: Campaign, user_id: int) -> None:
    """Generate and store an initial welcome message from the AI Game Master."""
    import logging
    from .ollama_service import _format_rag_context, _get_client
    from ..config import get_settings

    logger = logging.getLogger(__name__)
    settings = get_settings()

    # Get adventure seed content if template is selected
    adventure_seed = ""
    if campaign.adventure_template_id and campaign.adventure_template_id != "custom":
        adventure_seed = adventure_service.get_adventure_seed_content(campaign.adventure_template_id)
        template = adventure_service.get_adventure_template(campaign.adventure_template_id)
        if template:
            adventure_seed = f"Adventure: {template.name}\n{template.description}\n\n{adventure_seed}"

    # Create a system message to generate the welcome
    welcome_prompt = (
        "Welcome the adventurer to this new campaign. "
        "Provide an engaging, atmospheric introduction that sets the scene and invites them to begin their journey. "
        "Be warm and inviting, but also create a sense of mystery and adventure. "
        "Address them directly as 'adventurer' or 'hero'."
    )

    # Create a chat message for the welcome (to fetch RAG context)
    welcome_message = ChatMessage(
        campaign_id=campaign.id,
        character_id=None,
        content="Begin the adventure.",
        user_id=user_id,
    )

    # Generate the welcome response
    try:
        # Fetch some relevant rules for context
        rag_context = rag_service.fetch_relevant_rules(db, welcome_message)
        rag_text = _format_rag_context(rag_context)

        # Build custom system prompt for welcome
        welcome_system_prompt = (
            "You are an expert Dungeon Master for Dungeons & Dragons 5th Edition. "
            "You are welcoming a new adventurer to their campaign.\n\n"
            "THE GAME MASTER SCREEN - CRITICAL: Maintain your GM screen even in the welcome message. "
            "Do not reveal specific monster stats, exact treasure locations, secret plot details, or hidden "
            "information. Set the scene atmospherically and invite exploration, but keep mysteries mysterious.\n\n"
        )

        if adventure_seed:
            welcome_system_prompt += (
                f"Campaign Adventure Context (for your reference only - do not reveal all details):\n{adventure_seed}\n\n"
            )

        welcome_system_prompt += (
            f"Relevant rules and references:\n{rag_text}\n\n"
            "Craft a warm, engaging welcome message that introduces the campaign and sets the scene. "
            "Be atmospheric and inviting. Address the adventurer directly. "
            "This is the very first message they will see when entering the campaign. "
            "Hint at adventure and mystery without spoiling secrets or revealing mechanical details."
        )

        messages = [
            {"role": "system", "content": welcome_system_prompt},
            {"role": "user", "content": welcome_prompt},
        ]

        try:
            response = _get_client().chat(model=settings.ollama_model, messages=messages)
            payload = response.get("message", {})
            welcome_content = payload.get("content", "").strip()
            if not welcome_content:
                raise ValueError("Empty response from Ollama")
        except Exception as e:
            logger.warning(f"Failed to generate welcome from Ollama: {e}")
            welcome_content = (
                f"Welcome, adventurer, to {campaign.name}! "
                "Your journey begins here. What would you like to do?"
            )

        # Save the welcome message
        gm_entry = ChatLogEntry(
            campaign_id=campaign.id,
            character_id=None,
            role="gm",
            content=welcome_content,
            rag_context=list(rag_context.context_chunks) if hasattr(rag_context, 'context_chunks') else [],
            extra={"is_welcome": True},
        )
        db.add(gm_entry)
        db.commit()
    except Exception as e:
        # If welcome generation fails, create a simple default message
        logger.warning(f"Failed to generate welcome message: {e}")
        default_welcome = (
            f"Welcome, adventurer, to {campaign.name}! "
            "Your journey begins here. What would you like to do?"
        )
        gm_entry = ChatLogEntry(
            campaign_id=campaign.id,
            character_id=None,
            role="gm",
            content=default_welcome,
            rag_context=[],
            extra={"is_welcome": True},
        )
        db.add(gm_entry)
        db.commit()


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
