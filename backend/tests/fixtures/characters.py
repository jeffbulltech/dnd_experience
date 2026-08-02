"""Factory functions for creating test characters."""

from sqlalchemy.orm import Session

from app.services import character_service
from app.schemas.characters import CharacterCreate


def create_test_character(session: Session, user_id: int, campaign_id: int | None = None, **overrides):
    """
    Create a test character with default values.
    
    Args:
        session: Database session
        user_id: ID of the character owner
        campaign_id: Optional campaign ID to link character to
        **overrides: Override default values (name, level, race, character_class, etc.)
    
    Returns:
        Created CharacterRead instance
    """
    defaults = {
        "name": "Test Character",
        "level": 1,
        "race": "Human",
        "character_class": "Fighter",
        "background": "Soldier",
        "campaign_id": campaign_id,
    }
    defaults.update(overrides)
    
    payload = CharacterCreate(**defaults)
    return character_service.create_character(session, payload, user_id=user_id)
