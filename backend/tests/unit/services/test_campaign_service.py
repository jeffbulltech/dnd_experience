"""Unit tests for campaign_service module."""

import pytest

from app.models import ChatMessage, GameState
from app.schemas.campaigns import CampaignCreate, CampaignUpdate
from app.services import campaign_service
from tests.fixtures.campaigns import create_test_campaign
from tests.fixtures.users import create_test_user


class TestCampaignService:
    """Unit tests for campaign_service functions."""

    def test_create_campaign_success(self, db_session):
        """Test successful campaign creation."""
        user = create_test_user(db_session)
        payload = CampaignCreate(
            name="New Campaign",
            description="Test description"
        )
        
        result = campaign_service.create_campaign(
            db_session, payload, owner_id=user.id
        )
        
        assert result.id > 0
        assert result.name == "New Campaign"
        assert result.description == "Test description"
        assert result.owner_id == user.id
        assert result.is_active is True

    def test_create_campaign_creates_game_state(self, db_session):
        """Test that campaign creation automatically creates a game state."""
        user = create_test_user(db_session)
        payload = CampaignCreate(name="Game State Test")
        
        result = campaign_service.create_campaign(
            db_session, payload, owner_id=user.id
        )
        
        # Verify game state was created
        game_state = db_session.query(GameState).filter(
            GameState.campaign_id == result.id
        ).first()
        
        assert game_state is not None
        assert game_state.campaign_id == result.id
        assert game_state.location is None
        assert game_state.active_quests == []

    def test_create_campaign_with_adventure_template(self, db_session):
        """Test campaign creation with adventure template ID."""
        user = create_test_user(db_session)
        payload = CampaignCreate(
            name="Adventure Campaign",
            adventure_template_id="lost-mine-of-phandelver"
        )
        
        result = campaign_service.create_campaign(
            db_session, payload, owner_id=user.id
        )
        
        assert result.adventure_template_id == "lost-mine-of-phandelver"

    def test_create_campaign_with_custom_adventure(self, db_session):
        """Test campaign creation with custom adventure (None template ID)."""
        user = create_test_user(db_session)
        payload = CampaignCreate(
            name="Custom Campaign",
            adventure_template_id="custom"
        )
        
        result = campaign_service.create_campaign(
            db_session, payload, owner_id=user.id
        )
        
        assert result.adventure_template_id == "custom"

    def test_create_campaign_generates_welcome_message(self, db_session, mock_ollama_client):
        """Test that welcome message is generated on campaign creation."""
        user = create_test_user(db_session)
        payload = CampaignCreate(name="Welcome Test")
        
        result = campaign_service.create_campaign(
            db_session, payload, owner_id=user.id
        )
        
        # Verify welcome message was created
        messages = db_session.query(ChatMessage).filter(
            ChatMessage.campaign_id == result.id,
            ChatMessage.role == "gm"
        ).all()
        
        assert len(messages) == 1
        assert messages[0].extra.get("is_welcome") is True
        assert "Welcome" in messages[0].content or "adventurer" in messages[0].content.lower()

    def test_list_campaigns_filters_by_owner(self, db_session):
        """Test that list_campaigns only returns owner's campaigns."""
        owner1 = create_test_user(db_session, username="owner1")
        owner2 = create_test_user(db_session, username="owner2")
        
        campaign1 = create_test_campaign(db_session, owner1.id, name="Campaign 1")
        campaign2 = create_test_campaign(db_session, owner2.id, name="Campaign 2")
        
        owner1_campaigns = campaign_service.list_campaigns(
            db_session, owner_id=owner1.id
        )
        
        assert len(owner1_campaigns) == 1
        assert owner1_campaigns[0].id == campaign1.id
        assert owner1_campaigns[0].id != campaign2.id

    def test_list_campaigns_empty_for_user(self, db_session):
        """Test that list_campaigns returns empty list for user with no campaigns."""
        user = create_test_user(db_session)
        
        campaigns = campaign_service.list_campaigns(
            db_session, owner_id=user.id
        )
        
        assert len(campaigns) == 0

    def test_get_campaign_success(self, db_session):
        """Test successful campaign retrieval."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id, name="Get Test")
        
        result = campaign_service.get_campaign(db_session, campaign.id)
        
        assert result is not None
        assert result.id == campaign.id
        assert result.name == "Get Test"
        assert result.owner_id == user.id

    def test_get_campaign_not_found(self, db_session):
        """Test retrieval of non-existent campaign."""
        result = campaign_service.get_campaign(db_session, 99999)
        assert result is None

    def test_update_campaign_success(self, db_session):
        """Test successful campaign update."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        update = CampaignUpdate(
            name="Updated Name",
            description="Updated description"
        )
        
        result = campaign_service.update_campaign(
            db_session, campaign.id, update, owner_id=user.id
        )
        
        assert result.name == "Updated Name"
        assert result.description == "Updated description"

    def test_update_campaign_partial_update(self, db_session):
        """Test that partial updates only change specified fields."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(
            db_session, user.id, name="Original", description="Original Desc"
        )
        
        # Only update name
        update = CampaignUpdate(name="New Name")
        result = campaign_service.update_campaign(
            db_session, campaign.id, update, owner_id=user.id
        )
        
        assert result.name == "New Name"
        assert result.description == "Original Desc"  # Unchanged

    def test_update_campaign_wrong_owner(self, db_session):
        """Test that non-owners cannot update campaigns."""
        owner = create_test_user(db_session, username="owner")
        other_user = create_test_user(db_session, username="other")
        campaign = create_test_campaign(db_session, owner.id)
        
        update = CampaignUpdate(name="Hacked Name")
        
        with pytest.raises(ValueError, match="not found or access denied"):
            campaign_service.update_campaign(
                db_session, campaign.id, update, owner_id=other_user.id
            )

    def test_update_campaign_not_found(self, db_session):
        """Test updating non-existent campaign."""
        user = create_test_user(db_session)
        update = CampaignUpdate(name="Test")
        
        with pytest.raises(ValueError, match="not found or access denied"):
            campaign_service.update_campaign(
                db_session, 99999, update, owner_id=user.id
            )

    def test_delete_campaign_success(self, db_session):
        """Test successful campaign deletion."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        campaign_id = campaign.id
        
        campaign_service.delete_campaign(
            db_session, campaign_id, owner_id=user.id
        )
        
        # Verify campaign is deleted
        from app.models import Campaign
        assert db_session.get(Campaign, campaign_id) is None

    def test_delete_campaign_cascades_to_game_state(self, db_session):
        """Test that deleting campaign cascades to game state."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        campaign_id = campaign.id
        
        campaign_service.delete_campaign(
            db_session, campaign_id, owner_id=user.id
        )
        
        # Verify game state is also deleted
        assert db_session.query(GameState).filter(
            GameState.campaign_id == campaign_id
        ).first() is None

    def test_delete_campaign_wrong_owner(self, db_session):
        """Test that non-owners cannot delete campaigns."""
        owner = create_test_user(db_session, username="owner")
        other_user = create_test_user(db_session, username="other")
        campaign = create_test_campaign(db_session, owner.id)
        
        with pytest.raises(ValueError, match="not found or access denied"):
            campaign_service.delete_campaign(
                db_session, campaign.id, owner_id=other_user.id
            )

    def test_delete_campaign_not_found(self, db_session):
        """Test deleting non-existent campaign."""
        user = create_test_user(db_session)
        
        with pytest.raises(ValueError, match="not found or access denied"):
            campaign_service.delete_campaign(
                db_session, 99999, owner_id=user.id
            )
