"""Unit tests for game_state_service module."""

import pytest

from app.schemas.game_state import GameStateUpdate
from app.services import game_state_service
from tests.fixtures.campaigns import create_test_campaign
from tests.fixtures.users import create_test_user


class TestGameStateService:
    """Unit tests for game_state_service functions."""

    def test_get_game_state_success(self, db_session):
        """Test successful game state retrieval."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        result = game_state_service.get_game_state(db_session, campaign.id)
        
        assert result.campaign_id == campaign.id
        assert result.location is None
        assert result.active_quests == []
        assert result.summary is None
        assert result.metadata == {}

    def test_get_game_state_creates_if_missing(self, db_session):
        """Test that game state is created if it doesn't exist."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        # Delete the game state that was created with campaign
        from app.models import GameState
        db_session.query(GameState).filter(
            GameState.campaign_id == campaign.id
        ).delete()
        db_session.commit()
        
        # Get should create it
        result = game_state_service.get_game_state(db_session, campaign.id)
        
        assert result.campaign_id == campaign.id
        assert result.active_quests == []

    def test_get_game_state_campaign_not_found(self, db_session):
        """Test that getting game state for non-existent campaign raises error."""
        with pytest.raises(ValueError, match="Campaign not found"):
            game_state_service.get_game_state(db_session, 99999)

    def test_update_game_state_success(self, db_session):
        """Test successful game state update."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        update = GameStateUpdate(
            location="Phandalin",
            summary="Heroes arrive in town",
            active_quests=["Find Gundren", "Clear Cragmaw Hideout"]
        )
        
        result = game_state_service.update_game_state(
            db_session, campaign.id, update, owner_id=user.id
        )
        
        assert result.location == "Phandalin"
        assert result.summary == "Heroes arrive in town"
        assert result.active_quests == ["Find Gundren", "Clear Cragmaw Hideout"]

    def test_update_game_state_partial(self, db_session):
        """Test that partial updates only change specified fields."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        # Set initial state
        initial_update = GameStateUpdate(
            location="Town",
            summary="Initial summary",
            active_quests=["Quest 1"]
        )
        game_state_service.update_game_state(
            db_session, campaign.id, initial_update, owner_id=user.id
        )
        
        # Only update location
        update = GameStateUpdate(location="Dungeon")
        result = game_state_service.update_game_state(
            db_session, campaign.id, update, owner_id=user.id
        )
        
        assert result.location == "Dungeon"
        assert result.summary == "Initial summary"  # Unchanged
        assert result.active_quests == ["Quest 1"]  # Unchanged

    def test_update_game_state_metadata(self, db_session):
        """Test updating game state metadata."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        update = GameStateUpdate(
            metadata={"npc_met": ["Gundren", "Sildar"], "days_passed": 3}
        )
        
        result = game_state_service.update_game_state(
            db_session, campaign.id, update, owner_id=user.id
        )
        
        assert result.metadata == {"npc_met": ["Gundren", "Sildar"], "days_passed": 3}

    def test_update_game_state_wrong_owner(self, db_session):
        """Test that non-owners cannot update game state."""
        owner = create_test_user(db_session, username="owner")
        other_user = create_test_user(db_session, username="other")
        campaign = create_test_campaign(db_session, owner.id)
        
        update = GameStateUpdate(location="Hacked Location")
        
        with pytest.raises(ValueError, match="Campaign not found"):
            game_state_service.update_game_state(
                db_session, campaign.id, update, owner_id=other_user.id
            )

    def test_update_game_state_campaign_not_found(self, db_session):
        """Test updating game state for non-existent campaign."""
        user = create_test_user(db_session)
        update = GameStateUpdate(location="Test")
        
        with pytest.raises(ValueError, match="Campaign not found"):
            game_state_service.update_game_state(
                db_session, 99999, update, owner_id=user.id
            )

    def test_update_game_state_not_found(self, db_session):
        """Test updating game state that doesn't exist."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        # Delete the game state
        from app.models import GameState
        db_session.query(GameState).filter(
            GameState.campaign_id == campaign.id
        ).delete()
        db_session.commit()
        
        update = GameStateUpdate(location="Test")
        
        with pytest.raises(ValueError, match="Game state not found"):
            game_state_service.update_game_state(
                db_session, campaign.id, update, owner_id=user.id
            )

    def test_game_state_active_quests_empty_list(self, db_session):
        """Test that empty active_quests list is handled correctly."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        # Set quests
        update1 = GameStateUpdate(active_quests=["Quest 1", "Quest 2"])
        game_state_service.update_game_state(
            db_session, campaign.id, update1, owner_id=user.id
        )
        
        # Clear quests
        update2 = GameStateUpdate(active_quests=[])
        result = game_state_service.update_game_state(
            db_session, campaign.id, update2, owner_id=user.id
        )
        
        assert result.active_quests == []
