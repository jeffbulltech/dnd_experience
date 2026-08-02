"""Factory functions for creating test campaigns."""

from sqlalchemy.orm import Session

from app.services import campaign_service
from app.schemas.campaigns import CampaignCreate


def create_test_campaign(session: Session, owner_id: int, **overrides):
    """
    Create a test campaign with default values.
    
    Args:
        session: Database session
        owner_id: ID of the campaign owner
        **overrides: Override default values (name, description, adventure_template_id)
    
    Returns:
        Created CampaignRead instance
    """
    defaults = {
        "name": "Test Campaign",
        "description": "A test campaign for unit testing",
        "adventure_template_id": None,
    }
    defaults.update(overrides)
    
    payload = CampaignCreate(**defaults)
    return campaign_service.create_campaign(session, payload, owner_id=owner_id)
