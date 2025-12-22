from fastapi import APIRouter

from . import (
    adventures,
    auth,
    campaigns,
    campaign_attachments,
    catalog,
    character_builder,
    characters,
    chat,
    combat,
    dice,
    game_state,
    inventory,
)

router = APIRouter()
router.include_router(auth.router)
router.include_router(characters.router, tags=["characters"])
router.include_router(campaigns.router, tags=["campaigns"])
router.include_router(campaign_attachments.router)
router.include_router(chat.router, tags=["chat"])
router.include_router(dice.router, tags=["dice"])
router.include_router(combat.router, tags=["combat"])
router.include_router(game_state.router, tags=["game-state"])
router.include_router(inventory.router, tags=["inventory"])
router.include_router(character_builder.router)
router.include_router(catalog.router, tags=["catalog"])
router.include_router(adventures.router)
