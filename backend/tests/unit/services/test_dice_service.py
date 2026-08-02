"""Unit tests for dice_service module."""

import pytest

from app.services import dice_service
from tests.fixtures.campaigns import create_test_campaign
from tests.fixtures.characters import create_test_character
from tests.fixtures.users import create_test_user


class TestDiceService:
    """Unit tests for dice_service functions."""

    def test_record_roll_success(self, db_session):
        """Test successful dice roll recording."""
        result = dice_service.record_roll(
            db_session,
            campaign_id=None,
            character_id=None,
            roller_type="player",
            expression="1d20+5",
            total=18,
            detail={"rolls": [13], "modifier": 5}
        )
        
        assert result.id > 0
        assert result.expression == "1d20+5"
        assert result.total == 18
        assert result.roller_type == "player"
        assert result.campaign_id is None
        assert result.character_id is None
        assert result.detail == {"rolls": [13], "modifier": 5}

    def test_record_roll_with_campaign(self, db_session):
        """Test recording roll linked to a campaign."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        
        result = dice_service.record_roll(
            db_session,
            campaign_id=campaign.id,
            character_id=None,
            roller_type="gm",
            expression="2d6",
            total=8,
            detail=None
        )
        
        assert result.campaign_id == campaign.id

    def test_record_roll_with_character(self, db_session):
        """Test recording roll linked to a character."""
        user = create_test_user(db_session)
        character = create_test_character(db_session, user.id)
        
        result = dice_service.record_roll(
            db_session,
            campaign_id=None,
            character_id=character.id,
            roller_type="player",
            expression="1d8+3",
            total=7,
            detail={}
        )
        
        assert result.character_id == character.id

    def test_record_roll_with_both_campaign_and_character(self, db_session):
        """Test recording roll linked to both campaign and character."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        character = create_test_character(db_session, user.id, campaign.id)
        
        result = dice_service.record_roll(
            db_session,
            campaign_id=campaign.id,
            character_id=character.id,
            roller_type="player",
            expression="1d20",
            total=15,
            detail=None
        )
        
        assert result.campaign_id == campaign.id
        assert result.character_id == character.id

    def test_list_rolls_all(self, db_session):
        """Test listing all rolls without filters."""
        # Create multiple rolls
        dice_service.record_roll(
            db_session, None, None, "player", "1d20", 10, None
        )
        dice_service.record_roll(
            db_session, None, None, "player", "1d6", 4, None
        )
        dice_service.record_roll(
            db_session, None, None, "gm", "2d10", 12, None
        )
        
        rolls = dice_service.list_rolls(db_session)
        
        assert len(rolls) == 3
        # Should be ordered by created_at desc (newest first)
        assert rolls[0].expression in ["2d10", "1d6", "1d20"]

    def test_list_rolls_with_campaign_filter(self, db_session):
        """Test listing rolls filtered by campaign."""
        user = create_test_user(db_session)
        campaign1 = create_test_campaign(db_session, user.id, name="Camp 1")
        campaign2 = create_test_campaign(db_session, user.id, name="Camp 2")
        
        dice_service.record_roll(
            db_session, campaign1.id, None, "player", "1d20", 15, None
        )
        dice_service.record_roll(
            db_session, campaign2.id, None, "player", "1d20", 12, None
        )
        dice_service.record_roll(
            db_session, None, None, "player", "1d20", 10, None
        )
        
        campaign1_rolls = dice_service.list_rolls(
            db_session, campaign_id=campaign1.id
        )
        
        assert len(campaign1_rolls) == 1
        assert campaign1_rolls[0].campaign_id == campaign1.id

    def test_list_rolls_with_character_filter(self, db_session):
        """Test listing rolls filtered by character."""
        user = create_test_user(db_session)
        char1 = create_test_character(db_session, user.id, name="Char 1")
        char2 = create_test_character(db_session, user.id, name="Char 2")
        
        dice_service.record_roll(
            db_session, None, char1.id, "player", "1d20", 18, None
        )
        dice_service.record_roll(
            db_session, None, char2.id, "player", "1d20", 16, None
        )
        dice_service.record_roll(
            db_session, None, None, "player", "1d20", 14, None
        )
        
        char1_rolls = dice_service.list_rolls(
            db_session, character_id=char1.id
        )
        
        assert len(char1_rolls) == 1
        assert char1_rolls[0].character_id == char1.id

    def test_list_rolls_with_both_filters(self, db_session):
        """Test listing rolls filtered by both campaign and character."""
        user = create_test_user(db_session)
        campaign = create_test_campaign(db_session, user.id)
        char1 = create_test_character(db_session, user.id, campaign.id, name="Char 1")
        char2 = create_test_character(db_session, user.id, campaign.id, name="Char 2")
        
        dice_service.record_roll(
            db_session, campaign.id, char1.id, "player", "1d20", 20, None
        )
        dice_service.record_roll(
            db_session, campaign.id, char2.id, "player", "1d20", 18, None
        )
        dice_service.record_roll(
            db_session, campaign.id, None, "gm", "1d20", 15, None
        )
        
        filtered_rolls = dice_service.list_rolls(
            db_session, campaign_id=campaign.id, character_id=char1.id
        )
        
        assert len(filtered_rolls) == 1
        assert filtered_rolls[0].character_id == char1.id
        assert filtered_rolls[0].campaign_id == campaign.id

    def test_list_rolls_with_limit(self, db_session):
        """Test that limit parameter works correctly."""
        # Create 10 rolls
        for i in range(10):
            dice_service.record_roll(
                db_session, None, None, "player", f"1d20", 10 + i, None
            )
        
        # Request only 5
        rolls = dice_service.list_rolls(db_session, limit=5)
        
        assert len(rolls) == 5

    def test_list_rolls_empty(self, db_session):
        """Test listing rolls when none exist."""
        rolls = dice_service.list_rolls(db_session)
        assert len(rolls) == 0

    def test_record_roll_stores_metadata(self, db_session):
        """Test that roll metadata is stored correctly."""
        detail = {
            "rolls": [5, 6, 4],
            "modifier": 3,
            "has_advantage": False,
            "is_critical": False
        }
        
        result = dice_service.record_roll(
            db_session,
            None,
            None,
            "player",
            "3d6+3",
            18,
            detail
        )
        
        assert result.detail == detail
        assert result.detail["rolls"] == [5, 6, 4]
        assert result.detail["modifier"] == 3
